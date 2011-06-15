#!/usr/bin/python
from xml.etree import ElementTree
import datetime
import pyproj
from math import hypot

garmin_ns = '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}'

class TCXEntry(object):
    def __init__(self, time, hr, speed, cadence, altitude, lon, lat, power, distance):
        self.time = time
        self.hr = hr
        self.speed = speed
        self.cadence = cadence
        self.altitude = altitude
        self.lon = lon
        self.lat = lat
        self.power = power
        self.distance = distance
    def __unicode__(self):
        return '[%s] hr: %s, speed: %s, cadence: %s, alt: %s, lon %s, lat: %s, power: %s' % (self.time, self.hr, self.speed, self.cadence, self.altitude, self.lon, self.lat, self.power)

    def __str__(self):
        return self.__unicode__()

class LapData(object):
    def __init__(self, start_time, duration, distance,  max_speed, avg_hr, max_hr, avg_cadence, kcal_sum):
        self.start_time = start_time
        self.duration = duration
        self.distance = distance
        self.max_speed = max_speed
        self.avg_hr = avg_hr
        self.max_hr = max_hr
        self.avg_cadence = avg_cadence
        self.kcal_sum = kcal_sum
        self.kcal = self.kcal_sum # alias

class TCXParser(object):
    def __init__(self, gps_distance=False):
        self.entries = []
        self.gps_distance = gps_distance
        #if gps_distance:
        #initialize it no matter if we need or not
        self.geod = pyproj.Geod(ellps='WGS84')

    def parse_uploaded_file(self, f):
        self.cur_distance = 0

        t = ElementTree.parse(f)

        self.laps = []
        # warning. ugly xml crap ahead
        lapskaus = t.getiterator(garmin_ns + "Lap")
        for lap in lapskaus:
            try:
                startstring = dict(lap.items())["StartTime"]
            except:
                startstring = t.find(garmin_ns + "Courses").find(garmin_ns + "Course").find(garmin_ns + "Track").find(garmin_ns + "Trackpoint").find(garmin_ns + "Time").text
            time = datetime.datetime(*map(int, startstring.replace("T","-").replace(":","-").replace(".","-").strip("Z").split("-")))

            try:
                kcal_sum = int(lap.find(garmin_ns + "Calories").text)
            except AttributeError:
                kcal_sum = 0
            except ValueError:
                kcal_sum = int(float(lap.find(garmin_ns + "Calories").text))

            try:
                avg_cadence = int(lap.find(garmin_ns + "Cadence").text)
            except AttributeError:
                avg_cadence = 0

            try:
                max_hr = int(float(lap.find(garmin_ns + "MaximumHeartRateBpm").find(garmin_ns + "Value").text))
            except AttributeError:
                max_hr = 0    # Ring 113

            try:
                avg_hr = int(float(lap.find(garmin_ns + "AverageHeartRateBpm").find(garmin_ns + "Value").text))
            except AttributeError:
                avg_hr = 0    # Ring 113

            try:
                distance_sum = float(lap.find(garmin_ns + "DistanceMeters").text)
            except AttributeError:
                distance_sum = 0.0

            try:
                duration = float(lap.find(garmin_ns + "TotalTimeSeconds").text)
            except AttributeError:
                duration = 1.0 # we're going to divide by this, can't set to 0

            try:
                max_speed = float(lap.find(garmin_ns + "MaximumSpeed").text)*3.6
            except AttributeError:
                max_speed = None

            self.laps.append(LapData(time, duration, distance_sum, max_speed, avg_hr, max_hr, avg_cadence, kcal_sum))

        self.time = self.laps[0].start_time
        self.start_time = datetime.time(self.time.hour, self.time.minute, self.time.second)
        self.date = datetime.date(self.time.year, self.time.month, self.time.day)
        self.cur_time = self.time

        if self.gps_distance:
            self.distance_sum = 0.0
        else:
            self.distance_sum = sum([self.laps[i].distance for i in xrange(0,len(self.laps))])
        self.max_hr = max([self.laps[i].max_hr for i in xrange(0,len(self.laps))])
        try:
            tmp_avg_hr_index = sum([(self.laps[i].distance * self.laps[i].avg_hr) for i in xrange(0,len(self.laps))])
            self.avg_hr = tmp_avg_hr_index / self.distance_sum
        except ZeroDivisionError:
            self.avg_hr = 0

        try:
            tmp_avg_cadence_index = sum([(self.laps[i].distance * self.laps[i].avg_cadence) for i in xrange(0,len(self.laps))])
            self.avg_cadence = tmp_avg_cadence_index / self.distance_sum
        except ZeroDivisionError:
            self.avg_cadence = None

        self.kcal_sum = sum([self.laps[i].kcal_sum for i in xrange(0,len(self.laps))])

        self.heartbeats = 0
        self.rotations = 0
        self.pedaling_cad = 0
        pedaling_cad_seconds = 0
        pedaling_power_seconds = 0
        self.powersum = 0
        need_initial_altitude = 0
        for e in t.getiterator(tag=garmin_ns + "Trackpoint"):
            try:
                tstring = e.find(garmin_ns + "Time").text
            except AttributeError:
                continue

            try:
                hr = int(float(e.find(garmin_ns + "HeartRateBpm").find(garmin_ns + "Value").text))
            except AttributeError:
                hr = 0
                if self.entries:
                    hr = self.entries[-1].hr

            try:
                altitude = float(e.find(garmin_ns + "AltitudeMeters").text)
                if need_initial_altitude:
                    # We never found altitude until now. Set the same altitude on all prevfious entries
                    for e in self.entries:
                        e.altitude = altitude
                    need_initial_altitude = False
            except AttributeError:
                # Some garmin devices just don't report altitude in all points, 
                # so we just use the previous value
                if self.entries:
                    altitude = self.entries[-1].altitude
                else: # Missing altitude in the first value
                    altitude = 0
                    need_initial_altitude = True


            try:
                distance = float(e.find(garmin_ns + "DistanceMeters").text)
            except AttributeError:
                ## TODO figure out why elements lack distance, make this smarter ?
                #distance = self.cur_distance
# 310 XT maybe fix??
                pass
                distance = 0

            try:
                cadence = int(e.find(garmin_ns + "Cadence").text)
            except AttributeError:
                cadence = 0

            try:
                lon = float(e.find(garmin_ns + "Position").find(garmin_ns + "LongitudeDegrees").text)
            except AttributeError:
                lon = 0.0

            try:
                lat = float(e.find(garmin_ns + "Position").find(garmin_ns + "LatitudeDegrees").text)
            except AttributeError:
                lat = 0.0

            try:
                power = int(e.find(garmin_ns + "Extensions").find("{http://www.garmin.com/xmlschemas/ActivityExtension/v2}TPX").find("{http://www.garmin.com/xmlschemas/ActivityExtension/v2}Watts").text)
            except AttributeError:
                power = 0

            # Quickfix to skip empty trackpoints found at least in Garmin Edge 500 tcx-files
            #if lat == 0.0 and lon == 0.0 and distance == 0 and hr == 0:
            #    print "watness"
            #    continue
            # Check for silly 310XT only pos values
            # as in trackpoints with only lon, lat and altitude, but no other values
            if lat and lon and altitude and not (distance or hr or power or cadence):
                continue


            time = datetime.datetime(*map(int, tstring.replace("T","-").replace(":","-").replace(".","-").strip("Z").split("-")))

            timedelta = (time - self.cur_time).seconds
            distdelta = 0
            if self.gps_distance or (not distance and lon and lat):
                 # Didn't find DistanceMeterElement..but we have lon/lat, so calculate
                if self.entries:
                    #assert False, (timedelta, distance, lon, lat, altitude, power, hr, cadence)
                    o = self.entries[-1]
                    if o.lon and o.lat:
                        try:
                            hdelta = self.geod.inv(lon, lat, o.lon, o.lat)[2]
                            distdelta = hypot(hdelta, o.altitude-altitude)
                        except ValueError:
                            distdelta = 0
            if not distdelta:
                if distance:
                    distdelta = distance - self.cur_distance
                    self.cur_distance = distance
            if distdelta and not distance: # For gps_distance = True
                distance = self.cur_distance + distdelta
                self.cur_distance = distance

            if timedelta and distdelta:
                speed = distdelta/timedelta * 3.6
                if speed >= 200: #FIXME oh so naive
                    if self.entries:
                        speed = self.entries[-1].speed
                    else:
                        speed = 0
            else:
                speed = 0.0

            if timedelta <= 60:
                self.heartbeats += hr*timedelta
                self.rotations += cadence*timedelta
                if power:
                    self.powersum += power*timedelta
                    pedaling_power_seconds += timedelta
                if cadence > 0:
                    self.pedaling_cad += cadence*timedelta
                    pedaling_cad_seconds += timedelta

            t = TCXEntry(time, hr, speed, cadence, altitude, lon, lat, power, distance)
            self.entries.append(t)
            self.cur_time = time

        if self.gps_distance:
            self.max_speed = max([self.entries[i].speed for i in xrange(0,len(self.entries))])
            self.distance_sum = self.entries[-1].distance
        else:
            try:
                self.max_speed = max([self.laps[i].max_speed for i in xrange(0,len(self.laps))])
            except:
                pass
            try:
                if not self.max_speed:
                    self.max_speed = max(filter(lambda x: x<= 200,[self.entries[i].speed for i in xrange(0,len(self.entries))]))
            except:
                pass

        seconds = sum([self.laps[i].duration for i in xrange(0,len(self.laps))])
        self.avg_speed = self.distance_sum / seconds * 3.6
        try:
            self.max_cadence = max([self.entries[i].cadence for i in xrange(0,len(self.entries))])
        except:
            self.max_cadence = 0
            pass
        if self.rotations > 1.0:
            self.avg_cadence = self.rotations/seconds
            self.avg_pedaling_cad = self.pedaling_cad/pedaling_cad_seconds
        if self.heartbeats > 1.0:
            self.avg_hr = self.heartbeats/seconds
        self.duration = '%is' % int(seconds)
        if self.powersum:
            self.avg_power = self.powersum/seconds
            self.max_power = max([self.entries[i].power for i in xrange(0,len(self.entries))])
            self.avg_pedaling_power = self.powersum/pedaling_power_seconds


if __name__ == '__main__':

    import pprint
    import sys
    t = TCXParser(gps_distance=1)
    t.parse_uploaded_file(file(sys.argv[1]))

    print "Time, Speed, Altitude, Hr, Cadence"
    for x in t.entries:
        print x.time, x.speed, x.altitude, x.hr, x.cadence, x.distance

    print t.avg_hr, t.avg_speed, t.avg_cadence
    print t.max_hr, t.max_speed, t.max_cadence
    print t.start_time
    print t.date
    print t.distance_sum
