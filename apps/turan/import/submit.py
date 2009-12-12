import sys
import os

from os.path import abspath, dirname, join
from site import addsitedir

PINAX_ROOT = abspath(join(dirname(__file__), "../../.."))
PROJECT_ROOT = abspath(join(dirname(__file__), "./"))

path = addsitedir(join(PINAX_ROOT, "libs/external_libs"), set())
if path:
        sys.path = list(path) + sys.path
sys.path.insert(0, join(PINAX_ROOT, "apps/external_apps"))
sys.path.insert(0, join(PINAX_ROOT, "apps/local_apps"))
sys.path.insert(0, join(PINAX_ROOT, "projects"))
sys.path.insert(0, join(PROJECT_ROOT, "apps"))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, abspath(join(dirname(__file__), "../../")))

sys.path.append(os.path.dirname(os.path.abspath(__file__ + '/..')))
os.environ['DJANGO_SETTINGS_MODULE'] = 'turansite.settings'

from django.db import models
from django.conf import settings
from datetime import date, time
from apps.turan.models import *
from django.core.cache import cache
import pprint
import xml.sax
import triphandler

#import django.core.handlers.wsgi
#application = django.core.handlers.wsgi.WSGIHandler()
#import isapi_wsgi

parser = xml.sax.make_parser()
handler = triphandler.TripHandler()
parser.setContentHandler(handler)
parser.parse("abach.xml")

for date,trip in enumerate(handler.mapper):
   
    r = Route()
    r.name = handler.mapper[trip]['name']
    r.distance = handler.mapper[trip]['distance']
    r.singleserving = 1
    r.tags = "abach import"

    r.save()
    sys.exit()

r = Route()

r.name = "No Name"
r.distance = 10.0
r.singleserving = 1
r.description = "testtur"
r.tags = "abach import"
r.save()

c = CycleTrip()
c.avg_speed = 25.0
c.user = User.objects.get(username='andreas')
c.route = r
c.date = date(2009, 12, 12)
c.duration = "1h 1min"
c.tags = "abach import"

c.save()



