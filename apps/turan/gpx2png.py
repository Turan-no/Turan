#!/usr/bin/python

from xml.etree import ElementTree as ET
import math
import Image, ImageDraw
from cStringIO import StringIO



class GPX2PNG(object):
    maxele = 0
    minele = 0
    maxlat = 0
    minlat = 0
    maxlon = 0
    minlon = 0
    path = []
    image = None

    def __init__(self, filename, xsize=64, ysize=64):
        self.image = Image.new("RGBA", (xsize,ysize))
        self.draw = ImageDraw.Draw(self.image)

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
                ele = trkpt.find(self.ns + 'ele')

                if first:
                    self.minlat = lat
                    self.minlon = lon
                    self.laxlat = lat
                    self.maxlon = lon
                    if ele is not None:
                        self.minele = float(ele.text)
                        self.maxele = float(ele.text)
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
                    if ele is not None:
                        self.minele = min(float(ele.text), self.minele)
                        self.maxele = max(float(ele.text), self.maxele)


        yscale = -math.cos( (self.minlat + self.maxlat) / 2 / 180 * 3.141592 )

        for trk in self.root.findall(self.ns + 'trk'):
            first = True
            lat = 0
            lon = 0
            oldx = 0
            oldy = 0
            first = True

            trksegs = trk.find(self.ns + 'trkseg')
            trkpts = trksegs.findall(self.ns + 'trkpt')
            for trkpt in trkpts:
                lat = float(trkpt.attrib['lat'])
                lon = float(trkpt.attrib['lon'])
                ele = trkpt.find(self.ns + 'ele')

                x = (lon - self.minlon) / (self.maxlon - self.minlon) * xsize
                y = xsize+ ((lat - self.minlat) / (self.maxlat - self.minlat) * xsize * yscale)
                if first:
                    oldx = x
                    oldy = y
                    first = False
                    continue

                if ele is not None:
                    i = int((float(ele.text) - self.minele) / (self.maxele - self.minele) * 255)
                else:
                    i = 0
                self.draw.line((oldx, oldy, x, y), fill="rgb(%d,%d,%d)" % (i, 255-i, 255))
                oldx = x
                oldy = y

    def get_file(self):
        f = StringIO()
        self.image.save(f, "PNG")
        f.seek(0)
        return f


if __name__ == '__main__':
    import sys
    g = GPX2PNG(sys.argv[1])
    open("../../site_media/test.png", "w+").write(g.get_file().read())

