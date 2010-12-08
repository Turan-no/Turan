from xml.etree import ElementTree as ET
from datetime import datetime, timedelta

tp_ns = '{http://www.peaksware.com/PWX/1/0}'

def summary_attrib(summary, attrib, type):
    try:
        summarydata = summary.find(tp_ns + type)
        value = summarydata.attrib[attrib]
    except AttributeError:
        value = 0
    return value

def sample_value(sample, type):
    try:
        value = sample.find(tp_ns + type).text
    except AttributeError:
        value = 0
    return value


class PWXEntry(object):
    def __init__(self, time, hr, speed, cadence, power, torque, temp, altitude, lat, lon):
        self.time = time
        self.hr = hr
        self.speed = speed
        self.cadence = cadence
        self.power = power
        self.torque = torque
        self.temp = temp
        self.altitude = altitude
        self.lon = lon
        self.lat = lat

    def __str__(self):
        return '[%s] hr: %s spd: %s cad %s pwr %s torque: %s temp: %s alt: %s' % (self.time, self.hr, self.speed, self.cadence, self.power, self.torque, self.temp, self.altitude)

class PWXParser(object):
    def __init__(self, gps_distance=False):
        self.entries = []
        self.distance = 0.0
        self.ascent = 0.0
        self.descent = 0.0
        self.max_speed = 0
        self.avg_speed = 0
        self.max_hr = 0
        self.avg_hr = 0
        self.avg_cadence = 0
        self.max_cadence = 0
        self.avg_power = 0
        self.max_power = 0
        self.avg_torque = 0.0
        self.max_torque = 0.0
        self.avg_temp = 0.0
        self.max_temp = 0.0
        self.kcal_sum = 0

    def parse_uploaded_file(self, f):
        doc = ET.parse(f)
        workout = doc.find(tp_ns + "workout")

        start = datetime.strptime(workout.find(tp_ns + "time").text,"%Y-%m-%dT%H:%M:%S")

        self.start_time = start.time()
        self.date = start.date()

        summary = workout.find(tp_ns + "summarydata")
        self.duration = int(summary.find(tp_ns + "duration").text)
        try:
            self.distance = float(summary.find(tp_ns + "dist").text)
        except AttributeError:
            self.distance = 0.0
        self.avg_hr      = int(summary_attrib(summary, "avg", "hr"))
        self.max_hr      = int(summary_attrib(summary, "max", "hr"))
        self.avg_speed   = float(summary_attrib(summary, "avg", "spd"))
        self.max_speed   = float(summary_attrib(summary, "max", "spd"))
        self.avg_cadence = int(summary_attrib(summary, "avg", "cad"))
        self.max_cadence = int(summary_attrib(summary, "max", "cad"))
        self.avg_power   = int(summary_attrib(summary, "avg", "pwr"))
        self.max_power   = int(summary_attrib(summary, "max", "pwr"))
        self.avg_torque  = float(summary_attrib(summary, "avg", "torq"))
        self.max_torque  = float(summary_attrib(summary, "max", "torq"))
        self.avg_temp    = float(summary_attrib(summary, "avg", "temp"))
        self.max_temp    = float(summary_attrib(summary, "max", "temp"))
        self.ascent = float(sample_value(summary, "climbingelevation"))

        samples = workout.getiterator(tp_ns + "sample")
        for sample in samples:
            time = start + timedelta(0, int(sample.find(tp_ns + "timeoffset").text))

            hr     = int(sample_value(sample, "hr"))
            spd    = float(sample_value(sample, "spd"))
            cad    = int(sample_value(sample, "cad"))
            pwr    = int(sample_value(sample, "pwr"))
            torque = float(sample_value(sample, "torq"))
            temp   = float(sample_value(sample, "temp"))
            alt    = float(sample_value(sample, "alt"))
            lat    = float(sample_value(sample, "lat"))
            lon    = float(sample_value(sample, "lon"))
            
            self.entries.append(PWXEntry(time,hr,spd,cad,pwr,torque,temp,alt, lat, lon))

if __name__ == '__main__':
    import pprint
    import sys
    t = PWXParser(0)
    t.parse_uploaded_file(file(sys.argv[1]))

    for pwx_e in t.entries:
        print pwx_e

    print 'start: %s %s - duration: %s' % (t.date, t.start_time, t.duration)
    print 'HR - avg: %s - max: %s' % (t.avg_hr, t.max_hr)
    print 'SPEED - avg: %s - max: %s' % (t.avg_speed, t.max_speed)
    print 'CADENCE - avg: %s - max: %s' % (t.avg_cadence, t.max_cadence)
    print 'POWER - avg: %s - max: %s' % (t.avg_power, t.max_power)
    print 'TORQUE - avg: %s - max: %s' % (t.avg_torque, t.max_torque)
    print 'TEMP - avg: %s - max: %s' % (t.avg_temp, t.max_temp)
