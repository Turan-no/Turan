#!/usr/bin/env python
import datetime

class HRMEntry(object):

    def __init__(self, time, hr, speed, cadence, altitude, power):
        self.time = time
        self.hr = hr
        self.speed = speed
        self.cadence = cadence
        self.altitude = altitude
        self.lat = 0 #not supported by hrm shit
        self.lon = 0 #not supported by hrm shit
        self.power = power

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
                    if self.smode == '111111100':
                        try:
                            hr, speed, cadence, altitude, power, wat = line.split('\t')
                        except ValueError:
                            #garbled data
                            continue
                    elif self.smode == '111000100':
                        hr, speed, cadence, altitude = line.split('\t')
                    elif self.smode == '110000100':
                        hr, speed, cadence = line.split('\t')
                        altitude = 0
                    elif self.smode == '001000100':
                        hr, altitude = line.split('\t')
                        speed, cadence = 0, 0
                    elif self.smode == '011000100':
                        hr, cadence, altitude = line.split('\t')
                        speed = 0
                    elif self.smode == '101000100':
                        hr, speed, altitude = line.split('\t')
                        cadence = 0
                    elif self.smode == '010000100':
                        hr, cadence = line.split('\t')
                        speed, altitude = 0, 0
                    elif self.smode == '000000000':
                        hr = line.strip()
                        speed, altitude, cadence = 0, 0, 0
                    elif self.smode == '000000100':
                        hr = line.strip()
                        speed, altitude, cadence = 0, 0, 0
                    elif self.smode == '100000100':
                        hr, speed = line.split('\t')
                        altitude, cadence = 0, 0
                    elif self.smode == '110111100':
                        hr, speed, cadence, power, wat = line.split('\t')
                        altitude = 0
                    else:
                        assert False, "Unknown smode (combination of sensors), please contact admins"

                    hr = int(hr)
                    speed = float(speed)/10
                    cadence = int(cadence)
                    altitude = int(altitude)
                    power = int(power)

                    self.power_sum += power
                    self.max_power = max(power, self.max_power)

                    self.hr_sum += hr
                    if hr > self.max_hr:
                        self.max_hr = hr

                    self.speed_sum += speed
                    if speed > self.max_speed:
                        self.max_speed = speed

                    self.cadence_sum += cadence
                    if cadence > self.max_cadence:
                        self.max_cadence = cadence

                    if cadence > 0:
                        self.pedaling_cad += cadence*self.interval
                        self.pedaling_cad_seconds += self.interval

                    if power > 0:
                        self.pedaling_power += power*self.interval
                        self.pedaling_power_seconds += self.interval


                    time = datetime.datetime(self.date.year, self.date.month, self.date.day, self.start_time.hour, self.start_time.minute, self.start_time.second)
                    time = time + datetime.timedelta(0, self.interval*i)
                    self.entries.append(HRMEntry(time, hr, speed, cadence, altitude, power))
                    i += 1
            elif lapstarted:
                laprow += 1
                if laprow == 4:
                    splitted = line.split('\t')
                    self.temperature = float(splitted[3])/10
                    lapstarted = False # reset state
            elif notestarted:
                self.comment = line.strip().decode('ISO-8859-1')
                notestarted = False # reset state
            elif line.startswith('[IntTimes]'): #IntTimes = GoodTimes ?
                lapstarted = True
            elif line.startswith('Date'):
                year, date, month = int(line[5:9]), int(line[9:11]), int(line[11:13])
                self.date = datetime.date(year, date, month)
            elif line.startswith('StartTime'):
                hour, minute, second = int(line[10:12]), int(line[13:15]), int(line[16:18])
                self.start_time = datetime.time(hour, minute, second)
            elif line.startswith('Interval'):
                self.interval = int(line.split("=")[1])
            elif line.startswith('[HRData]'):
                hrstarted = True
            elif line.startswith('[Note]'):
                notestarted = True
            elif line.startswith('SMode'):
                self.smode = line[6:].strip()
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
        self.distance_sum = self.interval*len(self.entries) * self.avg_speed/3.6


if __name__ == '__main__':

    import pprint
    import sys
    h = HRMParser()
    h.parse_uploaded_file(file(sys.argv[1]))

    #for x in h.entries:
    #    print x.time, x.speed, x.altitude, x.hr, x.cadence

    print "avg hr, avg speed, avg cadence"
    print h.avg_hr, h.avg_speed, h.avg_cadence
    print "max hr, max speed, max cadence"
    print h.max_hr, h.max_speed, h.max_cadence
    print "temp"
    print h.temperature

    print h.avg_hr, h.avg_speed, h.avg_cadence, h.avg_pedaling_cad
    print h.max_hr, h.max_speed, h.max_cadence
    print "Distance:", h.distance_sum
