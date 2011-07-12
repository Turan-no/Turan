from celery.decorators import task
from celery.task.sets import subtask

from subprocess import call
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.core.cache import cache
from django.conf import settings
from django.db.models import get_model
from django.db import connection, transaction
from django.db.models import Avg, Max, Min, Count, Variance, StdDev, Sum
from django.utils.datastructures import SortedDict

from copy import deepcopy
import numpy
from collections import deque
from datetime import timedelta

from svg import GPX2SVG
from gpx2png import GPX2PNG
from gpxwriter import GPXWriter
from tcxwriter import TCXWriter
from gpxparser import GPXParser, proj_distance
from hrmparser import HRMParser
from gmdparser import GMDParser
from tcxparser import TCXParser
from csvparser import CSVParser
from pwxparser import PWXParser
from fitparser import FITParser
from polaronlineparser import POLParser
from suuntoxlsxparser import SuuntoXLSXParser


gpxstore = FileSystemStorage(location=settings.GPX_STORAGE)

def find_parser(filename):
    ''' Returns correctly initianted parser-class given a filename '''
    f_lower = filename.lower()

    if f_lower.endswith('.hrm'): # Polar !
        parser = HRMParser()
    elif f_lower.endswith('.gmd'): # garmin-tools-dump
        parser = GMDParser()
    elif f_lower.endswith('.tcx'): # garmin training centre
        parser = TCXParser(gps_distance=False) #should have menu on
                                               #upload page 
    elif f_lower.endswith('.csv'): # PowerTap
        parser = CSVParser()
    elif f_lower.endswith('.gpx'):
        parser = GPXParser()
    elif f_lower.endswith('.pwx'):
        parser = PWXParser()
    elif f_lower.endswith('.fit'):
        parser = FITParser()
    elif f_lower.endswith('.xml'): # Polar online
        parser = POLParser()
    elif filename.endswith('xlsx'): # Suunto Web export
        parser = SuuntoXLSXParser()
    else:
        raise Exception('Parser not found') # Maybe warn user somehow?
    return parser

def filldistance(values):
    ''' Helper to fill distance in a list of exercise details,
    needed until all parsers are fixed to export distance '''
    d = 0
    if values: #exists?
        d_check = values[len(values)-1].distance
        if d_check > 0:
            return d_check
        values[0].distance = 0
        for i in xrange(1, len(values)):
            delta_t = (values[i].time - values[i-1].time).seconds
            if values[i].speed:
                d += values[i].speed/3.6 * delta_t
                values[i].distance = d
            else:
                values[i].distance = values[i-1].distance
    return d

def getavghr(values, start, end):
    ''' Return average HR given values and start and end '''
    hr = 0
    for i in xrange(start+1, end+1):
        delta_t = (values[i].time - values[i-1].time).seconds
        if values[i].hr:
            hr += values[i].hr*delta_t
    delta_t = (values[end].time - values[start].time).seconds
    return float(hr)/delta_t


def getavgpwr(values, start, end):
    ''' Return average power given values and start and end '''
    pwr = 0
    for i in xrange(start+1, end+1):
        delta_t = (values[i].time - values[i-1].time).seconds
        try:
            pwr += values[i].power*delta_t
        except TypeError:
            return 0
    delta_t = (values[end].time - values[start].time).seconds
    return float(pwr)/delta_t

def calcpower(userweight, eqweight, gradient, speed,
        rollingresistance = 0.006 ,
        airdensity = 1.22 ,
        frontarea = 0.7 ):
    if not userweight: # Do not even bother
        return 0
    tot_weight = userweight+eqweight
    gforce = tot_weight * gradient/100 * 9.81
    frictionforce = rollingresistance * tot_weight * 9.81
    windforce = 0.5**2 * speed**2  * airdensity * frontarea
    return (gforce + frictionforce + windforce)*speed

@task
def getslopes(values, userweight, eqweight):
    ''' Given values and weight at the time of exercise, find
    and calculate stats for slopes in exercise and save to db, returning
    the slopes found. Deletes any existing slopes for exercise '''
    Slope = get_model('turan', 'Slope')

    # Make sure we don't create duplicate slopes
    values[0].exercise.slope_set.all().delete()

    # Make sure exercise type is cycling, this only makes sense for cycling
    exercise_type = values[0].exercise.exercise_type
    if not str(exercise_type) == 'Cycling':
        return []
    if not filldistance(values):
        return []

    slopes = []
    min_slope = 40
    cur_start = 0
    cur_end = 0
    stop_since = False
    inslope = False
    for i in xrange(1, len(values)):
        if values[i].speed < 0.05 and not stop_since:
            stop_since = i
        if values[i].speed >= 0.05:
            stop_since = False
        if inslope:
            if values[i].altitude > values[cur_end].altitude:
                cur_end = i
            hdelta = values[cur_end].altitude - values[cur_start].altitude
            if stop_since:
                stop_duration = (values[i].time - values[stop_since].time).seconds
            else:
                stop_duration = 0
            try:
                if (values[i+1].time - values[i].time).seconds > 60:
                    stop_duration = max( \
                            (values[i+1].time - values[i].time).seconds, \
                            stop_duration )
            except IndexError:
                pass
            if values[i].altitude < values[cur_start].altitude + hdelta*0.9 \
                    or i == len(values)-1 \
                    or stop_duration > 60:
                if stop_duration > 60:
                    cur_end = stop_since
                inslope = False
                if hdelta >= min_slope:
                    distance = values[cur_end].distance - values[cur_start].distance
                    if distance > 10:
                        slope = Slope(exercise=values[cur_start].exercise,
                                    start=values[cur_start].distance/1000,
                                    length = distance,
                                    ascent = hdelta,
                                    grade = hdelta/distance * 100)
                        slope.duration = (values[cur_end].time - values[cur_start].time).seconds
                        slope.speed = slope.length/slope.duration * 3.6
                        slope.avg_hr = getavghr(values, cur_start, cur_end)
                        slope.est_power = calcpower(userweight, eqweight, slope.grade, slope.speed/3.6)
                        slope.act_power = getavgpwr(values, cur_start, cur_end)

                        slope.start_lat = values[cur_start].lat
                        slope.start_lon = values[cur_start].lon
                        slope.end_lat = values[cur_end].lat
                        slope.end_lon = values[cur_end].lon

                        # Sanity check
                        if not slope.grade > 100:
                            slope.save()
                            slopes.append(slope)
                cur_start = i+1
        elif values[i].altitude <= values[cur_start].altitude:
            cur_start = i
            cur_end  = i
        elif values[i].altitude > values[cur_start].altitude:
            cur_end = i
            inslope = True
    return slopes

def match_slopes(se, offset=70):
    Slope = get_model('turan', 'Slope')
    slopes = Slope.objects.filter(start_lon__gt=0)
    for s in slopes:
        start_distance = proj_distance(se.start_lat, se.start_lon, s.start_lat, s.start_lon)
        if start_distance and start_distance < offset:
            end_distance = proj_distance(se.end_lat, se.end_lon, s.end_lat, s.end_lon)
            if end_distance and end_distance < offset:
                print start_distance, end_distance
                if not s.segment:
                    s.segment = se
                    s.save()

def slice_to_segmentdetail(exercise, segment, start, stop):
    SegmentDetail = get_model('turan', 'SegmentDetail')
    ret = detailslice_info(exercise.get_details().all()[start:stop+1])
    data = {}
    data['exercise'] = exercise
    data['start'] = ret['start']
    data['length'] = ret['distance']
    data['ascent'] = int(ret['ascent'])
    data['grade'] = ret['gradient']
    data['duration'] = ret['duration']
    data['speed'] = ret['speed__avg']
    data['est_power'] = ret['power__avg_est']
    data['act_power'] = ret['power__avg']
    data['vam'] = ret['vam']
    data['avg_hr'] = ret['hr__avg']
    data['start_lon'] = ret['start_lon']
    data['start_lat'] = ret['start_lat']
    data['end_lon'] = ret['end_lon']
    data['end_lat'] = ret['end_lat']
    if 'power_per_kg' in ret:
        data['power_per_kg'] = ret['power_per_kg']
    data['segment'] = segment
    #data['comment'] = 'Auto'
    new_object = SegmentDetail(**data)
    new_object.save()

def search_trip_for_possible_segments_matches(exercise, start_offset=30, end_offset=90, dupedistance=200, search_in_segments=None):
    ''' For every segment
            iterate every detail searching for pos matching the start pos
            then find match for end pos if distance elapsed doesn't exceed segment distance
                finally save the segment found if start and stop pos found '''
    Segment = get_model('turan', 'Segment')

    if not search_in_segments:
        search_in_segments = Segment.objects.all()
    # Only works for exercises with distance
    details = exercise.get_details().filter(lon__gt=0).filter(lat__gt=0).filter(distance__gt=0).values('distance', 'lon', 'lat')
    i_len = len(details)
    segments = [] #'[(segment, start, stop)...'
    #old_segmentdetails = exercise.segmentdetail_set.all()
    for se in search_in_segments:
        previous_start = 0
        started_at_distance = 0
        found_start = -1
        previous_end = 0
        found_end = 0
        for i, d in enumerate(details):
            if found_start < 0:
                start_distance = proj_distance(se.start_lat, se.start_lon, d['lat'], d['lon'])
                if start_distance < start_offset:
                    print i, start_distance
                    if previous_start:
                        if start_distance > previous_start:
                            found_start = i-1
                            started_at_distance = d['distance']
                            print "Start of %s at index %s" %(se, found_start)
                    previous_start = start_distance
                elif start_distance > 300000: # If start distance is further away than 300km we stop searching
                    print "Skipped segment, start was %s m away" %start_distance
                    print "Decimal distance was: %s" %(d['lat'] - se.start_lat)
                    break
            elif not found_end:
                end_distance = proj_distance(se.end_lat, se.end_lon, d['lat'], d['lon'])
                #Check if distance from start is longer than segment plus some, means we didnt' find stop
                search_distance = se.distance*1000 + 1000 + end_offset*2
                found_distance = d['distance'] - started_at_distance
                if found_distance > search_distance:
                    print started_at_distance, d['distance'], search_distance
                    print "Didn't find end, resetting state"
                    # reset start
                    found_start, found_end, previous_start, started_at_distance, previous_end = -1, 0, 0, 0, 0
                    continue
                if end_distance < end_offset: # We are closing in on end
                    print i, end_distance
                    if end_distance == 0.0: # Found exact match
                        found_end = i
                        print "End of %s at index %s" %(se, found_end)
                    elif previous_end:
                        if end_distance > previous_end:
                            found_end = i-1 # subtract, indexed used in list slice later
                            print "End of %s at index %s" %(se, found_end)
                    previous_end = end_distance
                    if i_len-1 == i: # We reached end of details, but we are withing segment
                        found_end = i
                        print "End of %s at index %s" %(se, found_end)
            if found_start>=0 and found_end:
                print "_________Found Segment %s" %se

                # Iterate over the existing segments for this exercise
                # Do not add the found segment if it's too close to existing
                # If the start is within dupedistance=300 meters, and the length is within 
                # we deem it coo close
                duplicate = False
                for old_segment in exercise.segmentdetail_set.all():
                    if (-dupedistance < (old_segment.start*1000-started_at_distance) < dupedistance and
                        -dupedistance < (old_segment.length-found_distance) < dupedistance):
                        # If distance of found segment is within 500 meters of
                        # the lenght of the segment we accept it
                        print "_____ Duplicate found, skipping"
                        print "Found start: %s, Old Segment Start: %s" %(started_at_distance, old_segment.start*1000)
                        print "Found distance: %s, Old Segment distance: %s" %(found_distance, old_segment.length)
                        duplicate = True
                        break
                if -500 < found_distance-se.distance*1000 < 500 and not duplicate:
                    segments.append((se, found_start, found_end, started_at_distance, found_distance))
                found_start, found_end, previous_start, started_at_distance, previous_end = -1, 0, 0, 0, 0

    return segments

@task
def create_simplified_gpx(gpx_path, filename):
    cmd = 'gpsbabel -i gpx -f %s -x duplicate,location -x position,distance=1m -x simplify,crosstrack,error=0.005k -o gpx -F %s' % (\
            gpx_path,
            '/'.join(gpx_path.split('/')[0:-2]) + '/' + filename)
    retcode = call(cmd.split())
    return retcode

@task
def create_png_from_gpx(gpx_path, filename):
    png = GPX2PNG(gpx_path)
    f = png.get_file()
    gpxstore.save(filename, ContentFile(f.read()))
    return True

@task
def create_svg_from_gpx(gpx_path, filename):
    g = GPX2SVG(gpx_path)
    svg = g.xml
    gpxstore.save(filename, ContentFile(svg))
    return True

@task
def create_gpx_from_details(exercise, callback=None):
#    logger = create_gpx_from_details.get_logger()
#    logger.info('create_gpx_from_details: %s' %exercise.id)

    if exercise.route:
        # Check if the route has .gpx or not.
        # Since we at this point have exercise details
        # we can generate gpx based on that
        if not exercise.route.gpx_file:

            # Check if the details have lon, some parsers doesn't provide position
            if exercise.get_details().filter(lon__gt=0).count() > 0 or exercise.get_details().filter(lon__lt=0).count():
                g = GPXWriter(exercise.get_details().all())
                filename = 'gpx/%s.gpx' %exercise.id

                # tie the created file to the route object
                # also call Save on route to generate start/stop-pos, etc
                exercise.route.gpx_file.save(filename, ContentFile(g.xml), save=True)

                # Save the Route (because of triggers for pos setting and such)
                exercise.route.save()

    if not callback is None:
        subtask(callback).delay(exercise)
#    calculate_best_efforts.delay(exercise)

@task
def merge_sensordata(exercise, callback=None):

    ExerciseDetail = get_model('turan', 'ExerciseDetail')

    for merger in exercise.mergesensorfile_set.all():

        # TODO, merge_types, this is only the merge kind.

        merger.sensor_file.file.seek(0)
        parser = find_parser(merger.sensor_file.name)
        parser.parse_uploaded_file(merger.sensor_file.file)
        for val in parser.entries:
            # Lookup correct detail based on time TODO: more merge strategies
            try:
                ed = ExerciseDetail.objects.get(exercise=exercise, time=val.time)
                for v in ('hr', 'altitude', 'speed', 'cadence', 'position'):
                    want_value = getattr(merger, v)
                    if want_value:
                        if v == 'position':
                            ed.lat = val.lat
                            ed.lon = val.lon
                        else:
                            setattr(ed, v, getattr(val, v))
                ed.save()
            except Exception:
                print "No match: %s" % val.time
                # Did not find match, continue
    if not callback is None:
        subtask(callback).delay(exercise)
#    create_gpx_from_details.delay(exercise)

def smoothListGaussian(list, degree=5):
    list = [x if x else 0 for x in list] # Change None into 0
    if not list:
        return list
    list = [list[0]]*(degree-1) + list + [list[-1]]*degree
    window = degree*2-1
    weight = numpy.array([1.0]*window)
    weightGauss = []
    for i in range(window):
        i = i-degree+1
        frac = i/float(window)
        gauss = 1/(numpy.exp((4*(frac))**2))
        weightGauss.append(gauss)
    weight = numpy.array(weightGauss)*weight
    smoothed = [0.0]*(len(list)-window)
    for i in range(len(smoothed)):
        smoothed[i] = sum(numpy.array(list[i:i+window])*weight)/sum(weight)
    return smoothed

def calculate_ascent_descent_gaussian(details, degree=5):
    ''' Calculate ascent and descent for an exercise. Use guassian filter to smooth '''

    altvals = []
    for a in details:
        altvals.append(a.altitude)

    altvals = smoothListGaussian(altvals, degree)
    return altvals_to_ascent_descent(altvals)

def altvals_to_ascent_descent(altvals):

    ascent = 0
    descent = 0
    previous = -1

    for a in altvals:
        if previous == -1:
            previous = a

        if a > previous:
            ascent += (a - previous)
        elif a < previous:
            descent += (previous - a)

        previous = a
    return round(ascent), round(descent)

def best_x_sec(details, length, altvals, speed=True, power=False):

    best_speed = 0.0
    best_power = 0.0
    best_power = 0.0
    sum_q_power = 0.0
    sum_q_speed = 0.0
    best_start_km_speed = 0.0
    best_start_km_power = 0.0
    best_speed_start_end = 0
    best_power_start_end = 0
    q_speed = deque()
    q_power = deque()
    best_length_speed = 0.0
    best_length_power = 0.0

    if speed:
        q_speed.appendleft(details[0].speed)
    j = 1
    if power and details[j].power:
        q_power.appendleft(details[j].power)
    j = 2
    len_i = len(details)
    for i in xrange(2, len_i):
        #try:
        delta_t = (details[i].time - details[i-1].time).seconds
        if speed:
            # Break if exerciser is on a break as well
            if delta_t < 60:
                q_speed.appendleft(details[i].speed * delta_t)
            else:
                q_speed = deque()
                q_speed.appendleft(details[i].speed)
            delta_t_total = (details[i].time - details[i-len(q_speed)].time).seconds
        if power:
            if delta_t < 60 and details[i].power:
                q_power.appendleft(details[i].power * delta_t)
            elif delta_t < 60 and not details[i].power:
                q_power.appendleft(0)
            else:
                q_power = deque()
                if details[i].power:
                    q_power.appendleft(details[i].power)
            if not speed:
                delta_t_total = (details[i].time - details[i-len(q_power)].time).seconds
        if delta_t_total >= length:
            break
        j += 1
        #except Exception as e:
        #    #print "%s %s %s %s %s" % (e, i, j, delta_t, len(q_speed))
        #    #j += 1
        #    continue
    j += 1

    for i in xrange(j, len(details)):

        try:
            if len(q_speed):
                if speed:
                    sum_q_speed_tmp = sum(q_speed)
                    delta_t_total = (details[i].time - details[i-len(q_speed)].time).seconds

                    if delta_t_total != 0 and delta_t_total == length:
                        sum_q_speed = sum_q_speed_tmp / (details[i].time - details[i-len(q_speed)].time).seconds
                    else:
                        # What can one do?
                        sum_q_speed = 0
            if len(q_power):
                if power:
                    sum_q_power_tmp = sum(q_power)
                    delta_t_total_power = (details[i].time - details[i-len(q_power)].time).seconds
                    if delta_t_total_power != 0 and delta_t_total_power == length:
                        sum_q_power = sum_q_power_tmp / delta_t_total_power
                    else:
                        sum_q_power = 0
            if sum_q_speed > best_speed:
                best_speed = sum_q_speed
                best_start_km_speed = details[i-len(q_speed)].distance / 1000
                best_speed_start_end = (i, i-len(q_speed))
                best_length_speed = (details[i].distance) - best_start_km_speed * 1000
            if sum_q_power > best_power:
                best_power = sum_q_power
                best_start_km_power = details[i-len(q_power)].distance / 1000
                best_power_start_end = (i, i-len(q_speed))
                best_length_power = (details[i].distance) - best_start_km_power * 1000

            delta_t = (details[i].time - details[i-1].time).seconds
            if speed:
                if delta_t < 60:
                    q_speed.appendleft(details[i].speed*delta_t)
                else:
                    q_speed = deque()
            if power:
                if delta_t < 60 and details[i].power:
                    q_power.appendleft(details[i].power*delta_t)
                elif delta_t < 60 and not details[i].power:
                    q_power.appendleft(0)
                else:
                    q_power = deque()
            while ((details[i].time - details[i-len(q_speed)].time).seconds) > length:
                q_speed.pop()
            while (power and (details[i].time - details[i-len(q_power)].time).seconds > length):
                q_power.pop()
        except Exception as e:
            print "something wrong %s, %s, %s, %s" % (e, len(q_speed), i, j)
            #raise
            continue

    if power and speed:
        best_speed_ascent = 0
        best_speed_descent = 0
        best_power_ascent = 0
        best_power_descent = 0
        if best_speed_start_end:
            c, d = best_speed_start_end
            best_speed_ascent, best_speed_descent = altvals_to_ascent_descent(altvals[d:c])
        if best_power_start_end:
            a, b = best_power_start_end
            best_power_ascent, best_power_descent = altvals_to_ascent_descent(altvals[b:a])

        return best_speed, best_start_km_speed, best_length_speed, best_speed_ascent, best_speed_descent, best_power, best_start_km_power, best_length_power, best_power_ascent, best_power_descent
    elif speed and not power:
        best_speed_ascent = 0
        best_speed_descent = 0
        if best_speed_start_end:
            a, b = best_speed_start_end
            best_speed_ascent, best_speed_descent = altvals_to_ascent_descent(altvals[b:a])
        return best_speed, best_start_km_speed, best_length_speed, best_speed_ascent, best_speed_descent
    elif power and not speed:
        best_power_ascent = 0
        best_power_descent = 0
        if best_power_start_end:
            a, b = best_power_start_end
            best_power_ascent, best_power_descent = altvals_to_ascent_descent(altvals[b:a])

        return best_power, best_start_km_power, best_length_power, best_power_ascent, best_power_descent

@task
def calculate_time_in_zones(exercise, callback=None):

    # First: Delete any existing in case of reparse
    exercise.hrzonesummary_set.all().delete()
    exercise.wzonesummary_set.all().delete()

    HRZoneSummary = get_model('turan', 'HRZoneSummary')
    WZoneSummary = get_model('turan', 'WZoneSummary')

    zones = getzones(exercise)
    for zone, val in zones.items():
        hrz = HRZoneSummary()
        hrz.exercise_id = exercise.id
        hrz.zone = zone
        hrz.duration = val
        hrz.save()
    wzones = getwzones(exercise)
    for zone, val in wzones.items():
        wz = WZoneSummary()
        wz.exercise_id = exercise.id
        wz.zone = zone
        wz.duration = val
        wz.save()

def getzones(exercise):
    ''' Calculate time in different sport zones given trip details '''

    values = exercise.get_details().all()
    max_hr = exercise.user.get_profile().max_hr
    if not max_hr:
        max_hr = 200 # FIXME warning to user etc

    zones = SortedDict({
            0: 0,
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            6: 0,
        })
    previous_time = False
    if values:
        for d in values:
            if not previous_time:
                previous_time = d.time
                continue
            time = d.time - previous_time
            previous_time = d.time
            if time.seconds > 60:
                continue
            hr_percent = 0
            if d.hr:
                hr_percent = float(d.hr)*100/max_hr
            zone = hr2zone(hr_percent)
            zones[zone] += time.seconds
    else:
        if exercise.duration:
            zones[0] = exercise.duration.total_seconds()

    return zones

def getwzones(exercise):
    ''' Get time in watt zones '''

    values = exercise.get_details().all()
    # Check for FTP, can't calculate zones if not
    userftp = exercise.user.get_profile().get_ftp(exercise.date)
    if not userftp:
        return {}
    # Check object for watt
    if not exercise.avg_power:
        return {}

    zones = SortedDict({
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            6: 0,
            7: 0,
        })
    previous_time = False
    for d in values:
        if not previous_time:
            previous_time = d.time
            continue
        time = d.time - previous_time
        previous_time = d.time
        if time.seconds > 60:
            continue
        w_percent = 0
        if d.power:
            w_percent = float(d.power)*100/userftp
        zone = watt2zone(w_percent)
        zones[zone] += time.seconds
    return zones

@task
def calculate_best_efforts(exercise, effort_range=[5, 10, 30, 60, 240, 300, 600, 1200, 1800, 3600], calc_only_power=False, callback=None):
    ''' Iterate over details for different effort ranges finding best
    speed and power efforts '''

    # First: Delete any existing best efforts
    if not calc_only_power:
        exercise.bestspeedeffort_set.all().delete()
    exercise.bestpowereffort_set.all().delete()
    BestSpeedEffort = get_model('turan', 'BestSpeedEffort')
    BestPowerEffort = get_model('turan', 'BestPowerEffort')

    details = exercise.get_details().all()
    calc_power = exercise.avg_power and not exercise.is_smart_sampled()

    if details:
        if filldistance(details):
            altvals = []
            for a in details:
                altvals.append(a.altitude)

            altvals = smoothListGaussian(altvals)
            for seconds in effort_range:
                if calc_power and not calc_only_power:
                    speed, pos, length, speed_ascent, speed_descent, power, power_pos, power_length, power_ascent, power_descent = best_x_sec(details, seconds, altvals, power=True)
                    if power:
                        be = BestPowerEffort(exercise=exercise, power=power, pos=power_pos, length=power_length, duration=seconds, ascent=power_ascent, descent=power_descent)
                        be.save()
                    if speed:
                        be = BestSpeedEffort(exercise=exercise, speed=speed, pos=pos, length=length, duration=seconds, ascent=speed_ascent, descent=speed_descent)
                        be.save()
                elif not calc_power:
                    speed, pos, length, speed_ascent, speed_descent = best_x_sec(details, seconds, altvals, power=False)
                    if speed:
                        be = BestSpeedEffort(exercise=exercise, speed=speed, pos=pos, length=length, duration=seconds, ascent=speed_ascent, descent=speed_descent)
                        be.save()
                elif calc_power and calc_only_power:
                    power, power_pos, power_length, power_ascent, power_descent = best_x_sec(details, seconds, altvals, power=True, speed=False)
                    if power:
                        be = BestPowerEffort(exercise=exercise, power=power, pos=power_pos, length=power_length, duration=seconds, ascent=power_ascent, descent=power_descent)
                        be.save()
    if not callback is None:
        subtask(callback).delay(exercise)

def normalize_altitude(exercise):
    ''' Normalize altitude, that is, if it's below zero scale every value up.
    Also set max and min altitude on route'''

    altitude_min = exercise.get_details().aggregate(Min('altitude'))['altitude__min']
    altitude_max = exercise.get_details().aggregate(Max('altitude'))['altitude__max']
    # Normalize values
    if altitude_min and altitude_min < 0:
        altitude_min = 0 - altitude_min
        previous_altitude = 0
        for d in exercise.get_details().all():
            if d.altitude == None: # Check for missing altitude values
                d.altitude = previous_altitude
            else:
                d.altitude += altitude_min
            d.save()
            previous_altitude = d.altitude
    # Find min and max and populate route object
    # reget new values after normalize
    altitude_min = exercise.get_details().aggregate(Min('altitude'))['altitude__min']
    altitude_max = exercise.get_details().aggregate(Max('altitude'))['altitude__max']
    r = exercise.route
    if r:
        if not r.min_altitude:
            r.min_altitude = altitude_min
        if not r.max_altitude:
            r.max_altitude = altitude_max
        r.save()

def sanitize_entries(parser):
    ''' Try and sanitize and work around different quirks in different parsers
    '''

    entries = parser.entries

    def distance_offset_fixer(entries):
        ''' Some parsers return non-zero distance for the first sample
         We make assumption that the user wants his trip to show as starting at 0 km
         The cause of this can be tcx-files that have laps cut out'''
        distance_offset = 0

        if hasattr(entries[0], 'distance'):
            if entries[0].distance > 100: # We don't care about small values
                distance_offset = entries[0].distance
                print "Parser: Offset distance: %s" %distance_offset
                for e in entries:
                    if e.distance != None:
                        e.distance -= distance_offset
        return entries

    def distance_inc_fixer(entries):
        ''' Do not accept distances that do not increase '''

        prev = entries[0].distance
        for index, e in enumerate(entries):
            if e.distance == None or e.distance < prev:
                print "Parser: Changed fucked distance: %s at index %s" %(e.distance, index)
                e.distance = prev
                e.speed = 0
            prev = e.distance
        return entries

    def none_to_prev_val(entries, val):
        ''' Do not accept None-sample, use previous value  '''

        prev = entries[0]
        for index, e in enumerate(entries):
            if getattr(e, val) == None:
                print "Parser: Changed %s: %s at index %s" %(val, getattr(e, val), index)
                setattr(e, val, getattr(prev, val))
            prev = e
        return entries


    def interpolate_to_1s(entries):
        ''' Interpolate skips in files to 1s, if not breaks for over 30s in series '''

        val_types = ('distance', 'hr', 'altitude', 'speed', 'cadence', 'lon', 'lat', 'power', 'temp')

        missed = 0
        missed_seconds = 0
        prev = entries[0]
        prevIndex = 0
        for index, e in enumerate(entries):
            time_d = (e.time - prev.time).seconds
            if time_d > 1 and time_d < 30: # more than 30s is break, deal with it
                missed += 1
                missed_seconds += time_d
                deltas = {}
                for vt in val_types:
                    if hasattr(e, vt) and getattr(e, vt) and getattr(prev, vt): #could be none
                        deltas[vt] = (getattr(e, vt) - getattr(prev, vt)) / time_d
                for s in xrange(1, time_d):
                    fake_entry = deepcopy(prev)
                    fake_entry.time = fake_entry.time + timedelta(0, s)
                    for vt in val_types:
                        if vt == 'lon' or vt == 'lat':  # Do not interpolate between missed samples
                            if not fake_entry.lon or not fake_entry.lat:
                                continue
                        if hasattr(fake_entry, vt) and vt in deltas:
                            newattr = getattr(prev, vt) + deltas[vt]*s
                            setattr(fake_entry, vt, newattr)

                    entries.insert(prevIndex+s, fake_entry)

            prevIndex = index
            prev = e

        if missed:
            print "Parser: Missed samples: %s, Missed seconds: %s" %(missed, missed_seconds)
        return entries

    def gps_lost_fixer(entries):
        ''' Do not export entries with lon,lat == 0'''
        prev = entries[0]
        prevIndex = 0
        missed = 0
        for index, e in enumerate(entries):
            if not e.lon or not e.lat:
                e.lon = prev.lon
                e.lat = prev.lat
                missed += 1
            prevIndex = index
            prev = e

        if missed:
            print "Parser: Samples with missing pos: %s" %(missed)
        return entries

    def power_spikes_fixer(entries):
        ''' Remove insane power spikes from entries '''
        fixed_any = False
        for index, e in enumerate(entries):
            if hasattr(e, 'power') and e.power > 3000: # Get real!
                e.power = 0
                fixed_any = True
                print "Parser: Skipped insane power value  %s at index %s" %(e.power, index)
        if fixed_any: # We fixed a spike, this means avg power and max power might be wrong
                      # So we try and recalculate
            prev = entries[0]
            parser.max_power = 0
            parser.avg_power = 0
            parser.avg_pedaling_power = 0
            powersum = 0
            powerseconds = 0
            for index, e in enumerate(entries):
                parser.max_power = max(e.power, parser.max_power)
                parser.avg_power += e.power
                time_d = (e.time - prev.time).seconds
                if time_d > 0 and time_d < 30: # more than 30s is break
                    if e.power != None and e.cadence != None:
                        powersum += e.power*time_d
                        powerseconds += time_d
                if powersum and powerseconds:
                    parser.avg_pedaling_power = powersum/powerseconds
                prev = e

            parser.avg_power = parser.avg_power/len(entries)
        return entries

    def duplicate_samples_fixer(entries):
        ''' Remove duplicate time sample TODO: merge the sample values '''


        prev = False
        for e in entries:
            if prev:
                time_d = (e.time - prev.time).seconds
                if time_d < 1:
                    print "Parser: Removing duplicate sample %s at %s" %(e, e.time)
                    del e
                    continue
            prev = e
        return entries


    distance_offset_fixer(entries)
    distance_inc_fixer(entries)
    none_to_prev_val(entries, 'altitude')
    none_to_prev_val(entries, 'hr')
    gps_lost_fixer(entries)
    interpolate_to_1s(entries)
    power_spikes_fixer(entries)
    duplicate_samples_fixer(entries)
    return entries # Not really used.

@task
def parse_sensordata(exercise, callback=None):
    ''' The function that takes care of parsing data file from sports equipment from polar or garmin and putting values into the detail-db, and also summarized values for trip. '''


    # TODO change into proper logging
    print "Parsing Exercise: %s, with file: %s" %(exercise.id, exercise.sensor_file)

    ExerciseDetail = get_model('turan', 'ExerciseDetail')
    Interval = get_model('turan', 'Interval')

    # Delete any existing Intervals
    exercise.interval_set.all().delete()


    if exercise.get_details().count(): # If the exercise already has details, delete them and reparse
        # Django is super shitty when it comes to deleation. If you want to delete 25k objects, it uses 500 queries to do so.
        # So. We do some RAWness.
        cursor = connection.cursor()

        # Data modifying operation - commit required
        cursor.execute("DELETE FROM turan_exercisedetail WHERE exercise_id = %s", [exercise.id])
        transaction.commit_unless_managed()

    if exercise.slope_set.count(): # If the exercise has slopes, delete them too
        exercise.slope_set.all().delete()


    # Delete cache
    # TODO: Fix better cache key stuffs
    cache_keys = (
            'json_trip_series_%s_%dtime_xaxis_%dpower_%dsmooth' %(exercise.id, 0, 0, 1),
            'json_trip_series_%s_%dtime_xaxis_%dpower_%dsmooth' %(exercise.id, 1, 0, 1),
            'json_trip_series_%s_%dtime_xaxis_%dpower_%dsmooth' %(exercise.id, 0, 0, 0),
            'json_trip_series_%s_%dtime_xaxis_%dpower_%dsmooth' %(exercise.id, 1, 0, 0)
            )
    cache.delete_many(cache_keys)


    exercise.sensor_file.file.seek(0)
    parser = find_parser(exercise.sensor_file.name)
    parser.parse_uploaded_file(exercise.sensor_file.file)


    sanitize_entries(parser) # Sanity will prevail
    for val in parser.entries:
        detail = ExerciseDetail()
        detail.exercise_id = exercise.id
        # Figure out which values the parser has
        for v in ('distance', 'time', 'hr', 'altitude', 'speed', 'cadence', 'lon', 'lat', 'power', 'temp'):
            if hasattr(val, v):
                setattr(detail, v, getattr(val, v))
        detail.save()

    # Parse laps/intervals
    for val in parser.laps:
        interval = Interval()
        interval.exercise_id = exercise.id

        # Figure out which values the parser has
        for v in ('start', 'start_time', 'duration', 'distance', 'ascent', 'descent',
                'avg_temp', 'kcal', 'start_lat', 'start_lon', 'end_lat', 'end_lon',
                'avg_hr', 'avg_speed', 'avg_cadence', 'avg_power',
                'max_hr', 'max_speed', 'max_cadence', 'max_power',
                'min_hr', 'min_speed', 'min_cadence', 'min_power',
           ):
            if hasattr(val, v):
                setattr(interval, v, getattr(val, v))
        #try:
        interval.save()
        #except:
        #    pass

    exercise.max_hr = parser.max_hr
    exercise.max_speed = parser.max_speed
    exercise.max_cadence = parser.max_cadence
    if hasattr(parser, 'avg_hr'):
        exercise.avg_hr = parser.avg_hr
    exercise.avg_speed = parser.avg_speed
    if hasattr(parser, 'avg_cadence'):
        exercise.avg_cadence = parser.avg_cadence
    if hasattr(parser, 'avg_pedaling_cad'):
        exercise.avg_pedaling_cad = parser.avg_pedaling_cad
    if hasattr(parser, 'duration'):
        exercise.duration = parser.duration

    if parser.kcal_sum: # only some parsers provide kcal
        exercise.kcal = parser.kcal_sum

    if hasattr(parser, 'avg_power'): # only some parsers
        exercise.avg_power = parser.avg_power
        # Generate normalized power
        exercise.normalized_power = power_30s_average(exercise.get_details().all())
    if hasattr(parser, 'max_power'): # only some parsers
        exercise.max_power = parser.max_power
    if hasattr(parser, 'avg_pedaling_power'):
        exercise.avg_pedaling_power = parser.avg_pedaling_power


    if hasattr(parser, 'start_time'):
        if parser.start_time:
            exercise.time = parser.start_time

    if hasattr(parser, 'date'):
        if parser.date:
            exercise.date = parser.date

    if hasattr(parser, 'temperature'):
        if parser.temperature:
            exercise.temperature = parser.temperature

    if hasattr(parser, 'min_temp'):
        if parser.min_temp:
            exercise.min_temperature = parser.min_temp

    if hasattr(parser, 'max_temp'):
        if parser.max_temp:
            exercise.max_temperature = parser.max_temp

    if hasattr(parser, 'comment'): # Polar has this
        if parser.comment: # comment isn't always set
            exercise.comment = parser.comment



    # Normalize altitude, that is, if it's below zero scale every value up
    normalize_altitude(exercise)


    # Calculate normalized hr
    exercise.normalized_hr = normalized_attr(exercise, 'hr')

    # Auto calculate total ascent and descent
    route = exercise.route
    if route:
        if route.distance:
            # Sum is in meter, but routes like km.
            # use the distance from sensor instead of gps
            if parser.distance_sum and parser.distance_sum/1000 != route.distance:
                route.distance = parser.distance_sum/1000
                route.save()
        elif parser.distance_sum:
            route.distance = parser.distance_sum/1000
            route.save()

        if route.distance:
            ascent, descent = calculate_ascent_descent_gaussian(exercise.get_details().all())
        else:
            ascent = 0
            descent = 0
        # prefer ascent/descent calculated from sensor data over gps
        if route.ascent == 0 or route.descent == 0 \
                or not route.ascent or not route.descent \
                or route.descent != descent or route.ascent != ascent:
            route.ascent = ascent
            route.descent = descent
            route.save()

    # Somebadyyy saaaaaaave meee
    exercise.save()

    if not callback is None:
        subtask(callback).delay(exercise)

    # Apply jobs, so we can use this in view
    merge_sensordata(exercise)
    create_gpx_from_details(exercise)
    calculate_best_efforts(exercise)
    calculate_time_in_zones(exercise)
    if hasattr(route, 'ascent') and route.ascent > 0:
        getslopes(exercise.get_details().all(), exercise.user.get_profile().get_weight(exercise.date), exercise.get_eq_weight())
    populate_interval_info(exercise)
    for segment in search_trip_for_possible_segments_matches(exercise):
        slice_to_segmentdetail(exercise, segment[0], segment[1], segment[2])
        # TODO: send notifications notification.send(friend_set_for(request.user.id), 'exercise_create', {'sender': request.user, 'exercise': new_object}, [request.user])



@task
def populate_interval_info(exercise):
    #if exercise.sensor_file.name.endswith('.fit'):
        #"FIT. SO PRO"
    #    return
    details = list(exercise.exercisedetail_set.all())
    d = filldistance(details) # FIXME
    for interval in exercise.interval_set.all():
        start = 0 #= exercise.exercisedetail_set.get(time=interval.start_time)
        stop = 0 # exercise.exercisedetail_set.get(time=interval.start_time+interval.duration)
        stop_time = interval.start_time + timedelta(0, interval.duration)
        for i, ed in enumerate(details):
            if not start:
                if ed.time >= interval.start_time:
                    start = i
            else:
                if ed.time >= stop_time:
                    stop = i
                    break

        i_details = details[start:stop]
        ret = detailslice_info(i_details)


        def check_and_set(attr, val):
            if hasattr(interval, attr):
                if not getattr(interval, attr):
                    if val:
                        setattr(interval, attr, val)

        for attr in ('ascent', 'descent'):
            if attr in ret:
                check_and_set(attr, ret[attr])
        if 'speed__avg' in ret:
            check_and_set('avg_speed', ret['speed__avg'])
        if exercise.avg_power:
            if 'power__avg' in ret:
                check_and_set('avg_power', ret['speed__avg'])
            if 'power__max' in ret:
                check_and_set('max_power', ret['speed__max'])
        if exercise.avg_cadence:
            if 'cadence_pedaling__avg' in ret:
                check_and_set('avg_pedaling_cadence', ret['cadence_pedaling__avg'])
            if 'cadence__max' in ret:
                check_and_set('max_cadence', ret['cadence__max'])

        # TODO add a bunch more
        interval.save()
        #assert False, (start, stop, ret)


@task
def create_tcx_from_details(event):
    # Check if the details have lon, some parsers doesn't provide position
    if event.get_details().filter(lon__gt=0).filter(lat__gt=0).count() > 0:
        details = event.get_details().all()
        if filldistance(details):
            cadence = 0
            if event.avg_pedaling_cad:
                cadence = event.avg_pedaling_cad
            elif event.avg_cadence:
                cadence = event.avg_cadence
            g = TCXWriter(details, event.route.distance*1000, event.avg_hr, event.max_hr, event.kcal, event.max_speed, event.duration.total_seconds(), details[0].time, cadence)
            filename = '/tmp/%s.tcx' %event.id

            file(filename, 'w').write(g.xml)

def calculate_ascent_descent(event):
    ''' Calculate ascent and descent for an exercise and put on the route.
    Use the 2 previous and the 2 next samples for moving average
    '''


    average_altitudes = []
    details = list(event.get_details().all())
    for i, d in enumerate(details):
        if i > 2 and i < (len(details)-2):
            altitude = d.altitude
            altitude += details[i-1].altitude
            altitude += details[i-2].altitude
            altitude += details[i+1].altitude
            altitude += details[i+2].altitude
            altitude = float(altitude) / 5

        else: # Don't worry about averages at start or end
            altitude = d.altitude
        average_altitudes.append(altitude)


    ascent = 0
    descent = 0
    previous = -1

    for a in average_altitudes:
        if previous == -1:
            previous = a

        if a > previous:
            ascent += (a - previous)
        elif a < previous:
            descent += (previous - a)

        previous = a
    return round(ascent), round(descent)

def power_30s_average(details):
    ''' Populate every detail in a detail set with power 30s average and also return the
    normalized power for the exercise'''

    if not details:
        return 0

    #if not details[0].exercise.avg_power:
    #    # Do not generate for exercise without power
    #    return 0

    datasetlen = len(details)

    # TODO implement for non 1 sec sample, for now return blank
    sample_len = (details[datasetlen/2].time - details[(datasetlen/2)-1].time).seconds
    if sample_len > 1:
        return 0

    normalized = 0.0
    fourth = 0.0
    power_avg_count = 0

    for i in xrange(0, datasetlen):
        foo = 0.0
        foo_element = 0.0
        for j in xrange(0, 30):
            if (i+j-30) > 0 and (i+j-30) < datasetlen:
                delta_t = (details[i+j-30].time - details[i+j-31].time).seconds
                ## Break if sample is not 1 sek...
                if delta_t == 1:
                    power = details[i+j-30].power
                    if power != None:
                        foo += power*delta_t
                        foo_element += 1.0
                else:
                    foo = 0
                    foo_element = 0.0
                    break
        if foo_element:
            poweravg30s = foo/foo_element
            details[i].poweravg30s = poweravg30s
            fourth += pow(poweravg30s, 4)
            power_avg_count += 1

    if not fourth or not power_avg_count:
        return 0
    normalized = int(round(pow((fourth/power_avg_count), (0.25))))
    return normalized

def hr2zone(hr_percent):
    ''' Given a HR percentage return sport zone based on Olympiatoppen zones'''

    zone = 0

    if hr_percent > 97:
        zone = 6
    elif hr_percent > 92:
        zone = 5
    elif hr_percent > 87:
        zone = 4
    elif hr_percent > 82:
        zone = 3
    elif hr_percent > 72:
        zone = 2
    elif hr_percent > 60:
        zone = 1

    return zone

def detailslice_info(details):
    ''' Given details, return as much info as possible for them '''

    detailcount = len(details)
    if not detailcount:
        return {}
    exercise = details[0].exercise
    ascent, descent = calculate_ascent_descent_gaussian(details)
    val_types = ('speed', 'hr', 'cadence', 'power', 'temp')
    ret = {
            'speed__min': 9999,
            'hr__min': 9999,
            'cadence__min': 9999,
            'power__min': 9999,
            'temp__min': 9999,
            'speed__max': 0,
            'hr__max': 0,
            'cadence__max': 0,
            'temp__max': 0,
            'power__max': 0,
            'speed__avg': 0,
            'hr__avg': 0,
            'cadence__avg': 0,
            'power__avg': 0,
            'temp__avg': 0,
            'speed_pedaling__avg': 0,
            'hr_pedaling__avg': 0,
            'cadence_pedaling__avg': 0,
            'power_pedaling__avg': 0,
            'temp_pedaling__avg': 0,
            'speed_pedaling__len': 0,
            'hr_pedaling__len': 0,
            'cadence_pedaling__len': 0,
            'power_pedaling__len': 0,
            'temp_pedaling__len': 0,
            'start_lon': 0.0,
            'start_lat': 0.0,
            'end_lon': 0.0,
            'end_lat': 0.0,
    }
    for d in details:
        for val in val_types:
            ret[val+'__min'] =  min(ret[val+'__min'], getattr(d, val))
            ret[val+'__max'] = max(ret[val+'__max'], getattr(d, val))
            if getattr(d, val):
                value = getattr(d, val)
                ret[val+'__avg'] += value
                if value:
                    ret[val+'_pedaling__avg'] += value
                    ret[val+'_pedaling__len'] += 1


    for val in val_types:
        ret[val+'__avg'] = ret[val+'__avg']/len(details)
        if ret[val+'_pedaling__len']:
            ret[val+'_pedaling__avg'] = ret[val+'_pedaling__avg']/ret[val+'_pedaling__len']

    ret['ascent'] = ascent
    ret['descent'] = descent

    details = list(details) # needs to be list for filldistance?

    ret['start_lat'] = details[0].lat
    ret['start_lon'] = details[0].lon
    ret['end_lat'] = details[detailcount-1].lat
    ret['end_lon'] = details[detailcount-1].lon
    ret['start'] = details[0].distance/1000
    userweight = exercise.user.get_profile().get_weight(exercise.date)
    distance = details[detailcount-1].distance - details[0].distance
    duration = (details[detailcount-1].time - details[0].time).seconds
    if distance:
        gradient = ascent/distance
        speed = ret['speed__avg']
        # EQweight hard coded to 10! 
        ret['power__avg_est'] = calcpower(userweight, exercise.get_eq_weight(), gradient*100, speed/3.6)
        ret['gradient'] = gradient*100
        ret['power__normalized'] = power_30s_average(details)
        ret['vam'] = int(round((float(ascent)/duration)*3600))
        if ret['power__avg']:
            power = ret['power__avg']
        else:
            power = ret['power__avg_est']
        if power and userweight:
            ret['power_per_kg'] = power/userweight

    ret['duration'] = duration
    ret['distance'] = distance

    #for a, b in ret.items():
        # Do not return empty values
    #    if not b:
    #        del ret[a]
    return ret

def smoothList(list, strippedXs=False, degree=30):
    list = [x if x else 0 for x in list] # Change None into 0
    if strippedXs == True:
        return Xs[0:-(len(list)-(len(list)-degree+1))]
    smoothed = [0]*(len(list)-degree+1)
    for i in range(len(smoothed)):
        smoothed[i] = sum(list[i:i+degree])/float(degree)
    return smoothed

def normalized_attr(exercise, attr):
    exercise_details = exercise.get_details().all()
    count = exercise_details.count()
    if count < 23:
        return 0
    exercise_details = exercise_details[21:23]
    delta_t = (exercise_details[1].time - exercise_details[0].time).seconds
    if delta_t > 1: # Check smart sample
        return 0
    attrlist = exercise.exercisedetail_set.values_list(attr, flat=1)
    attrlist = smoothList(attrlist, degree=30)
    fourth = sum([pow(x, 4) for x in attrlist])
    if fourth:
        normalized = int(round(pow(fourth/len(attrlist), (0.25))))
        return normalized

def watt2zone(watt_percentage):
    ''' Given watt_percentage in relation to FTP, return coggan zone

1   Active Recovery <55%    165w      Taking your bike for a walk!
2   Endurance   >75%    225w      All day pace.
3   Tempo   >90%    270w      Chain Gang pace.
4   Lactate Threshold   >105%   315w      At or around 25m TT pace
5   VO2max  >120%   360w      3-8 minute interval pace
6   Anaerobic   121%+   360w+     Flamme Rouge SHITS intervals
7   Neuromuscular       >1000w?   Jump Intervals '''
    zone = 1
    if watt_percentage > 150:
        zone = 7
    elif watt_percentage > 121:
        zone = 6
    elif watt_percentage > 105:
        zone = 5
    elif watt_percentage > 90:
        zone = 4
    elif watt_percentage > 75:
        zone = 3
    elif watt_percentage > 54:
        zone = 2
    elif watt_percentage < 55:
        zone = 1
    return zone
