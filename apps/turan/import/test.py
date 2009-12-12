# abach 2009
# imports polarpersonaltrainer.com-exercises from xml-file, merges it with
# on.wheelz.biz-data and submits it to turan. Needs to be run from shell.
# -*- coding: utf-8 -*-
import sys
import xml.sax
import triphandler
from django.db import models
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from datetime import date, time
from apps.turan.models import *
import pprint
import urllib
import re
def strip_tags(value):
    return re.sub(r'<[^>]*?>', '', value)


parser = xml.sax.make_parser()
handler = triphandler.TripHandler()
parser.setContentHandler(handler)
parser.parse("abach.xml")
i = 0

for index,trip in enumerate(handler.mapper):

   
    r_created = False
    extra_tags = ""
    r = Route()
    if handler.mapper[trip]['name'] == "NoName":
        r.name = str(trip)
    else:
        r.name = handler.mapper[trip]['name']
    if handler.mapper[trip].has_key('distance'):
        r.distance = handler.mapper[trip]['distance']/1000.0
    else:
        r.distance = 0.0

    c = CycleTrip()
    c.user = User.objects.get(username='andreas')
    year = int(trip[0:4])
    month = int(trip[5:7])
    day = int(trip[8:10])

    c.date = date(int(trip[0:4]), int(trip[5:7]), int(trip[8:10]))
    c.url = "http://on.wheelz.biz/tur.php?user=8&dato=" + trip

    f = urllib.urlopen("http://on.wheelz.biz/tur.php?user=8&dato=" + trip)
    s = f.read()
    f.close()
    start = s.find("Tras")
    end = s.find("</p>", start)
    trase = s[start+11:end]
    trase = trase.decode('ISO-8859-1')
    trase = strip_tags(trase)
    r.description = trase
    try:
        r, r_created = Route.objects.get_or_create(description=trase, distance=r.distance)
        if handler.mapper[trip]['name'] == "NoName":
            r.name = str(trip)
        else:
            r.name = handler.mapper[trip]['name']
    except Exception, e:
        if isinstance(e, MultipleObjectsReturned):
            r.save()
            r_created = 1
        else:
            sys.exit()
    r.tags = "\"abach import\""



    start = s.find("Kommentar:")
    end = s.find("</p>", start)
    kommentar = s[start+15:end]
    kommentar = kommentar.decode('ISO-8859-1')
    kommentar = strip_tags(kommentar)
    kommentar = kommentar.replace('&quot;', '"')
    if 'knall' in kommentar:
        extra_tags += "knall "
    c.comment = kommentar

    start = s.find("<br><img src=")
    end = s.find("\">", start)
    vaer = s[start+21:end-4]
    if vaer == "sky_sol":
        vaer = "\"delvis overskyet\" "
    if vaer == "sky":
        vaer = "overskyet "
    if vaer == "sol_sky":
        vaer = "\"for det meste sol\" "
    if vaer == "sol_regn":
        vaer = "\"varierende vær\" "
    if vaer == "regn":
        vaer = "regnvær "
    if vaer == "regn_regn":
        vaer = "\"pøsende regnvær\" "
    if vaer == "regn_sno":
        vaer = "sludd "
    if vaer == "sol_regn_sno":
        vaer = "trøndervær "
    if vaer == "sol":
        vaer = "sol "
    
    hour = int(handler.mapper[trip]['timeofday'][0:2])
    if hour > 20:
        extra_tags += "kveldstur "


    if handler.mapper[trip].has_key('timeofday'):
        c.time = handler.mapper[trip]['timeofday']
    if handler.mapper[trip].has_key('avgSpeed'):
        c.avg_speed = handler.mapper[trip]['avgSpeed']
    if handler.mapper[trip].has_key('maxSpeed'):
        c.max_speed = handler.mapper[trip]['maxSpeed']
    if handler.mapper[trip].has_key('avgCadence'):
        c.avg_cadence = handler.mapper[trip]['avgCadence']
    if handler.mapper[trip].has_key('maxCadence'):
        c.max_cadence = handler.mapper[trip]['maxCadence']
    if handler.mapper[trip].has_key('hrAvg'):
        c.avg_hr = handler.mapper[trip]['hrAvg']
    if handler.mapper[trip].has_key('hrMax'):
        c.max_hr = handler.mapper[trip]['hrMax']
    if handler.mapper[trip].has_key('duration'):
        hour = handler.mapper[trip]['duration'][0:2]
        if not hour:
            hour = 0
        minute = handler.mapper[trip]['duration'][3:5]
        if not minute:
            minute = 0
        sec = handler.mapper[trip]['duration'][6:8]
        if not sec:
            sec = 0
        c.duration = str(hour) + "h " + str(minute) + "min " + str(sec) + "s"
    else:
        c.duration = "1min"
    if handler.mapper[trip].has_key('calories'):
        c.kcal = handler.mapper[trip]['calories']

    if c.avg_cadence and c.avg_cadence < 80:
        extra_tags += "ulletråkk "
    if c.avg_hr > 170:
        extra_tags += "knallhardt "


    c.tags = "\"abach import\" " + vaer + extra_tags

    if r.name and c.time:
        r.save()
        
        c.route = r
        c.save()
