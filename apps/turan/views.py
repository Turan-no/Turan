from models import *
#from forms import *
from profiles.models import Profile
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, HttpResponsePermanentRedirect, HttpResponseForbidden, Http404
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.template import RequestContext, Context, loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django import forms
from django.core.urlresolvers import reverse
from django.db.models import Avg, Max, Min, Count, Variance, StdDev, Sum
from django.contrib.syndication.feeds import Feed
from django.contrib.comments.models import Comment
from django.core.files.storage import FileSystemStorage
from django.utils.safestring import mark_safe
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.views import redirect_to_login
from django.views.generic.create_update import get_model_and_form_class, apply_extra_context, redirect, update_object, lookup_object
from django.views.generic.list_detail import object_list
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.views.decorators.cache import cache_page

from tagging.models import Tag
from tribes.models import Tribe


import re
from datetime import timedelta, datetime
from datetime import date as datetimedate
from time import mktime, strptime
import locale

from svg import GPX2SVG
from turancalendar import WorkoutCalendar

from hrmparser import HRMParser
from gmdparser import GMDParser
from tcxparser import TCXParser

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

from friends.models import friend_set_for

def datetime2jstimestamp(obj):
    ''' Helper to generate js timestamp for usage in flot '''
    return mktime(obj.timetuple())*1000

#def profile(request, object_id):
#    ''' View for profile page for a user '''
#
#    object = get_object_or_404(UserProfile, pk=object_id)
#
#    weights = []
#    wdates = []
#
#    total_duration = timedelta()
#    total_distance = 0
#    total_avg_speed = 0
#    nr_trips = 0
#    longest_trip = 0
#    avg_length = 0
#    avg_duration = 0
#
#
#    hrs = []
#    hrs_dates = []
#
#    height = float(object.height)/100
#
#    bmidataseries = ""
#    bmiline = ''
#    pulsedataseries = ""
#    tripdataseries = ""
#    avgspeeddataseries = ""
#
#    weightqs = UserProfileDetail.objects.filter(userprofile=object_id).filter(weight__isnull=False).order_by('time')
#
#    for wtuple in weightqs.values_list('time', 'weight'):
#        bmidataseries += '[%s, %s],' % (datetime2jstimestamp(wtuple[0]), wtuple[1]/(height*height))
#        bmiline += '[%s, 25],' %datetime2jstimestamp(wtuple[0])
#
#    pulseqs = UserProfileDetail.objects.filter(userprofile=object_id).filter(resting_hr__isnull=False).order_by('time')
#    for hrtuple in pulseqs.values_list('time', 'resting_hr'):
#        pulsedataseries += '[%s, %s],' % (datetime2jstimestamp(hrtuple[0]), hrtuple[1])
#    pulsedataseries = pulsedataseries.rstrip(',')
#
#    hikeqs = Hike.objects.filter(user=object.user).order_by('date')
#    for trip in hikeqs:
#        if trip.route.distance > longest_trip:
#            longest_trip = trip.route.distance
#        if trip.duration:
#            total_duration += trip.duration
#        total_distance += trip.route.distance
#
#    cycleqs = CycleTrip.objects.filter(user=object.user).order_by('date')
#    for trip in cycleqs:
#        tripdataseries += '[%s, %s],' % ( nr_trips, trip.route.distance)
#
#        if trip.route.distance > longest_trip:
#            longest_trip = trip.route.distance
#
#        if trip.duration:
#            total_duration += trip.duration
#        total_distance += trip.route.distance
#        if trip.avg_speed:
#            # only increase counter if trip has speed
#            avgspeeddataseries += '[%s, %s],' % (datetime2jstimestamp(trip.date), trip.avg_speed)
#            total_avg_speed += trip.avg_speed
#            nr_trips += 1
#    if total_avg_speed:
#        total_avg_speed = total_avg_speed/nr_trips
#
#    total_kcals = 0
#    try:
#        total_kcals += CycleTrip.objects.filter(user=object.user).aggregate(Sum('kcal'))['kcal__sum']
#    except TypeError:
#        pass
#    try:
#        total_kcals += Hike.objects.filter(user=object.user).aggregate(Sum('kcal'))['kcal__sum']
#    except TypeError:
#        pass
#
#    #avg_speed_dict = CycleTrip.objects.filter(user=object.user).aggregate(Avg('avg_speed'), Max('avg_speed'), Min('avg_speed'), Variance('avg_speed'), StdDev('avg_speed'))
#    #hr_dict = CycleTrip.objects.filter(user=object.user).aggregate(Avg('avg_hr'), Max('avg_hr'), Min('avg_hr'), Variance('avg_hr'), StdDev('avg_hr'))
#    #cadence_dict = CycleTrip.objects.filter(user=object.user).aggregate(Avg('avg_cadence'), Max('avg_cadence'), Min('avg_cadence'), Variance('avg_cadence'), StdDev('avg_cadence'))
#    #duration_dict = CycleTrip.objects.filter(user=object.user).aggregate(Avg('duration'), Max('duration'), Min('duration'), Variance('duration'), StdDev('duration'))
#    #distance_dict = CycleTrip.objects.filter(user=object.user).aggregate(Avg('route__distance'), Max('route__distance'), Min('route__distance'), Variance('route__distance'), StdDev('route__distance'))
#
#
#
#    return render_to_response('turan/userprofile_detail.html', locals(), context_instance=RequestContext(request))


def index(request):
    ''' Index view for Turan '''

    cycletrip_list = CycleTrip.objects.all().order_by('-date', '-time')[:10]
    hike_list = Hike.objects.all().order_by('-date', '-time')[:5]
    exercise_list = OtherExercise.objects.all().order_by('-date', '-time')[:5]
    comment_list = Comment.objects.order_by('-submit_date', '-time')[:5]

    route_list = Route.objects.all()
    route_list = sorted(route_list, key=lambda x: -x.cycletrip_set.count()-x.hike_set.count())[:15]

    tag_list = Tag.objects.all()

    return render_to_response('turan/index.html', locals(), context_instance=RequestContext(request))

def trip_compare(request, event_type, trip1, trip2):

    if event_type == 'cycletrip' or event_type == 'trip':
        trip1 = get_object_or_404(CycleTrip, pk=trip1)
        trip2 = get_object_or_404(CycleTrip, pk=trip2)
        if event_type == 'trip':
            event_type = 'cycletrip'
    elif event_type == 'hike':
        trip1 = get_object_or_404(Hike, pk=trip1)
        trip2 = get_object_or_404(Hike, pk=trip2)
    elif event_type == 'exercise':
        trip1 = get_object_or_404(OtherExercise, pk=trip1)
        trip2 = get_object_or_404(OtherExercise, pk=trip2)
    else:
        return HttpResponse('unsupported type')

    t1_speed = tripdetail_js(event_type, trip1.id, 'speed')
    t2_speed = tripdetail_js(event_type, trip2.id, 'speed')
    t1_hr = tripdetail_js(event_type, trip1.id, 'hr')
    t2_hr = tripdetail_js(event_type, trip2.id, 'hr')
    t1_cad = tripdetail_js(event_type, trip1.id, 'cadence')
    t2_cad = tripdetail_js(event_type, trip2.id, 'cadence')

    alt = tripdetail_js(event_type, trip1.id, 'altitude')

    alt_max = trip1.get_details().aggregate(Max('altitude'))['altitude__max']*2

    return render_to_response('turan/cycletrip_compare.html', locals(), context_instance=RequestContext(request))

class TripsFeed(Feed):
    title = "lart.no turan trips"
    link = "https://lart.no/turan/"
    description = "Trips from lart.no/turan"

    def items(self):
        return CycleTrip.objects.order_by('-date')[:20]

    def item_author_name(self, obj):
        "Item author"
        return obj.user

    def item_link(self, obj):
        return reverse('cycletrip', kwargs={ 'object_id': obj.id })

    def item_pubdate(self, obj):
        try:
            return datetime(obj.date.year, obj.date.month, obj.date.day, obj.time.hour, obj.time.minute, obj.time.second)
        except AttributeError:
            pass # Some trips just doesn't have time set
        return

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('turanindex'))

def events(request, group_slug=None, bridge=None, username=None):
    object_list = []

    if bridge is not None:
        try:
            group = bridge.get_group(group_slug)
        except ObjectDoesNotExist:
            raise Http404
    else:
        group = None

    if group:
        cycleqs = group.content_objects(CycleTrip)
        hikeqs = group.content_objects(Hike)
        exerciseqs = group.content_objects(OtherExercise)
    else:
        cycleqs = CycleTrip.objects.select_related()
        hikeqs = Hike.objects.select_related()
        exerciseqs = OtherExercise.objects.select_related()
        if username:
            user = get_object_or_404(User, username=username)
            cycleqs = cycleqs.filter(user=user)
            hikeqs = hikeqs.filter(user=user)
            exerciseqs = exerciseqs.filter(user=user)


    object_list.extend(cycleqs)
    object_list.extend(hikeqs)
    object_list.extend(exerciseqs)
    object_list = sorted(object_list, key=lambda x: x.date)
    object_list.reverse()

    return render_to_response('turan/event_list.html', locals(), context_instance=RequestContext(request))

def route_detail(request, object_id):
    object = get_object_or_404(Route, pk=object_id)
    speeddataseries = ''
    for trip in sorted(object.get_trips(), key=lambda x:x.date):
        try:
            time = trip.duration.seconds/60
            speeddataseries +=  '[%s, %s],' % (datetime2jstimestamp(trip.date), time)
        except AttributeError:
            pass # stupid decimal value in trip duration!
    return render_to_response('turan/route_detail.html', locals(), context_instance=RequestContext(request))

def week(request, week, user_id='all'):

    object_list = []
    cycleqs = CycleTrip.objects.filter(date__month=week)
    hikeqs = Hike.objects.filter(date__month=week)

    for e in cycleqs:
        object_list.append(e)
    for e in hikeqs:
        object_list.append(e)
    
    return render_to_response('turan/event_list.html', locals(), context_instance=RequestContext(request))

def statistics(request, year=None, month=None):
    teamname = request.GET.get('team')
    if teamname:
        team = get_object_or_404(Tribe, slug=teamname)
        statsusers = team.members.all()
        statsprofiles = Profile.objects.all().filter(user__in=statsusers)
    else:
        statsprofiles = Profile.objects.all()

    stats_dict = CycleTrip.objects.aggregate(Max('avg_speed'), Avg('avg_speed'), Avg('route__distance'), Max('route__distance'), Sum('route__distance'), Avg('duration'), Max('duration'), Sum('duration'))
    total_duration = stats_dict['duration__sum']
    total_distance = stats_dict['route__distance__sum']
    total_avg_speed = stats_dict['avg_speed__avg']
    longest_trip = stats_dict['route__distance__max']

    userstats = statsprofiles.annotate( \
            avg_avg_speed = Avg('user__cycletrip__avg_speed'), \
            max_avg_speed = Max('user__cycletrip__avg_speed'), \
            max_speed = Max('user__cycletrip__max_speed'), \
            num_trips = Count('user__cycletrip'), \
            sum_distance = Sum('user__cycletrip__route__distance'), \
            sum_duration = Sum('user__cycletrip__duration'), \
            sum_energy = Sum('user__cycletrip__kcal'), \
            sum_ascent = Sum('user__cycletrip__route__ascent'), \
            avg_avg_hr = Avg('user__cycletrip__avg_hr') \
            )

    maxavgspeeds = userstats.filter(max_avg_speed__gt=0.0).order_by('max_avg_speed').reverse()
    maxspeeds = userstats.filter(max_speed__gt=0.0).order_by('max_speed').reverse()
    avgspeeds = userstats.filter(avg_avg_speed__gt=0.0).order_by('avg_avg_speed').reverse()
    numtrips = userstats.filter(num_trips__gt=0).order_by('num_trips').reverse()
    distsums = userstats.filter(sum_distance__gt=0).order_by('sum_distance').reverse()
    dursums = userstats.filter(sum_duration__gt=0).order_by('sum_duration').reverse()
    energysums = userstats.filter(sum_energy__gt=0).order_by('sum_energy').reverse()
    ascentsums = userstats.filter(sum_ascent__gt=0).order_by('sum_ascent').reverse()
    avgavghrs = userstats.filter(avg_avg_hr__gt=0).filter(max_hr__gt=0)

    for u in avgavghrs:
        u_avg_avg_hr = u.avg_avg_hr
        if u_avg_avg_hr:
            u.avgavghrpercent = float(u_avg_avg_hr)/u.max_hr*100
        else:
            u.avgavghrpercent = 0
    avgavghrs = sorted(avgavghrs, key=lambda x:-x.avgavghrpercent)

    validroutes = Route.objects.filter(ascent__gt=0).filter(distance__gt=0)
    climbstats = statsprofiles.filter(user__cycletrip__route__in=validroutes).annotate( \
            distance = Sum('user__cycletrip__route__distance'), \
            height = Sum('user__cycletrip__route__ascent'),  \
            duration = Sum('user__cycletrip__duration') \
            )

    for u in climbstats:
        u.avgclimb = u.height/u.distance
        u.avgclimbperhour = u.height/(float(u.duration)/10**6/3600)
    climbstats = sorted(climbstats, key=lambda x: -x.avgclimb)
    climbstatsbytime = sorted(climbstats, key=lambda x:-x.avgclimbperhour)

    hikestats = statsprofiles.annotate( \
            hike_avg_avg_speed = Avg('user__hike__avg_speed'), \
            hike_max_avg_speed = Max('user__hike__avg_speed'), \
            hike_max_speed = Max('user__hike__max_speed'), \
            hike_num_trips = Count('user__hike'), \
            hike_sum_distance = Sum('user__hike__route__distance'), \
            hike_sum_duration = Sum('user__hike__duration'), \
            hike_sum_energy = Sum('user__hike__kcal'), \
            hike_sum_ascent = Sum('user__hike__route__ascent'), \
            hike_avg_avg_hr = Avg('user__hike__avg_hr') \
            )

    hike_maxavgspeeds = hikestats.filter(hike_max_avg_speed__gt=0.0).order_by('hike_max_avg_speed').reverse()
    hike_maxspeeds = hikestats.filter(hike_max_speed__gt=0.0).order_by('hike_max_speed').reverse()
    hike_avgspeeds = hikestats.filter(hike_avg_avg_speed__gt=0.0).order_by('hike_avg_avg_speed').reverse()
    hike_numtrips = hikestats.filter(hike_num_trips__gt=0).order_by('hike_num_trips').reverse()
    hike_distsums = hikestats.filter(hike_sum_distance__gt=0).order_by('hike_sum_distance').reverse()
    hike_dursums = hikestats.filter(hike_sum_duration__gt=0).order_by('hike_sum_duration').reverse()
    hike_energysums = hikestats.filter(hike_sum_energy__gt=0).order_by('hike_sum_energy').reverse()
    hike_ascentsums = hikestats.filter(hike_sum_ascent__gt=0).order_by('hike_sum_ascent').reverse()
    hike_avgavghrs = hikestats.filter(hike_avg_avg_hr__gt=0).filter(max_hr__gt=0)

    for u in hike_avgavghrs:
        u.avgavghrpercent = float(u.hike_avg_avg_hr)/u.max_hr*100
    hike_avgavghrs = sorted(hike_avgavghrs, key=lambda x:-x.avgavghrpercent)

    hike_climbstats = statsprofiles.filter(user__hike__route__in=validroutes).annotate( \
            distance = Sum('user__hike__route__distance'), \
            height = Sum('user__hike__route__ascent'), \
            duration = Sum('user__hike__duration') \
            )

    for u in hike_climbstats:
        u.avgclimb = u.height/u.distance
        u.avgclimbperhour = u.height/(float(u.duration)/10**6/3600)
    hike_climbstats = sorted(hike_climbstats, key=lambda x: -x.avgclimb)
    hike_climbstatsbytime = sorted(hike_climbstats, key=lambda x:-x.avgclimbperhour)

    return render_to_response('turan/statistics.html', locals(), context_instance=RequestContext(request))

def generate_tshirt(request):
    import Image
    import ImageFont
    import ImageDraw
    from cStringIO import StringIO

    root = (150, 200)

    if 'user' in request.GET:
        user = request.GET['user']
    else:
        user = 1

    if 'team' in request.GET:
        team = request.GET['team']

    user = User.objects.filter(pk = user)[0]

    try:
        team = Team.objects.filter(members = user).filter(pk = team)[0]
    except IndexError:
        team = None

    if team:
        tlogo = team.logo.file.name
        logoim = Image.open(tlogo)
    else:
        logoim = None

    if user.first_name != None and len(user.first_name) > 0:
        shirt_name = user.first_name[0] + ". " + user.last_name
    else:
        shirt_name = user.username

    im = Image.open(settings.MEDIA_ROOT + "turan/tshirt.jpg")
    ifont = ImageFont.truetype("/usr/share/fonts/truetype/ttf-liberation/LiberationSans-Regular.ttf", 36)
    draw = ImageDraw.Draw(im)
    draw.rectangle([(123,200), (420,260)], fill=0xeeeeee)
    draw.rectangle([(123,260), (421,447)], fill=0xff3030)
    draw.text((root[0]+64+10,root[1]+10), shirt_name, font=ifont, fill=1)

    if logoim:
        im.paste(logoim, root, logoim)

    #im = im.resize((200,200))
    data = StringIO()
    im.save(data, "png")
    data.seek(0)
    return HttpResponse(data.read(), mimetype='image/png',status=200)

def normalize_altitude(trip_id):
    ''' Normalize altitude, that is, if it's below zero scale every value up '''

    altitude_min = CycleTripDetail.objects.filter(trip=trip_id).aggregate(Min('altitude'))['altitude__min']
    if altitude_min < 0:
        altitude_min = 0 - altitude_min
        for ctd in CycleTripDetail.objects.filter(trip=trip_id):
            ctd.altitude += altitude_min
            ctd.save()

def calendar(request, user_id=False):
    now = datetime.now()
    return calendar_month(request, now.year, now.month, user_id)

def calendar_month(request, year, month, user_id=False):
    ''' the calendar view, some code stolen from archive_month generic view '''

    month_format = '%m' 
    allow_future = True
    date_field = 'date'
    tt = strptime("%s-%s" % (year, month), '%s-%s' % ('%Y', month_format))
    date = datetimedate(*tt[:3])
    now = datetime.now()


    # Calculate first and last day of month, for use in a date-range lookup.
    first_day = date.replace(day=1)
    if first_day.month == 12:
        last_day = first_day.replace(year=first_day.year + 1, month=1)
    else:
        last_day = first_day.replace(month=first_day.month + 1)
    lookup_kwargs = {
        '%s__gte' % date_field: first_day,
        '%s__lt' % date_field: last_day,
    }

    # Only bother to check current date if the month isn't in the past and future objects are requested.
    if last_day >= now.date() and not allow_future:
        lookup_kwargs['%s__lte' % date_field] = now


    cycletrips = CycleTrip.objects.order_by('date').filter(**lookup_kwargs)
    hikes = Hike.objects.order_by('date').filter(**lookup_kwargs)
    exercices = OtherExercise.objects.order_by('date').filter(**lookup_kwargs)

    if user_id:
        cycletrips = cycletrips.filter(user=user_id)
        hikes = hikes.filter(user=user_id)
        exercices = exercices.filter(user=user_id)

    # Calculate the next month, if applicable.
    if allow_future:
        next_month = last_day
    elif last_day <= datetime.date.today():
        next_month = last_day
    else:
        next_month = None

    # Calculate the previous month
    if first_day.month == 1:
        previous_month = first_day.replace(year=first_day.year-1,month=12)
    else:
        previous_month = first_day.replace(month=first_day.month-1)

    months = []
    workouts = []
    workouts.extend(cycletrips)
    workouts.extend(hikes)
    workouts.extend(exercices)
    workouts = sorted(workouts, key=lambda x: x.date)

   # FIXME django locale
    # stupid calendar needs int
    year, month = int(year), int(month)
    cal = WorkoutCalendar(workouts, locale.getdefaultlocale()).formatmonth(year, month)
    return render_to_response('turan/calendar.html',
            {'calendar': mark_safe(cal),
             'months': months,
             'previous_month': previous_month,
             'next_month': next_month,
             },
            context_instance=RequestContext(request))

@cache_page(86400*7)
def geojson(request, event_type, object_id):
    ''' Return GeoJSON with coords as linestring for use in openlayers stylemap,
    give each line a zone property so it can be styled differently'''

    if event_type == 'cycletrip':
        qs = CycleTripDetail.objects.filter(trip=object_id)
    elif event_type == 'hike':
        qs = HikeDetail.objects.filter(trip=object_id)
    elif event_type == 'exercise':
        qs = OtherExerciseDetail.objects.filter(trip=object_id)

    qs = qs.exclude(lon=0).exclude(lat=0)
    if qs.count() == 0:
        return HttpResponse('{}')

    max_hr = qs[0].trip.user.get_profile().max_hr

    class Feature(object):

        linestrings = '\n'

        def __init__(self, zone):
            self.jsonhead = '''
            { "type": "Feature", "properties":
                { "ZONE": %s },
                "geometry": {
                    "type": "LineString", "coordinates": [ ''' %zone
            self.jsonfoot = '''] }
            },'''
            
        def addLine(self, a, b, c, d):
            self.linestrings += '[%s, %s], [%s, %s],\n' %(a,b,c,d)

        @property
        def json(self):
            if self.linestrings == '\n':
                # Don't return empty feature
                return ''
            return self.jsonhead + self.linestrings + self.jsonfoot

    features = []

    previous_lon, previous_lat, previous_zone = 0, 0, 0
    previous_feature = False
    for d in qs:
        if previous_lon and previous_lat:
            hr_percent = float(d.hr)*100/max_hr
            zone = 1
            if hr_percent > 89:
                zone = 5
            elif hr_percent > 79:
                zone = 4
            elif hr_percent > 69:
                zone = 3
            elif hr_percent > 59:
                zone = 2

            if previous_zone == zone:
                previous_feature.addLine(previous_lon, previous_lat, d.lon, d.lat)
            else:
                if previous_feature:
                    features.append(previous_feature)
                previous_feature = Feature(zone)

            previous_zone = zone
        previous_lon = d.lon
        previous_lat = d.lat

    # add last segment
    features.append(previous_feature)


    gjhead = '''{
    "type": "FeatureCollection",
        "features": ['''
    gjfoot = ']}'
    gjstr = gjhead
    for f in features:
        gjstr += f.json
    gjstr = gjstr.rstrip(',')
    gjstr += gjfoot

    return HttpResponse(re.sub('\s','', gjstr), mimetype='text/javascript')

def tripdetail_js(event_type, object_id, val, start=False, stop=False):
    if start:
        start = int(start)
    if stop:
        stop = int(stop)
    if event_type == 'cycletrip':
        qs = CycleTripDetail.objects.filter(trip=object_id)
    elif event_type == 'hike':
        qs = HikeDetail.objects.filter(trip=object_id)
    elif event_type == 'exercise':
        qs = OtherExerciseDetail.objects.filter(trip=object_id)

    distance = 0
    previous_time = False
    js = ''
    for i, d in enumerate(qs.iterator()):
        if start and start < i:
            continue
        if stop and i > stop:
            break
        if not previous_time:
            previous_time = d.time
        time = d.time - previous_time
        previous_time = d.time
        distance += ((d.speed/3.6) * time.seconds)/1000
        dval = getattr(d, val)
        if dval > 0: # skip zero values (makes prettier graph)
            js += '[%s, %s],' % (distance, dval)
    return js

def json_tripdetail(request, event_type, object_id, val, start=False, stop=False):

    #response = HttpResponse()
    #serializers.serialize('json', qs, fields=('id', val), indent=4, stream=response)
    js = tripdetail_js(event_type, object_id, val, start, stop)
    return HttpResponse(js)

def getslopes(values):
    slopes = []
    min_slope = 40
    cur_start = 0
    cur_end = 0
    stop_since = False
    inslope = False
    for i in xrange(1,len(values)):
        if values[i].speed < 0.05 and not stop_since:
            stop_since = i
        if values[i].speed >= 0.05:
            stop_since = False
        if inslope:
            if values[i].altitude > values[cur_end].altitude:
                cur_end = i
            hdelta = values[cur_end].altitude - values[cur_start].altitude
            if stop_since:
                stop_duration = (values[i].time - values[stop_since].time).seconds
            else:
                stop_duration = 0
            if values[i].altitude < values[cur_start].altitude + hdelta*0.9 \
                    or i == len(values) \
                    or stop_duration > 60:
                if stop_duration > 60:
                    cur_stop = stop_since
                inslope = False
                if hdelta >= min_slope:
                    distance = values[cur_end].distance - values[cur_start].distance
                    slopes.append(Slope(cur_start, cur_end, distance, hdelta, hdelta/distance * 100, values[cur_start].distance/1000))
                cur_start = i
        elif values[i].altitude <= values[cur_start].altitude:
            cur_start = i
            cur_end  = i
        elif values[i].altitude > values[cur_start].altitude:
            cur_end = i
            inslope = True
    return slopes

def getdistance(values, start, end):
    d = 0
    for i in xrange(start+1, end+1):
        delta_t = (values[i].time - values[i-1].time).seconds
        d += values[i].speed/3.6 * delta_t
    return d

def filldistance(values):
    d = 0
    values[0].distance = 0
    for i in xrange(1,len(values)):
        delta_t = (values[i].time - values[i-1].time).seconds
        d += values[i].speed/3.6 * delta_t
        values[i].distance = d

def getavghr(values, start, end):
    hr = 0
    for i in xrange(start+1, end+1):
        delta_t = (values[i].time - values[i-1].time).seconds
        hr += values[i].hr*delta_t
    delta_t = (values[end].time - values[start].time).seconds
    return float(hr)/delta_t

class Slope(object):
    def __init__(self, start, end, length, hdelta, gradient, start_km):
        self.start = start
        self.end = end
        self.length = length
        self.hdelta = hdelta
        self.gradient = gradient
        self.start_km = start_km

def calcpower(userweight, eqweight, gradient, speed, 
        rollingresistance = 0.006 ,
        airdensity = 1.22 ,
        frontarea = 0.7 ):
    tot_weight = userweight+eqweight
    gforce = tot_weight * gradient/100 * 9.81
    frictionforce = rollingresistance * tot_weight * 9.81
    windforce = 0.5**2 * speed**2  * airdensity * frontarea
    return (gforce + frictionforce + windforce)*speed

def cycletrip(request, object_id):
    ''' View for cycletrip detail '''

    object = get_object_or_404(CycleTrip, pk=object_id)
    details = object.cycletripdetail_set.all()
    if details:
        #userweight = object.user.userprofile_set.all()[0].weight
        userweight = object.user.get_profile().weight
        filldistance(details)
        slopes = getslopes(details)
        for slope in slopes:
            delta_t = (details[slope.end].time - details[slope.start].time).seconds
            slope.speed = slope.length/delta_t * 3.6
            slope.avg_hr = getavghr(details, slope.start, slope.end)
            slope.avg_power = calcpower(userweight, 10, slope.gradient, slope.speed/3.6)
        
        speedjs = tripdetail_js('cycletrip', object_id, 'speed')
        hrjs = tripdetail_js('cycletrip', object_id, 'hr')
        cadencejs = tripdetail_js('cycletrip', object_id, 'cadence')
        powerjs = tripdetail_js('cycletrip', object_id, 'power')
        altitudejs = tripdetail_js('cycletrip', object_id, 'altitude')
    return render_to_response('turan/cycletrip_detail.html', locals(), context_instance=RequestContext(request))

def json_serializer(request, queryset, root_name = None, relations = (), extras = ()):
    if root_name == None:
        root_name = queryset.model._meta.verbose_name_plural
    #hardcoded relations and extras while testing
    return HttpResponse(serializers.serialize('json', queryset, indent=4, relations=relations, extras=extras), mimetype='text/javascript')

def create_object(request, model=None, template_name=None,
        template_loader=loader, extra_context=None, post_save_redirect=None,
        login_required=False, context_processors=None, form_class=None, user_required=False):
    """
    Generic object-creation function. 
    Modified for turan to always save user to model

    Templates: ``<app_label>/<model_name>_form.html``
    Context:
        form
            the form for the object
    """
    if extra_context is None: extra_context = {}
    if login_required and not request.user.is_authenticated():
        return redirect_to_login(request.path)

    model, form_class = get_model_and_form_class(model, form_class)
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            new_object = form.save(commit=False)
            if user_required:
                new_object.user = request.user
            new_object.save()

            # notify friends of new object
            if notification and user_required: # only notify for user owned objects
                notification.send(friend_set_for(request.user.id), 'exercise_create', {'sender': request.user, 'exercise': new_object}, [request.user])
            

            if request.user.is_authenticated():
                request.user.message_set.create(message=ugettext("The %(verbose_name)s was created successfully.") % {"verbose_name": model._meta.verbose_name})
            return redirect(post_save_redirect, new_object)
    else:
        form = form_class()

    # Create the template, context, response
    if not template_name:
        template_name = "%s/%s_form.html" % (model._meta.app_label, model._meta.object_name.lower())
    t = template_loader.get_template(template_name)
    c = RequestContext(request, {
        'form': form,
    }, context_processors)
    apply_extra_context(extra_context, c)
    return HttpResponse(t.render(c))

def update_object_user(request, model=None, object_id=None, slug=None,
        slug_field='slug', template_name=None, template_loader=loader,
        extra_context=None, post_save_redirect=None, login_required=False,
        context_processors=None, template_object_name='object',
        form_class=None):
    """
    Uses generic update code, just checks if object is owned by user.
    """

    model, form_class = get_model_and_form_class(model, form_class)
    obj = lookup_object(model, object_id, slug, slug_field)
    if not obj.user == request.user:
        return HttpResponseForbidden('Wat?')

    return update_object(request, model, object_id, slug, slug_field, template_name,
            template_loader, extra_context, post_save_redirect, login_required,
            context_processors, template_object_name, form_class)

def turan_object_list(request, queryset):

    search_query = request.GET.get('q', '')
    if search_query:
        qset = (
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(tags__contains=search_query)
        )
        queryset = queryset.filter(qset).distinct()

    username = request.GET.get('username', '')
    if username:
        user = get_object_or_404(User, username=username)
        queryset = queryset.filter(user=user)

    return object_list(request, queryset=queryset)


def autocomplete_route(request, app_label, model):
    ''' ajax view to return list of matching routes to given query'''

    #try:
    #    model = ContentType.objects.get(app_label=app_label, model=model)
    #except:
    #    raise Http404

    if not request.GET.has_key('q'):
        raise Http404

    query = request.GET.get('q', '')
    qset = (
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__contains=query)
        )

    limit = request.GET.get('limit', None)

    routes = Route.objects.filter(qset).order_by('name').distinct()[:limit]
    route_list = '\n'.join([u'%s|%s' % (f.__unicode__(), f.pk) for f in routes])

    return HttpResponse(route_list)
