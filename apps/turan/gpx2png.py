#!/usr/bin/python

from xml.etree import ElementTree as ET
import math
import Image, aggdraw
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
        self.draw = aggdraw.Draw(self.image)

        try:
            doc = ET.parse(filename)
            self.root = doc.getroot()
            self.ns = self.root.tag[:-3]
        except ET.ParseError, e:
            return None

        first = True
        if hasattr(self, 'root'):
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
            # Sanity check before drawing
            if yscale != 0 and self.minlon != self.maxlon and self.minlat != self.maxlat and self.minele != self.maxele:
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
                            p = aggdraw.Pen("rgb(%d,%d,%d)" % (i, 0, 0), 2.0)
                            self.draw.line((oldx, oldy, x, y), p)
                        else:
                            p = aggdraw.Pen("black", 2.0)
                            self.draw.line((oldx, oldy, x, y), p)

                        oldx = x
                        oldy = y

                    self.draw.flush()

    def get_file(self):
        f = StringIO()
        self.image.save(f, "PNG")
        f.seek(0)
        return f


if __name__ == '__main__':
    import sys
    g = GPX2PNG(sys.argv[1])
    open("../../site_media/test.png", "w+").write(g.get_file().read())

