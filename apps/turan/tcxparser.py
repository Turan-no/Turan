#!/usr/bin/python
from xml.etree import ElementTree
import datetime
import pyproj
from math import hypot

class TCXEntry(object):
    def __init__(self, time, hr, speed, cadence, altitude, lon, lat, power):
        self.time = time
        self.hr = hr
        self.speed = speed
        self.cadence = cadence
        self.altitude = altitude
        self.lon = lon
        self.lat = lat
        self.power = power
    def __unicode__(self):
         return '[%s] hr: %s, speed: %s, cadence: %s, alt: %s, lon %s, lat: %s, power: %s' % (self.time, self.hr, self.speed, self.cadence, self.altitude, self.lon, self.lat, self.power)

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

class TCXParser(object):
    def __init__(self, gps_distance=False):
        self.entries = []
        self.gps_distance = gps_distance
        if gps_distance:
            self.geod = pyproj.Geod(ellps='WGS84')

    def parse_uploaded_file(self, f):
        self.cur_distance = 0

        t = ElementTree.parse(f)

        self.laps = []
        # warning. ugly xml crap ahead
        lapskaus = t.getiterator("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Lap")
        for lap in lapskaus:
            try:
                startstring = dict(lap.items())["StartTime"]
            except:
                startstring = t.find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Courses").find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Course").find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Track").find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Trackpoint").find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Time").text
            time = datetime.datetime(*map(int, startstring.replace("T","-").replace(":","-").replace(".","-").strip("Z").split("-")))

            try:
                kcal_sum = int(lap.find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Calories").text)
            except AttributeError:
                kcal_sum = 0

            try:
                avg_cadence = int(lap.find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Cadence").text)
            except AttributeError:
                avg_cadence = 0

            try:
                max_hr = int(lap.find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}MaximumHeartRateBpm").find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Value").text)
            except AttributeError:
                max_hr = 0    # Ring 113

            try:
                avg_hr = int(lap.find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}AverageHeartRateBpm").find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Value").text)
            except AttributeError:
                avg_hr = 0    # Ring 113
            
            try:
                distance_sum = float(lap.find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}DistanceMeters").text)
            except AttributeError:
                distance_sum = 0.0

            try:
                duration = float(lap.find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}TotalTimeSeconds").text)
            except AttributeError:
                duration = 1.0 # we're going to divide by this, can't set to 0

            try:
                max_speed = float(lap.find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}MaximumSpeed").text)*3.6
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
        last_altitude = 0
        for e in t.getiterator(tag="{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Trackpoint"):
            try:
                tstring = e.find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Time").text
            except AttributeError:
                continue

            try:
                hr = int(e.find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}HeartRateBpm").find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Value").text)
            except AttributeError:
                hr = 0

            try:
                altitude = float(e.find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}AltitudeMeters").text)
            except AttributeError:
                altitude = last_altitude

            try:
                distance = float(e.find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}DistanceMeters").text)
            except AttributeError:
                distance = 0

            try:
                cadence = int(e.find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Cadence").text)
            except AttributeError:
                cadence = 0

            try:
                lon = float(e.find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Position").find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}LongitudeDegrees").text)
            except AttributeError:
                lon = 0.0

            try:
                lat = float(e.find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Position").find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}LatitudeDegrees").text)
            except AttributeError:
                lat = 0.0

            try:
                power = int(e.find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Extensions").find("{http://www.garmin.com/xmlschemas/ActivityExtension/v2}TPX").find("{http://www.garmin.com/xmlschemas/ActivityExtension/v2}Watts").text)
            except AttributeError:
                power = 0

            # Quickfix to skip empty trackpoints found at least in Garmin Edge 500 tcx-files
            if lat == 0.0 and lon == 0.0 and distance == 0:
                continue

            time = datetime.datetime(*map(int, tstring.replace("T","-").replace(":","-").replace(".","-").strip("Z").split("-")))

            timedelta = (time - self.cur_time).seconds
            distdelta = 0

            if self.gps_distance:
                if len(self.entries):
                    try:
                        hdelta = self.geod.inv(lon, lat, self.entries[-1].lon, self.entries[-1].lat)[2]
                        distdelta = hypot(hdelta, self.entries[-1].altitude-altitude)
                    except ValueError:
                        distdelta = 0
                self.distance_sum += distdelta
            else:
                distdelta = distance - self.cur_distance
                self.cur_distance = distance

            if timedelta and distdelta:
                speed = distdelta/timedelta * 3.6
                if speed >= 200:
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

            self.entries.append(TCXEntry(time, hr, speed, cadence, altitude, lon, lat, power))
            self.cur_time = time
            last_altitude = altitude

        seconds = sum([self.laps[i].duration for i in xrange(0,len(self.laps))])
        self.avg_speed = self.distance_sum / seconds * 3.6
        if self.gps_distance:
            self.max_speed = max([self.entries[i].speed for i in xrange(0,len(self.entries))])
        else:
            try:
                self.max_speed = max([self.laps[i].max_speed for i in xrange(0,len(self.laps))])
            except:
                pass
            if not self.max_speed:
                self.max_speed = max(filter(lambda x: x<= 200,[self.entries[i].speed for i in xrange(0,len(self.entries))]))
 
        self.max_cadence = max([self.entries[i].cadence for i in xrange(0,len(self.entries))])
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
    t = TCXParser()
    t.parse_uploaded_file(file(sys.argv[1]))

    for x in t.entries:
        print x.time, x.speed, x.altitude, x.hr, x.cadence

    print t.avg_hr, t.avg_speed, t.avg_cadence
    print t.max_hr, t.max_speed, t.max_cadence
    print t.start_time
    print t.date
