#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""Parser for PowerTap .csv """

import csv
from datetime import time, timedelta, datetime

# end slurp
#

class CSVEntry(object):

    def __init__(self, time, hr, speed, cadence, power):
        self.time = time
        self.hr = hr
        self.speed = speed
        self.cadence = cadence
        self.altitude = 0 # not in this format
        self.power = power
        self.lat = 0 # not in this format
        self.lon = 0 # not in this format

class CSVParser(object):
    entries = []
    duration = 0
    start_time = time(0,0,0)
    now = datetime.now()
    date = datetime(now.year, now.month, now.day)

    max_hr = 0
    max_speed = 0
    max_cadence = 0
    max_power = 0

    hr_sum = 0
    speed_sum = 0
    cadence_sum = 0
    distance_sum = 0
    kcal_sum = 0
    power_sum = 0

    def parse_uploaded_file(self, f):

        source = csv.reader(f)
        for i, row in enumerate(source):
            if i == 0: continue # first line is columns
            #['Minutes', 'Torq (N-m)', 'Km/h', 'Watts', 'Km', 'Cadence', 'Hrate', 'ID']
            #['0.021', '', '3.7', '0', '0.008', '0', '', '0']
            #['0.042', '', '', '0', '0.008', '0', '', '0']

            minutes, torq, speed, power, distance, cadence, hr, id = [x.strip() for x in row]

            if hr:
                hr = int(hr)
            else:
                hr = 0
            if speed:
                speed = float(speed)
            else:
                speed = 0
            power = int(power)
            distance = float(distance)
            cadence = int(cadence)

            seconds = int(float(minutes)*60)
            n_time = self.date + timedelta(0, seconds)
   
            self.entries.append(CSVEntry(n_time, hr, speed, cadence, power))

            self.hr_sum += hr
            if hr > self.max_hr:
                self.max_hr = hr

            self.speed_sum += speed
            if speed > self.max_speed:
                self.max_speed = speed

            self.cadence_sum += cadence
            if cadence > self.max_cadence:
                self.max_cadence = cadence

            self.power_sum += power
            self.max_power = max(power, self.max_power)

        self.avg_hr = self.hr_sum/len(self.entries)
        self.avg_speed = self.speed_sum/len(self.entries)
        self.avg_cadence = self.cadence_sum/len(self.entries)
        self.avg_power = self.power_sum/len(self.entries)
        # Get duration from last sample
        self.duration =  '%ss' %seconds



if __name__ == "__main__":
    import pprint
    import sys

    c = CSVParser()
    c.parse_uploaded_file(file(sys.argv[1]))

    for x in c.entries:
        print x.time, x.speed, x.power, x.hr, x.cadence

    print c.avg_hr, c.avg_speed, c.avg_cadence, c.avg_power
    print c.max_hr, c.max_speed, c.max_cadence, c.max_power

    print c.duration
