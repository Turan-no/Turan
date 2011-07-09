#!/usr/bin/env python
import datetime
from BeautifulSoup import BeautifulSoup

class GMDEntry(object):
    def __init__(self, time, hr, speed, cadence, altitude, lon, lat, distance):
        self.time = time
        self.hr = hr
        self.speed = speed
        self.cadence = cadence
        self.altitude = altitude
        self.lon = lon
        self.lat = lat
        self.distance = distance
    def __unicode__(self):
        return '[%s] hr: %s, speed: %s, cadence: %s, alt: %s, lon %s, lat: %s, dist: %s' % (self.time, self.hr, self.speed, self.cadence, self.altitude, self.lon, self.lat, self.distance)
    
    def __str__(self):
        return self.__unicode__()

class GMDParser(object):

    def __init__(self):
        self.started = False
        self.entries = []
        self.laps = []
        self.start_time = 0
        self.date = 0
        self.interval = 0
        self.duration = 0

        self.avg_hr = 0
        self.avg_speed = 0
        self.avg_cadence = 0

        self.max_hr = 0
        self.max_speed = 0
        self.max_cadence = 0

        self.hr_sum = 0
        self.speed_sum = 0
        self.cadence_sum = 0

    def __unicode__(self):
        return '%s hr: %s/%s speed: %s/%s' % (self.duration, self.avg_hr, self.max_hr, self.avg_speed, self.max_speed)
    
    def __str__(self):
        return self.__unicode__()

    def parse_uploaded_file(self, f):
        self.soup = BeautifulSoup(f.read())

        lap = self.soup.find('lap')

        self.datetime = datetime.datetime.strptime(lap['start'].split("+")[0], "%Y-%m-%dT%H:%M:%S")
        self.start_time = self.datetime.time()
        self.date = self.datetime.date()
        self.cur_time = self.datetime
        self.cur_distance = 0.0
        self.duration = "%sh %sm %ss" % tuple(lap['duration'].split(".")[0].split(":"))
        self.distance_sum = float(lap['distance'])

        self.max_speed = float(lap.max_speed.string)*3.6
        self.max_hr = int(lap.max_hr.string)
        self.avg_hr = int(lap.avg_hr.string)
        self.kcal_sum = int(lap.calories.string)

        points = self.soup.findAll('point')

        for point in points:
            time = datetime.datetime.strptime(point['time'].split("+")[0], "%Y-%m-%dT%H:%M:%S")
            if point.has_key('distance'):
                interval = float(point['distance']) - self.cur_distance
                timedelta = (time - self.cur_time).seconds
                if timedelta == 0:
                    speed = 0
                else:
                    speed = interval * 3.6 / timedelta
            else:
                speed = 0.0
            cadence = 0 # not supported yet
            self.cur_time = time
            if point.has_key('distance'):
                self.cur_distance = float(point['distance'])
            if point.has_key('hr'):
                point['hr'] = int(point['hr'])
            else:
                point['hr'] = 0
            if point.has_key('alt'):
                point['alt'] = float(point['alt'])
            else:
                point['alt'] = 0.0
            if point.has_key('lon'):
                point['lon'] = float(point['lon'])
            else:
                point['lon'] = 0
            if point.has_key('lat'):
                point['lat'] = float(point['lat'])
            else:
                point['lat'] = 0
            e = GMDEntry(time, point['hr'], speed, cadence, point['alt'], point['lon'], point['lat'], self.cur_distance)
            self.entries.append(e)

if __name__ == '__main__':
    import sys
    p = GMDParser()
    f = open(sys.argv[1])
    p.parse_uploaded_file(f)

    for ent in p.entries:
        print ent

    print p
