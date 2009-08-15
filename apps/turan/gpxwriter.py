#!/usr/bin/env python
# -*- coding: UTF-8
#

''' This file will need a list of object that has following properties:

    * time
    * lon
    * lat
    * altitude
    
    Since the objects doesn't know about GPS signal quality the writer does not write information about it to the xml
'''


class GPXWriter(object):

    xml = '''<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.0" creator="Turan.lart.no"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xmlns="http://www.topografix.com/GPX/1/0"
xsi:schemaLocation="http://www.topografix.com/GPX/1/0 http://www.topografix.com/GPX/1/0/gpx.xsd">
<trk>
<trkseg>'''


    def __init__(self, objects):

        def point2xmlblock(time, lon, lat, alt):
            xmlp = '<trkpt lat="%s" lon="%s">\n' %(lat, lon)
            xmlp+= ' <time>%s</time>\n' %time.strftime('%Y-%m-%dT%H:%M:%SZ')
            xmlp+= ' <ele>%.1f</ele>\n' %alt
            xmlp+= '</trkpt>\n'
            return xmlp

        for o in objects:
            self.xml += point2xmlblock(o.time, o.lon, o.lat, o.altitude)

        self.xml += '''</trkseg>
</trk>
</gpx>'''


