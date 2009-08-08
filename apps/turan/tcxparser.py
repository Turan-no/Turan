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

class TCXParser(object):
    def __init__(self, gps_distance=False):
        self.entries = []
        self.gps_distance = gps_distance
        if gps_distance:
            self.geod = pyproj.Geod(ellps='WGS84')

    def parse_uploaded_file(self, f):
        self.cur_distance = 0

        t = ElementTree.parse(f)

        # warning. ugly xml crap ahead
        #garmin probably supports multiple laps, should be fixed
        try: 
            lap = t.find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Activities").find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Activity").find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Lap")
        except:
            lap = t.find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Courses").find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Course").find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Lap")
        try:
            startstring = dict(lap.items())["StartTime"]
        except:
            startstring = t.find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Courses").find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Course").find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Track").find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Trackpoint").find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Time").text
        self.time = datetime.datetime(*map(int, startstring.replace("T","-").replace(":","-").strip("Z").split("-")))
        self.cur_time = self.time

        try:
            self.kcal_sum = int(lap.find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Calories").text)
        except AttributeError:
            self.kcal_sum = 0

        try:
            self.avg_cadence = int(lap.find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Cadence").text)
        except AttributeError:
            self.avg_cadence = 0

        try:
            self.max_hr = int(lap.find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}MaximumHeartRateBpm").find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Value").text)
        except AttributeError:
            self.max_hr = 0    # Ring 113

        try:
            self.avg_hr = int(lap.find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}AverageHeartRateBpm").find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Value").text)
        except AttributeError:
            self.avg_hr = 0    # Ring 113
        
        if self.gps_distance:
            self.distance_sum = 0.0
        else:
            try:
                self.distance_sum = float(lap.find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}DistanceMeters").text)
            except AttributeError:
                self.distance_sum = 0.0

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
                altitude = 0

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

            power = 0 # not yet

            time = datetime.datetime(*map(int, tstring.replace("T","-").replace(":","-").strip("Z").split("-")))

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
                    speed = self.entries[-1].speed
            else:
                speed = 0.0

            self.entries.append(TCXEntry(time, hr, speed, cadence, altitude, lon, lat, power))
            self.cur_time = time

        try:
            seconds = float(lap.find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}TotalTimeSeconds").text)
        except AttributeError:
            seconds = 1.0 # we're going to divide by this, can't set to 0
        
        self.avg_speed = self.distance_sum / seconds * 3.6
        if self.gps_distance:
            self.max_speed = max([self.entries[i].speed for i in xrange(0,len(self.entries))])
        else:
            try:
                self.max_speed = float(lap.find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}MaximumSpeed").text)*3.6
            except AttributeError:
                self.max_speed = max(filter(lambda x: x<= 200,[self.entries[i].speed for i in xrange(0,len(self.entries))]))
 
        self.max_cadence = max([self.entries[i].cadence for i in xrange(0,len(self.entries))])
        self.duration = '%is' % int(seconds)
