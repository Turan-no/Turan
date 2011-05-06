#!/usr/bin/env python
# -*- coding: UTF-8
#

''' This file will need a list of object that have following properties:

    * time
    * lon
    * lat
    * altitude

    Since the objects doesn't know about GPS signal quality the writer does not write information about it to the xml
    It anonymizes timestamps by default, can be turned off by instanciating with anon_time=False
'''


class GPXWriter(object):

    xml = '''<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.0" creator="Turan.no"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xmlns="http://www.topografix.com/GPX/1/0"
xsi:schemaLocation="http://www.topografix.com/GPX/1/0 http://www.topografix.com/GPX/1/0/gpx.xsd">
<trk>
<trkseg>'''

    def __init__(self, objects, anon_time=True):

        self.anon_time = anon_time


        def point2xmlblock(time, lon, lat, alt):
            if not lon or not lat:
                # Some devices (Garmin!) likes to save 0-points. Skip those.
                return ''
            xmlp = '<trkpt lat="%s" lon="%s">\n' %(lat, lon)
            xmlp+= ' <ele>%.1f</ele>\n' %alt
            timestring = '0001-01-01T00:00:00Z'
            if not self.anon_time:
                timestring = time.strftime('%Y-%m-%dT%H:%M:%SZ')
            xmlp+= ' <time>%s</time>\n' %timestring
            xmlp+= '</trkpt>\n'
            return xmlp

        pointsxml = [point2xmlblock(o.time, o.lon, o.lat, o.altitude) for o in objects]
        self.xml += ''.join(pointsxml)
        self.xml += '''</trkseg>
</trk>
</gpx>'''


