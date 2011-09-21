#!/usr/bin/python

''' This module will take a file, that is a dump of Strava JSON-api, and parse it into entries

    @author: Bjorn-Olav Strand <bolav@ikke.no>
'''


import simplejson
from datetime import datetime, timedelta, date

class StravaEntry(object):
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

class StravaStreamParser(object):
    def parse_uploaded_file(self, f):
        strava = simplejson.load(f)
        self.laps = []
        self.entries = []
        self.max_speed = strava["meta"]["ride"]["maximumSpeed"] / 1000
        self.max_hr = 0
        self.max_cadence = 0
        self.avg_hr = 0
        self.avg_cadence = 0
        self.avg_speed = strava["meta"]["ride"]["averageSpeed"] * 3.6
        self.kcal_sum = 0
        self.distance_sum = strava["meta"]["ride"]["distance"]
        self.avg_power = 0
        self.max_power = 0
        # self.start_time = datetime.now()
        j = strava["stream"]
        startstring = strava["meta"]["ride"]["startDateLocal"]
        self.time = datetime(*map(int, startstring.replace("T","-").replace(":","-").replace(".","-").strip("Z").split("-")))
        self.start_time = self.time
        self.date = date(self.time.year, self.time.month, self.time.day)
        self.duration = '%is' % int(strava["meta"]["ride"]["elapsedTime"])
        self.heartbeats = 0
        
        lasttime = j["time"][0]
        lastdist = j["distance"][0]
        for i in range(0,len(j["latlng"])):
            deltatime = j["time"][i] - lasttime
            altitude = j["altitude"][i]
            if "speed" in j:
                speed = j["speed"][i]
            else:
                if (deltatime == 0):
                    deltatime = 1
                deltadist = j["distance"][i] - lastdist
                speed = (deltadist / deltatime) * 3.6 
            distance = j["distance"][i]
            lat = j["latlng"][i][0]
            lon = j["latlng"][i][1]
            if "cadence" in j:
                cadence = j["cadence"][i]
            else:
                cadence = 0
            if "watts" in j:
                power = j["watts"][i]
            else:
                power = 0
            if "heartrate" in j:
                hr = j["heartrate"][i]
            else:
                hr = 0
            time = self.start_time + timedelta(seconds=j["time"][i])
            t = StravaEntry(time, hr, speed, cadence, altitude, lon, lat, power, distance)
            lasttime = j["time"][i]
            lastdist = distance
            self.entries.append(t)
            
            self.heartbeats += hr * deltatime
            # setup maxs
            if (hr > self.max_hr):
                self.max_hr = hr
            if (speed > self.max_speed):
                self.max_speed = speed
            if (cadence > self.max_cadence):
                self.max_cadence = cadence
        
        self.start_lat = self.entries[0].lat
        self.start_lon = self.entries[0].lon
        self.end_lat = self.entries[-1].lat
        self.end_lon = self.entries[-1].lon
        self.avg_hr = self.heartbeats / strava["meta"]["ride"]["elapsedTime"]
        self.laps.append(LapData(self.start_time, strava["meta"]["ride"]["elapsedTime"], strava["meta"]["ride"]["distance"], self.max_speed, self.avg_hr, self.max_hr, self.avg_cadence, self.kcal_sum))

if __name__ == '__main__':
    import pprint
    import sys
    print sys.argv[1]
    t = StravaStreamParser()
    t.parse_uploaded_file(file(sys.argv[1]))

    for e in t.entries:
        print e
    for lap in t.laps:
        print lap

    print 'start: %s %s - duration: %s - distance: %s' % (t.date, t.start_time, t.duration, t.distance_sum)
    print 'start - lat: %s - lon: %s' % (t.start_lat, t.start_lon)
    print 'end - lat: %s - lon: %s' % (t.end_lat, t.end_lon)
    print 'HR - avg: %s - max: %s' % (t.avg_hr, t.max_hr)
    print 'SPEED - avg: %s - max: %s' % (t.avg_speed, t.max_speed)
    print 'CADENCE - avg: %s - max: %s' % (t.avg_cadence, t.max_cadence)
    print 'POWER - avg: %s - max: %s' % (t.avg_power, t.max_power)
    print 'LAPS: %s ENTRIES: %s' %(len(t.laps), len(t.entries))
