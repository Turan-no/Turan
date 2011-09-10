#!/usr/bin/env python

import re
import sys
import os
from os.path import abspath, dirname, join
import urllib
from MySQLdb import IntegrityError
from datetime import datetime
import pinax

from django.conf import settings
from django.core.management import setup_environ, execute_from_command_line

sys.path.append(os.path.dirname(os.path.abspath(__file__ + '/../..')))
try:
    import settings as settings_mod # Assumed to be in the same directory.
except ImportError:
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

# setup the environment before we start accessing things in the settings.
setup_environ(settings_mod)

sys.path.insert(0, join(settings.PINAX_ROOT, "apps"))
sys.path.insert(0, join(settings.PROJECT_ROOT, "apps"))
from turan.models import Location

if __name__ == '__main__':
    countries = {}
    if os.path.exists("countryInfo.txt"):
        data = file("countryInfo.txt")
    else:
        print "Using network"
        countries_url = "http://download.geonames.org/export/dump/countryInfo.txt"
        data = urllib.urlopen(countries_url, "r")

    for line in data.readlines():
        if line[0] in ["#", "\n", "\r"]:
            continue
        fields = line.decode("UTF-8").strip("\r").split("\t")
        try:
            countries[fields[0]] = fields[4]
        except IndexError:
            print line

    if os.path.exists("cities1000.txt"):
        data = file("cities1000.txt")
    else:
        print "Need to download cities1000"
        sys.exit(1)

    Location.objects.filter(url__startswith="http://www.geonames.org").delete()

    for line in data.readlines():
#        print line
        fields = line.decode("UTF-8").strip("\r").split("\t")
#        fields = [x.decode("UTF-8") for x in fields]
        l = Location()
        l.town = fields[1]
        l.lat = fields[4]
        l.lon = fields[5]
        l.url = "http://www.geonames.org/%s/" % (fields[0])
        l.country = countries[fields[8]]
        # Hack until we get Location.country
        l.town = l.town + ", " + l.country
        try:
            l.save()
        except ValueError, e:
            pass
        except IntegrityError:
            pass
        except Exception, e:
            print line
            raise e
