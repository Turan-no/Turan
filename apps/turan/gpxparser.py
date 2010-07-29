from xml.etree import ElementTree as ET
import datetime
import pyproj
from math import hypot

class GPXParser(object):
    start_lon = 0.0
    start_lat = 0.0

    end_lon = 0.0
    end_lat = 0.0

    entries = []
    distance = 0.0
    ascent = 0.0
    descent = 0.0
    geod = pyproj.Geod(ellps='WGS84')

    def __proj_distance(self, lat1, lon1, lat2, lon2, elev1=None, elev2=None):
        try:
            hdelta = self.geod.inv(lon2, lat2, lon1, lat1)[2]
            if elev1 and elev2:
                distdelta = hypot(hdelta, elev1-elev2)
            else:
                distdelta = hdelta
            return distdelta
        except ValueError:
            return 0.0

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
                try:
                    ele = float(trkpt.find(ns + 'ele').text)
                except:
                    ele = None

                if(len(self.entries) > 0):
                    self.distance = self.distance + self.__proj_distance(self.entries[-1]['lat'],
                            self.entries[-1]['lon'],
                            lat,
                            lon,
                            self.entries[-1]['ele'],
                            ele)
                    if ele and self.entries[-1]['ele']:
                        delta_ele = ele - self.entries[-1]['ele']
                        if delta_ele > 0.0:
                            self.ascent = self.ascent + delta_ele
                        else:
                            self.descent = self.descent + delta_ele


                tstring = trkpt.find(ns + 'time').text
                time = datetime.datetime(*map(int, tstring.replace("T","-").replace(":","-").strip("Z").split("-")))

                if not self.start_lon:
                    self.start_lon = lon
                    self.start_lat = lat

                self.entries.append( {
                    'time':time,
                    'lon': lon ,
                    'lat': lat,
                    'ele': ele,
                    })

            self.end_lon = lon
            self.end_lat = lat


if __name__ == '__main__':
    import sys
    filename = sys.argv[1]
    g = GPXParser(filename)
    print g.start_lon, g.start_lat, g.end_lon, g.end_lat

    for e in g.entries:
        print e['time'], e['lon'], e['lat']
    print 'distance: ', g.distance
    print 'ascent: ', g.ascent
    print 'descent: ', g.descent


