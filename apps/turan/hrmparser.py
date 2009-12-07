#!/usr/bin/env python
import datetime

class HRMEntry(object):

    def __init__(self, time, hr, speed, cadence, altitude):
        self.time = time
        self.hr = hr
        self.speed = speed
        self.cadence = cadence
        self.altitude = altitude
        self.lat = 0 #not supported by hrm shit
        self.lon = 0 #not supported by hrm shit

class HRMParser(object):

    entries = []
    start_time = 0
    date = 0
    interval = 0
    duration = 0
    temperature = 0

    smode = 0 # Polar specific mode (sensor mode)

    max_hr = 0
    max_speed = 0
    max_cadence = 0

    hr_sum = 0
    speed_sum = 0
    cadence_sum = 0
    distance_sum = 0
    kcal_sum = 0

    comment = ''


    def parse_uploaded_file(self, f):

        i = 0
        laprow = 0
        hrstarted = False
        lapstarted = False
        notestarted = False
        for line in f.readlines():
            if hrstarted:
                line = line.strip()
                if line:
                    if self.smode == '111000100':
                        hr, speed, cadence, altitude = line.split('\t')
                    elif self.smode == '110000100':
                        hr, speed, cadence = line.split('\t')
                        altitude = 0
                    elif self.smode == '001000100':
                        hr, altitude = line.split('\t')
                        speed, cadence = 0, 0
                    elif self.smode == '101000100':
                        hr, speed, altitude = line.split('\t')
                        cadence = 0
                    elif self.smode == '000000000':
                        hr = line.strip()
                        speed, altitude, cadence = 0, 0, 0
                    else:
                        assert False, "Unknown smode, please contact admins"

                    hr = int(hr)
                    speed = float(speed)/10
                    cadence = int(cadence)
                    altitude = int(altitude)

                    self.hr_sum += hr
                    if hr > self.max_hr:
                        self.max_hr = hr

                    self.speed_sum += speed
                    if speed > self.max_speed:
                        self.max_speed = speed

                    self.cadence_sum += cadence
                    if cadence > self.max_cadence:
                        self.max_cadence = cadence

                    time = datetime.datetime(self.date.year, self.date.month, self.date.day, self.start_time.hour, self.start_time.minute, self.start_time.second)
                    time = time + datetime.timedelta(0, self.interval*i)
                    self.entries.append(HRMEntry(time, hr, speed, cadence, altitude))
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
                self.interval = int(line[9:10])
            elif line.startswith('[HRData]'):
                hrstarted = True
            elif line.startswith('[Note]'):
                notestarted = True
            elif line.startswith('SMode'):
                self.smode = line[6:].strip()
            elif line.startswith('Length'):
                hours = line[7:9]
                minutes = line[10:12]
                seconds = line[13:15]
                self.duration = '%sh %smin %ss' % (hours, minutes, seconds)

        self.avg_hr = self.hr_sum/len(self.entries)
        self.avg_speed = self.speed_sum/len(self.entries)
        self.avg_cadence = self.cadence_sum/len(self.entries)


if __name__ == '__main__':
    
    import pprint
    import sys
    h = HRMParser()
    h.parse_uploaded_file(file(sys.argv[1]))

    #for x in h.entries:
    #    print x.time, x.speed, x.altitude, x.hr, x.cadence

    print h.avg_hr, h.avg_speed, h.avg_cadence
    print h.max_hr, h.max_speed, h.max_cadence
    print h.temperature

    h.parse_uploaded_file(file(sys.argv[1]))
    print h.avg_hr, h.avg_speed, h.avg_cadence
    print h.max_hr, h.max_speed, h.max_cadence
