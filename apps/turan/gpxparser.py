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

class GPXParser(object):
    start_lon = 0.0
    start_lat = 0.0

    end_lon = 0.0
    end_lat = 0.0

    entries = []
    distance = 0.0
    ascent = 0.0
    descent = 0.0
    max_speed = 0
    avg_speed = 0
    max_hr = 0 # Fixme
    avg_hr = 0 # Fixme
    avg_cadence = 0 # Fixme
    max_cadence = 0 # Fixme
    kcal_sum = 0
    # comment = '' Fixme

    def parse_uploaded_file(self, fileame):
        ''' Not used in this class '''
        pass

    def __init__(self, filename):
        doc = ET.parse(filename)
        root = doc.getroot()
        ns = root.tag[:-3]

        for trk in root.findall(ns + 'trk'):
            trksegs = trk.find(ns + 'trkseg')
            trkpts = trksegs.findall(ns + 'trkpt')
            for trkpt in trkpts:
                lat = float(trkpt.attrib['lat'])
                lon = float(trkpt.attrib['lon'])
                #try:
                ele = float(trkpt.find(ns + 'ele').text)
                #except:
                #    ele = None

                speed = 0
                tstring = trkpt.find(ns + 'time').text
                time = datetime.datetime(*map(int, tstring.replace("T","-").replace(":","-").strip("Z").split("-")))

                if self.entries:
                    this_distance = proj_distance(self.entries[-1]['lat'],
                            self.entries[-1]['lon'],
                            lat,
                            lon,
                            self.entries[-1]['altitude'],
                            ele)
                    self.distance += this_distance
                    if ele and self.entries[-1]['altitude']:
                        delta_ele = ele - self.entries[-1]['altitude']
                        if delta_ele > 0.0:
                            self.ascent = self.ascent + delta_ele
                        else:
                            self.descent = self.descent + delta_ele
                    speed = 3.6 * this_distance/(time - self.entries[-1]['time']).seconds

                e_dict = {
                    'time':time,
                    'lon': lon ,
                    'lat': lat,
                    'altitude': ele,
                    }
                e_dict['speed'] = speed
                self.avg_speed += speed
                self.max_speed = max(self.max_speed, speed)

                self.entries.append(e_dict)

        if self.entries:

            self.start_lon = self.entries[0]['lon']
            self.start_lat = self.entries[0]['lat']

            self.end_lon = lon
            self.end_lat = lat

            # Turan likes distance in km
            #self.distance = self.distance/1000
            self.distance_sum = self.distance
            self.avg_speed = self.avg_speed/len(self.entries)
            s_t = self.entries[0]['time']
            self.start_time = datetime.time(s_t.hour, s_t.minute, s_t.second)
            self.duration = '%ss' %((self.entries[-1]['time'] - s_t).seconds)
            self.date = datetime.date(s_t.year, s_t.month, s_t.day)


if __name__ == '__main__':
    import sys
    filename = sys.argv[1]
    g = GPXParser(filename)
    print g.start_lon, g.start_lat, g.end_lon, g.end_lat

    for e in g.entries:
        if 'speed' in e and 'altitude' in e:
            print e['time'], e['lon'], e['lat'], e['altitude'], e['speed']
        else:
            print e['time'], e['lon'], e['lat']
    print 'distance: ', g.distance
    print 'ascent: ', g.ascent
    print 'descent: ', g.descent


