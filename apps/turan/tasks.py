from celery.decorators import task
from celery.task.sets import subtask

from subprocess import call
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.db.models import get_model
from django.db import connection, transaction
from django.db.models import Avg, Max, Min, Count, Variance, StdDev, Sum

import numpy
from collections import deque

from svg import GPX2SVG
from gpxwriter import GPXWriter
from gpxparser import GPXParser
from hrmparser import HRMParser
from gmdparser import GMDParser
from tcxparser import TCXParser
from csvparser import CSVParser
from pwxparser import PWXParser


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
    else:
        raise Exception('Parser not found') # Maybe warn user somehow?
    return parser

def filldistance(values):
    d = 0
    if values:
        values[0].distance = 0
    for i in xrange(1,len(values)):
        delta_t = (values[i].time - values[i-1].time).seconds
        d += values[i].speed/3.6 * delta_t
        values[i].distance = d
    return d

def getavghr(values, start, end):
    hr = 0
    for i in xrange(start+1, end+1):
        delta_t = (values[i].time - values[i-1].time).seconds
        if values[i].hr:
            hr += values[i].hr*delta_t
    delta_t = (values[end].time - values[start].time).seconds
    return float(hr)/delta_t

def getavgpwr(values, start, end):
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
    tot_weight = userweight+eqweight
    gforce = tot_weight * gradient/100 * 9.81
    frictionforce = rollingresistance * tot_weight * 9.81
    windforce = 0.5**2 * speed**2  * airdensity * frontarea
    return (gforce + frictionforce + windforce)*speed

@task
def getslopes(values, userweight):
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
    for i in xrange(1,len(values)):
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
                    cur_stop = stop_since
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
                        slope.est_power = calcpower(userweight, 10, slope.grade, slope.speed/3.6)
                        slope.act_power = getavgpwr(values, cur_start, cur_end)

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

@task
def create_simplified_gpx(gpx_path, filename):
    cmd = 'gpsbabel -i gpx -f %s -x duplicate,location -x position,distance=1m -x simplify,crosstrack,error=0.005k -o gpx -F %s' % (\
            gpx_path,
            '/'.join(gpx_path.split('/')[0:-2]) + '/' + filename)
    retcode = call(cmd.split())
    return retcode

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
                pass # Did not find match, silently continue
    if not callback is None:
        subtask(callback).delay(exercise)
#    create_gpx_from_details.delay(exercise)

def smoothListGaussian(list,degree=5):
    list = [list[0]]*(degree-1) + list + [list[-1]]*degree
    window=degree*2-1
    weight=numpy.array([1.0]*window)
    weightGauss=[]
    for i in range(window):
        i=i-degree+1
        frac=i/float(window)
        gauss=1/(numpy.exp((4*(frac))**2))
        weightGauss.append(gauss)
    weight=numpy.array(weightGauss)*weight
    smoothed=[0.0]*(len(list)-window)
    for i in range(len(smoothed)):
        smoothed[i]=sum(numpy.array(list[i:i+window])*weight)/sum(weight)
    return smoothed

def calculate_ascent_descent_gaussian(details):
    ''' Calculate ascent and descent for an exercise. Use guassian filter to smooth '''

    altvals = []
    for a in details:
        altvals.append(a.altitude)

    altvals = smoothListGaussian(altvals)

    ascent = 0
    descent = 0
    previous = -1

    for a in altvals:
        if previous == -1:
            previous = a

        if a > previous:
            ascent += (a - previous)
        if a < previous:
            descent += (previous - a)

        previous = a
    return round(ascent), round(descent)

def best_x_sec(details, length, power):

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

    q_speed.appendleft(details[0].speed)
    if power:
        q_power.appendleft(details[0].power)
    j = 2
    len_i = len(details)
    for i in xrange(2, len_i):
        try:
            delta_t = (details[i].time - details[i-1].time).seconds
            # Break if exerciser is on a break as well
            if delta_t < 60:
                q_speed.appendleft(details[i].speed * delta_t)
            else:
                q_speed = deque()
                q_speed.appendleft(details[i].speed)
            if power:
                if delta_t < 60:
                    q_power.appendleft(details[i].power * delta_t)
                else:
                    q_power = deque()
                    q_power.appendleft(details[i].power)
            delta_t_total = (details[i].time - details[i-len(q_speed)].time).seconds
            if delta_t_total >= length:
                break
            j += 1
        except Exception as e:
            #print "%s %s %s %s %s" % (e, i, j, delta_t, len(q_speed))
            #j += 1
            continue
    j += 1

    for i in xrange(j, len(details)):

        try:
            if len(q_speed) != 0:
                sum_q_speed_tmp = sum(q_speed)
                delta_t_total = (details[i].time - details[i-len(q_speed)].time).seconds

                if delta_t_total != 0 and delta_t_total == length:
                    sum_q_speed = sum_q_speed_tmp / (details[i].time - details[i-len(q_speed)].time).seconds
                else:
                    # What can one do?
                    sum_q_speed = 0
            if len(q_power) != 0:
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
            if delta_t < 60:
                q_speed.appendleft(details[i].speed*delta_t)
            else:
                q_speed = deque()
            if power:
                if delta_t < 60:
                    q_power.appendleft(details[i].power*delta_t)
                else:
                    q_power = deque()
            while ((details[i].time - details[i-len(q_speed)].time).seconds) > length:
                q_speed.pop()
            while (power and (details[i].time - details[i-len(q_power)].time).seconds > length):
                q_power.pop()
        except Exception as e:
            #print "something wrong %s, %s, %s, %s" % (e, len(q_speed), i, j)
            #raise
            continue


    if power:
        best_speed_ascent = 0
        best_speed_descent = 0
        best_power_ascent = 0
        best_power_descent = 0
        if best_speed_start_end:
            c, d = best_speed_start_end
            best_speed_ascent, best_speed_descent = calculate_ascent_descent_gaussian(details[d:c])
        if best_power_start_end:
            a, b = best_power_start_end
            best_power_ascent, best_power_descent = calculate_ascent_descent_gaussian(details[b:a])

        return best_speed, best_start_km_speed, best_length_speed, best_speed_ascent, best_speed_descent, best_power, best_start_km_power, best_length_power, best_power_ascent, best_power_descent
    else:
        best_speed_ascent = 0
        best_speed_descent = 0
        if best_speed_start_end:
            a, b = best_speed_start_end
            best_speed_ascent, best_speed_descent = calculate_ascent_descent_gaussian(details[b:a])
        return best_speed, best_start_km_speed, best_length_speed, best_speed_ascent, best_speed_descent

@task
def calculate_best_efforts(exercise, callback=None):
    ''' Iterate over details for different effort ranges finding best
    speed and power efforts '''

    # First: Delete any existing best efforts
    exercise.bestspeedeffort_set.all().delete()
    exercise.bestpowereffort_set.all().delete()
    BestSpeedEffort = get_model('turan', 'BestSpeedEffort')
    BestPowerEffort = get_model('turan', 'BestPowerEffort')

    details = exercise.get_details().all()
    if details:
        if filldistance(details):
            effort_range = [5, 30, 60, 300, 600, 1800, 3600]
            for seconds in effort_range:
                if exercise.avg_power and not exercise.is_smart_sampled():
                    speed, pos, length, speed_ascent, speed_descent, power, power_pos, power_length, power_ascent, power_descent = best_x_sec(details, seconds, power=True)
                    if power:
                        be = BestPowerEffort(exercise=exercise, power=power, pos=power_pos, length=power_length, duration=seconds, ascent=power_ascent, descent=power_descent)
                        be.save()
                else:
                    speed, pos, length, speed_ascent, speed_descent = best_x_sec(details, seconds, power=False)
                if speed:
                    be = BestSpeedEffort(exercise=exercise, speed=speed, pos=pos, length=length, duration=seconds, ascent=speed_ascent, descent=speed_descent)
                    be.save()
    if not callback is None:
        subtask(callback).delay(exercise)

def normalize_altitude(exercise):
    ''' Normalize altitude, that is, if it's below zero scale every value up '''

    altitude_min = exercise.get_details().aggregate(Min('altitude'))['altitude__min']
    if altitude_min and altitude_min < 0:
        altitude_min = 0 - altitude_min
        for d in exercise.get_details().all():
            d.altitude += altitude_min
            d.save()

@task
def parse_sensordata(exercise, callback=None):
    ''' The function that takes care of parsing data file from sports equipment from polar or garmin and putting values into the detail-db, and also summarized values for trip. '''

    ExerciseDetail = get_model('turan', 'ExerciseDetail')


    if exercise.get_details().count(): # If the exercise already has details, delete them and reparse
        # Django is super shitty when it comes to deleation. If you want to delete 25k objects, it uses 500 queries to do so.
        # So. We do some RAWness.
        cursor = connection.cursor()

        # Data modifying operation - commit required
        cursor.execute("DELETE FROM turan_exercisedetail WHERE exercise_id = %s", [exercise.id])
        transaction.commit_unless_managed()

    if exercise.slope_set.count(): # If the exercise has slopes, delete them too
        exercise.slope_set.all().delete()


    exercise.sensor_file.file.seek(0)
    parser = find_parser(exercise.sensor_file.name)
    parser.parse_uploaded_file(exercise.sensor_file.file)
    #if EXPERIMENTAL_POLAR_GPX_HRM_COMBINER:
    #    gpxvalues = GPXParser(exercise.route.gpx_file.file).entries

    for val in parser.entries:
        detail = ExerciseDetail()
        detail.exercise_id = exercise.id

        # Figure out which values the parser has
        for v in ('time', 'hr', 'altitude', 'speed', 'cadence', 'lon', 'lat', 'power'):
            if hasattr(val, v):
                #if not types.NoneType == type(val[v]):
                setattr(detail, v, getattr(val, v))
        #if EXPERIMENTAL_POLAR_GPX_HRM_COMBINER:
        #    if not d.lat and not d.lon: # try and get from .gpx FIXME yeah...you know why
        #        try:
        #            d.lon = gpxvalues[i]['lon']
        #            d.lat = gpxvalues[i]['lat']
        #        except IndexError:
        #            pass # well..it might not match
        detail.save()

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

    if hasattr(parser, 'temperature'): # Polar has this
        if parser.temperature:
            exercise.temperature = parser.temperature

    if hasattr(parser, 'comment'): # Polar has this
        if parser.comment: # comment isn't always set
            exercise.comment = parser.comment

    # Normalize altitude, that is, if it's below zero scale every value up
    normalize_altitude(exercise)

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
    exercise.save()

    if not callback is None:
        subtask(callback).delay(exercise)

    # Apply jobs, so we can use this in view
    merge_sensordata(exercise)
    create_gpx_from_details(exercise)
    calculate_best_efforts(exercise)
    if hasattr(route, 'ascent') and route.ascent > 0:
        getslopes(exercise.get_details().all(), exercise.user.get_profile().get_weight(exercise.date))

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
            g = TCXWriter(details, event.route.distance*1000, event.avg_hr, event.max_hr, event.kcal, event.max_speed, event.duration.seconds, details[0].time, cadence)
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
        if a < previous:
            descent += (previous - a)

        previous = a
    return round(ascent), round(descent)
