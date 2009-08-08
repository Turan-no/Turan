#!/usr/bin/env python

import re
import sys
import os
import urllib
from MySQLdb import IntegrityError
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__ + '/../..')))
os.environ['DJANGO_SETTINGS_MODULE'] = 'lortal.settings'

from lortal.turan.models import Location

if __name__ == '__main__':
    url = 'http://fil.nrk.no/yr/viktigestader/noreg.txt'
    data = urllib.urlopen(url, "r")
    #data = open("noreg.txt", "r").read()

    for line in data.split("\n"):
        fields = line.strip("\r").split("\t")

        try:
            (county_num, town_name, priority, town_type, county, state, lat, lon, url_nn, url_nb, url_en) = fields
        except ValueError, e:
            pass

        l = Location()
        l.town = town_name.decode("UTF-8")
        l.county = county.decode("UTF-8")
        l.state = state.decode("UTF-8")
        l.lat = lat.decode("UTF-8")
        l.lon = lon.decode("UTF-8")
        l.url = url_en.decode("UTF-8")
        try:
            l.save()
        except ValueError, e:
            pass
        except IntegrityError:
            pass

