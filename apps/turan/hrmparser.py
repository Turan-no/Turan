#!/usr/bin/env python
import datetime

''' This module will parse a HRMfile into a Turan datastructure

    http://www.polar.fi/files/Polar_HRM_file%20format.pdf
'''


class HRMEntry(object):

    def __init__(self, time, hr, speed, cadence, altitude, power, distance):
        self.time = time
        self.hr = hr
        self.speed = speed
        self.cadence = cadence
        self.altitude = altitude
        self.lat = 0 #not supported by hrm shit
        self.lon = 0 #not supported by hrm shit
        self.power = power
        self.distance = distance

    def __str__(self):
        return '[%s] hr: %s spd: %s cad: %s pwr: %s alt: %s distance: %s' % (self.time, self.hr, self.speed, self.cadence, self.power, self.altitude, self.distance)

class HRMLap(object):

    def __init__(self, time, duration, min_hr, max_hr, avg_hr):
        self.start_time = time
        self.duration = duration
        self.max_hr = max_hr
        self.avg_hr = avg_hr
        self.min_hr = min_hr

    def __str__(self):
        return '[%s] duration: %s distance: %s' % (self.start_time, self.duration, self.distance)

class HRMParser(object):

    def __init__(self):
        self.entries = []
        self.laps = []

        self.start_time = 0
        self.date = 0
        self.interval = 0
        self.duration = 0
        self.temperature = 0

        self.smode = 0 # Polar specific mode (sensor mode)

        self.max_hr = 0
        self.max_speed = 0
        self.max_cadence = 0
        self.max_power = 0

        self.hr_sum = 0
        self.speed_sum = 0
        self.cadence_sum = 0
        self.distance_sum = 0
        self.kcal_sum = 0
        self.power_sum = 0
        self.pedaling_cad_seconds = 0
        self.pedaling_cad = 0
        self.pedaling_power = 0
        self.pedaling_power_seconds = 0

        self.comment = ''


    def parse_uploaded_file(self, f):

        i = 0
        laprow = 0
        hrstarted = False
        lapstarted = False
        notestarted = False
        for line in f:
            if hrstarted:
                line = line.strip()
                power = 0
                if line:
                    values = {}
                    if self.smodes:
                        try:
                            data = line.split('\t')
                            for index, value in enumerate(data):
                                values[self.smodes[index]] = value
                            # print values
                        except ValueError:
                            continue
                        hr = values['hr']
                        if 'speed' in values:
                            speed = values['speed']
                        if 'cadence' in values:
                            cadence = values['cadence']
                        if 'altitude' in values:
                            altitude = values['altitude']
                        if 'power' in values:
                            power = values['power']

                    hr = int(hr)
                    # TODO! Support for mph!
                    speed = float(speed)/10
                    cadence = int(cadence)
                    altitude = int(altitude)
                    power = int(power)
                    distance = 0

                    self.power_sum += power
                    self.max_power = max(power, self.max_power)

                    self.hr_sum += hr
                    if hr > self.max_hr:
                        self.max_hr = hr

                    self.speed_sum += speed
                    if speed > self.max_speed:
                        self.max_speed = speed

                    if speed:
                        self.distance_sum += speed/3.6*self.interval
                        distance = self.distance_sum

                    self.cadence_sum += cadence
                    if cadence > self.max_cadence:
                        self.max_cadence = cadence

                    if cadence > 0:
                        self.pedaling_cad += cadence*self.interval
                        self.pedaling_cad_seconds += self.interval

                    if power > 0:
                        self.pedaling_power += power*self.interval
                        self.pedaling_power_seconds += self.interval


                    time = self.time + datetime.timedelta(0, self.interval*i)
                    self.entries.append(HRMEntry(time, hr, speed, cadence, altitude, power, distance))
                    i += 1
            elif lapstarted:
                laprow += 1
                splitted = line.strip().split('\t')
                if not len(splitted) > 1:
                    # Lap Section Done
                    lapstarted = False # reset state
                else:
                    if laprow == 1: # New lap
                        time, hr, min_hr, max_hr, avg_hr = splitted[:]
                        hours, minutes, seconds = time.split(':')
                        hours, minutes, seconds = int(hours), int(minutes), float(seconds) # FIXME microseconds
                        seconds_after_start = (int(int(hours)*3600 + (int(minutes)*60) + float(seconds))) # FIXME support for microseconds
                        time = self.time + datetime.timedelta(0, seconds_after_start)
                        if self.laps:
                            duration = (time - self.laps[-1].start_time).seconds
                        else: # first lap
                            duration = seconds_after_start
                        self.laps.append(HRMLap(time, duration, min_hr, max_hr, avg_hr))
                    elif laprow == 2:
                        wut, wut, wut, speed, cadence, altitude = splitted[:]
                        speed = float(speed)/10
                        cadence = int(cadence)
                        altitude = int(altitude)
                    elif laprow == 4:
                        lap_type, distance, power, temperature, phrase_lap, air_pressure = splitted[:]
                        temperature = float(temperature)/10
                        distance = float(distance)
                        self.laps[-1].avg_temp = temperature
                        self.laps[-1].distance = distance
                        self.temperature = temperature
                    elif laprow == 5:
                        laprow = 0 # reset lap counter
            elif notestarted:
                self.comment = line.strip().decode('ISO-8859-1')
                notestarted = False # reset state
            elif line.startswith('[IntTimes]'): #IntTimes = GoodTimes ?
                lapstarted = True
            elif line.startswith('Date'):
                year, date, month = int(line[5:9]), int(line[9:11]), int(line[11:13])
                self.date = datetime.date(year, date, month)
            elif line.startswith('StartTime'):
                #hour, minute, second = int(line[10:12]), int(line[13:15]), int(line[16:18])
                parts = line.split(':')
                hour = int(parts[0].split('=')[1])
                minute = int(parts[1])
                second = int(parts[2].split('.')[0]) # fixme millisecond
                self.start_time = datetime.time(hour, minute, second)
                self.time = datetime.datetime(self.date.year, self.date.month, self.date.day, \
                        self.start_time.hour, self.start_time.minute, self.start_time.second)
            elif line.startswith('Interval'):
                self.interval = int(line.split("=")[1])
            elif line.startswith('[HRData]'):
                hrstarted = True
            elif line.startswith('[Note]'):
                notestarted = True
            elif line.startswith('Version'):
                self.file_version = line[8:].strip()
            elif line.startswith('SMode'):
                self.smodes = []
                self.smode = line[6:].strip()
                self.smodes.append('hr')
                if (self.file_version == '106') or (self.file_version == '107'):
                    if self.smode[0] == '1':
                        self.smodes.append('speed')
                    if self.smode[1] == '1':
                        self.smodes.append('cadence')
                    if self.smode[2] == '1':
                        self.smodes.append('altitude')
                    if self.smode[3] == '1':
                        self.smodes.append('power')
                    if self.smode[4] == '1':
                        self.smodes.append('powerbal')
                    if self.smode[7] == '1':
                        self.kph_mph = 'mph'
                    else:
                        self.kph_mph = 'kph'
                else:
                    if self.smode[0] == '0':
                        self.smodes.append('cadence')
                    if self.smode[0] == '1':
                        self.smodes.append('altitude')
                    if self.smode[2] == '1':
                        self.kph_mph = 'mph'
                    else:
                        self.kph_mph = 'kph'
                if self.file_version == '107':
                    if self.smode[8] == '1':
                        self.smodes.append('airpress')
                        
            elif line.startswith('Length'):
                hours, minutes, seconds = line.strip().split('=')[1].split(':')
                #hours = line[7:9]
                #minutes = line[10:12]
                #seconds = line[13:]
                self.duration = '%ss' %(int(int(hours)*3600 + (int(minutes)*60) + float(seconds))) # FIXME support for microseconds
                #self.duration = '%sh %sm %ss' % (hours, minutes, seconds)

        self.avg_power = self.power_sum/len(self.entries)
        self.avg_hr = self.hr_sum/len(self.entries)
        self.avg_speed = self.speed_sum/len(self.entries)
        self.avg_cadence = self.cadence_sum/len(self.entries)
        if self.pedaling_cad and self.pedaling_cad_seconds:
            self.avg_pedaling_cad = self.pedaling_cad/self.pedaling_cad_seconds
        if self.pedaling_power and self.pedaling_power_seconds:
            self.avg_pedaling_power = self.pedaling_power/self.pedaling_power_seconds
        #self.distance_sum = self.interval*len(self.entries) * self.avg_speed/3.6


if __name__ == '__main__':

    import pprint
    import sys
    h = HRMParser()
    h.parse_uploaded_file(file(sys.argv[1]))

    for x in h.entries:
        print x.time, x.speed, x.altitude, x.hr, x.cadence, x.distance

    print "avg hr, avg speed, avg cadence"
    print h.avg_hr, h.avg_speed, h.avg_cadence
    print "max hr, max speed, max cadence"
    print h.max_hr, h.max_speed, h.max_cadence
    print "temp"
    print h.temperature

    print h.avg_hr, h.avg_speed, h.avg_cadence
    print h.max_hr, h.max_speed, h.max_cadence
    print "Distance:", h.distance_sum
    if h.laps:
        print "Laps:"
        for lap in h.laps:
            print lap
