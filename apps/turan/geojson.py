#!/usr/bin/env python
# -*- coding: UTF-8
#
import simplejson


class GeoJSONFeatureCollection(object):

    def __init__(self, features):
        self.res = {
            "type": "FeatureCollection",
            "features": [f.res for f in features]
        }

    def __str__(self):
        ''' Return json '''
        return simplejson.dumps(self.res, separators=(',',':'))

class GeoJSONFeature(object):

    def __init__(self, zone):
        self.lines = []
        self.res = {
          "geometry": {
            "type": "LineString",
            "coordinates": self.lines
           },
          "properties": {
              "ZONE": zone
            },
          "type": "Feature",
        }

    def addLine(self, a, b, c, d):
        ''' lon1, lat1, lon2, lat2 '''
        self.lines.append((a,b))
        self.lines.append((c,d))

    def __str__(self):
        return self.json

    @property
    def json(self):
        if not self.lines:
            # Do not return empty feature
            return ''
        return simplejson.dumps(self.res, separators=(',',':'))
