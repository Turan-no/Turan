from xml.etree import ElementTree as ET
import datetime

class GPXParser(object):
    start_lon = 0.0
    start_lat = 0.0

    end_lon = 0.0
    end_lat = 0.0

    entries = []

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

                tstring = trkpt.getchildren()[0].text
                time = datetime.datetime(*map(int, tstring.replace("T","-").replace(":","-").strip("Z").split("-")))

                if not self.start_lon:
                    self.start_lon = lon
                    self.start_lat = lat

                self.entries.append( {
                    'time':time,
                    'lon': lon ,
                    'lat': lat,
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


