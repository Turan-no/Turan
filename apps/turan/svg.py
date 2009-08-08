#!/usr/bin/python

from xml.etree import ElementTree as ET
import math


class GPX2SVG(object):
    xml = '''<?xml version="1.0" standalone="no"?>
    <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" 
    "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">

    <svg width="100%" height="100%" version="1.1"
    xmlns="http://www.w3.org/2000/svg">
    '''
    maxlat = 0
    minlat = 0
    maxlon = 0
    minlon = 0


    def __init__(self, filename, xsize=50):

        doc = ET.parse(filename)
        self.root = doc.getroot()
        self.ns = self.root.tag[:-3]

        first = True
        for trk in self.root.findall(self.ns + 'trk'):
            trksegs = trk.find(self.ns + 'trkseg')
            trkpts = trksegs.findall(self.ns + 'trkpt')
            for trkpt in trkpts:
                lat = float(trkpt.attrib['lat'])
                lon = float(trkpt.attrib['lon'])
                if first:
                  self.minlat = lat
                  self.minlon = lon
                  self.laxlat = lat
                  self.maxlon = lon
                  first = False
                else:
                    if lat < self.minlat:
                      self.minlat = lat
                    if lon < self.minlon:
                      self.minlon = lon
                    if lat > self.maxlat:
                      self.maxlat = lat
                    if lon > self.maxlon:
                      self.maxlon = lon

        yscale = -math.cos( (self.minlat + self.maxlat) / 2 / 180 * 3.141592 )

        for trk in self.root.findall(self.ns + 'trk'):
            first = True
            lat = 0
            lon = 0
            oldx = 0
            oldy = 0

            trksegs = trk.find(self.ns + 'trkseg')
            trkpts = trksegs.findall(self.ns + 'trkpt')
            for trkpt in trkpts:
                lat = float(trkpt.attrib['lat'])
                lon = float(trkpt.attrib['lon'])

                x = (lon - self.minlon) / (self.maxlon - self.minlon) * xsize
                y = xsize+ ((lat - self.minlat) / (self.maxlat - self.minlat) * xsize * yscale)
                if first:
                  self.xml += '<polyline points="%s,%s' %(x, y)
                  first = False
                else:
                  self.xml += "\n,%s,%s" %(x,y)

        self.xml += '" style="fill:white;stroke:black;stroke-width:2"/>'

        self.xml += '</svg>'

if __name__ == '__main__':
    import sys
    g = GPX2SVG(sys.argv[1])
    print g.xml
