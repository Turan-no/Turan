#!/usr/bin/env python
# -*- coding: UTF-8
#

''' This file will need a list of object that have following properties:

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
            if not lon or not lat:
                # Some devices (Garmin!) likes to save 0-points. Skip those.
                return 
            xmlp = '<trkpt lat="%s" lon="%s">\n' %(lat, lon)
            xmlp+= ' <ele>%.1f</ele>\n' %alt
            xmlp+= ' <time>%s</time>\n' %time.strftime('%Y-%m-%dT%H:%M:%SZ')
            xmlp+= '</trkpt>\n'
            return xmlp

        for o in objects:
            xmlblock = point2xmlblock(o.time, o.lon, o.lat, o.altitude)
            if xmlblock:
                self.xml += xmlblock

        self.xml += '''</trkseg>
</trk>
</gpx>'''


