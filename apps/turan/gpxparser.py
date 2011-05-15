from xml.etree import ElementTree as ET
import datetime
import pyproj
from math import hypot
geod = pyproj.Geod(ellps='WGS84')

def proj_distance(lat1, lon1, lat2, lon2, elev1=None, elev2=None):
    try:
        hdelta = geod.inv(lon2, lat2, lon1, lat1)[2]
        if elev1 and elev2:
            distdelta = hypot(hdelta, elev1-elev2)
        else:
            distdelta = hdelta
        return distdelta
    except ValueError:
        return 0.0

class GPXEntry(object):

    def __init__(self, time, hr, speed, cadence, altitude, lon, lat, distance):
        self.time = time
        self.hr = hr
        self.speed = speed
        self.cadence = cadence
        if not altitude:
            altitude = 0
        self.altitude = altitude
        self.lat = lat
        self.lon = lon
        self.distance = distance

class GPXParser(object):

    def val_or_none(self, item, val, return_zero=False):
        ''' Return value if found or none if not. makes it easier to deal with
        missing elements in xml'''
        try:
            e = item.find(self.ns + val)
            return float(e.text)
        except ValueError:
            if return_zero:
                return 0
            return None # missing element
        except AttributeError:
            if return_zero:
                return 0
            return None # missing element

    def __init__(self, filename=None):
        self.garmin_ns = '{http://www.garmin.com/xmlschemas/TrackPointExtension/v1}'
        self.start_lon = 0.0
        self.start_lat = 0.0

        self.end_lon = 0.0
        self.end_lat = 0.0

        self.entries = []
        self.laps = []
        self.distance = 0.0
        self.ascent = 0.0
        self.descent = 0.0
        self.max_speed = 0
        self.avg_speed = 0
        self.max_hr = 0
        self.avg_hr = 0
        self.avg_cadence = 0
        self.max_cadence = 0
        self.kcal_sum = 0
        # self.comment = '' Fixme
        if filename:
            self.parse_uploaded_file(filename)

    def parse_uploaded_file(self, filename):
        if self.entries: # Do not parse again if sent filename in constructor
            return

        try:
            doc = ET.parse(filename)
        except:
            # mongofil
            return
        root = doc.getroot()
        ns = root.tag[:-3]
        self.ns = ns

        # http://en.wikipedia.org/wiki/Dilution_of_precision_(GPS)
        vdop_cutoff = 30
        hdop_cutoff = 90

        for trk in root.findall(ns + 'trk'):
            trksegs = trk.findall(ns + 'trkseg')
            for trkseg in trksegs:
                trkpts = trkseg.findall(ns + 'trkpt')
                for trkpt in trkpts:
                    lat = float(trkpt.attrib['lat'])
                    lon = float(trkpt.attrib['lon'])
                    ele = self.val_or_none(trkpt, 'ele')
                    vdop = self.val_or_none(trkpt, 'vdop')
                    hdop = self.val_or_none(trkpt, 'hdop')
                    if vdop > vdop_cutoff:
                        # If accurarcy is low, use previous sample
                        if self.entries:
                            ele = self.entries[-1].altitude
                    if hdop > hdop_cutoff:
                        # If accurarcy is low, use previous sample
                        if self.entries:
                            lat = self.entries[-1].lat
                            lon = self.entries[-1].lon

                    speed = self.val_or_none(trkpt, 'speed', return_zero=True)
                    try:
                        tstring = trkpt.find(ns + 'time').text
                    except AttributeError:
                        # maybe stupid garmin format with multiple trkseg, one without time. skip skip
                        continue
                    if '+' in tstring:
                        tstring = tstring[0:tstring.index('+')]
                    tstringtemp = tstring.replace("T","-").replace(":","-").strip("Z\n ").split("-")
                    time = datetime.datetime(*map(int, map(float, tstringtemp)))

                    # extensions (hr)
                    hr = 0
                    try:
                        hr_ele = trkpt.find('.//' +self.garmin_ns + 'hr')
                        hr = int(hr_ele.text)
                        self.avg_hr += hr
                        self.max_hr = max(hr, self.max_hr)
                    except AttributeError:
                        pass # no hr in file
                    # extensions (cadence)
                    cad = 0
                    try:
                        cad_ele = trkpt.find('.//' +self.garmin_ns + 'cad')
                        cad = int(cad_ele.text)
                        self.avg_cadence += cad
                        self.max_cadence = max(cad, self.max_cadence)
                    except AttributeError:
                        pass # no hr in file

                    if self.entries:
                        this_distance = proj_distance(self.entries[-1].lat,
                                self.entries[-1].lon,
                                lat,
                                lon,
                                self.entries[-1].altitude,
                                ele)
                        self.distance += this_distance
                        if ele and self.entries[-1].altitude:
                            delta_ele = ele - self.entries[-1].altitude
                            if delta_ele > 0.0:
                                self.ascent = self.ascent + delta_ele
                            else:
                                self.descent = self.descent + delta_ele
                        if not speed and this_distance:
                            time_d = (time - self.entries[-1].time).seconds
                            if time_d:
                                speed = 3.6 * this_distance/time_d

                    e = GPXEntry(time, hr, speed, cad, ele, lon, lat, self.distance)
                    self.avg_speed += speed
                    self.max_speed = max(self.max_speed, speed)

                    self.entries.append(e)

        if self.entries:

            self.start_lon = self.entries[0].lon
            self.start_lat = self.entries[0].lat

            self.end_lon = self.entries[-1].lon
            self.end_lat = self.entries[-1].lat

            # Turan likes distance in km
            #self.distance = self.distance/1000
            self.distance_sum = self.distance
            self.avg_speed = self.avg_speed/len(self.entries)
            if self.avg_hr:
                self.avg_hr = self.avg_hr/len(self.entries)
            if self.avg_cadence:
                self.avg_cadence = self.avg_cadence/len(self.entries)
            s_t = self.entries[0].time
            self.start_time = datetime.time(s_t.hour, s_t.minute, s_t.second)
            self.duration = '%ss' %((self.entries[-1].time - s_t).seconds)
            self.date = datetime.date(s_t.year, s_t.month, s_t.day)




if __name__ == '__main__':
    import sys
    filename = sys.argv[1]
    g = GPXParser(filename)
    print g.start_lon, g.start_lat, g.end_lon, g.end_lat

    for e in g.entries:
        #if 'speed' in e and 'altitude' in e:
        print e.time, e.lon, e.lat, e.altitude, e.speed, e.distance
        #else:
        #    print e['time'], e['lon'], e['lat']
    print 'distance: ', g.distance
    print 'ascent: ', g.ascent
    print 'descent: ', g.descent
    print 'avg_hr: ', g.avg_hr
    print 'avg_cadence: ', g.avg_cadence
    print 'avg_speed: ', g.avg_speed


