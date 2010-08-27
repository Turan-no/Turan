from models import *
from itertools import groupby
from forms import ExerciseForm
from profiles.models import Profile
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, HttpResponsePermanentRedirect, HttpResponseForbidden, Http404
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.template import RequestContext, Context, loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django import forms
from django.forms.models import inlineformset_factory
from django.core.urlresolvers import reverse
from django.db.models import Avg, Max, Min, Count, Variance, StdDev, Sum
from django.contrib.syndication.feeds import Feed
from threadedcomments.models import ThreadedComment
from django.core.files.storage import FileSystemStorage
from django.utils.safestring import mark_safe
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.views import redirect_to_login
from django.views.generic.create_update import get_model_and_form_class, apply_extra_context, redirect, update_object, lookup_object, delete_object
from django.views.generic.list_detail import object_list
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.utils.decorators import decorator_from_middleware
from django.utils.datastructures import SortedDict
from django.middleware.gzip import GZipMiddleware

from django.core.files.base import ContentFile
from turan.models import Route
from urllib2 import urlopen
from tempfile import NamedTemporaryFile


from BeautifulSoup import BeautifulSoup

from tagging.models import Tag
from tribes.models import Tribe
from friends.models import Friendship

import re
from datetime import timedelta, datetime
from datetime import date as datetimedate
from time import mktime, strptime
import locale

from svg import GPX2SVG
from turancalendar import WorkoutCalendar
from feeds import ExerciseCalendar

import simplejson
from profiler import profile

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

from friends.models import friend_set_for

def datetime2jstimestamp(obj):
    ''' Helper to generate js timestamp for usage in flot '''
    return mktime(obj.timetuple())*1000

def index(request):
    ''' Index view for Turan '''

    exercise_list = Exercise.objects.all()[:10]
    comment_list = ThreadedComment.objects.filter(is_public=True).order_by('-date_submitted')[:5]

    route_list = Route.objects.extra( select={ 'tcount': 'SELECT COUNT(*) FROM turan_exercise WHERE turan_exercise.route_id = turan_route.id' }).extra( order_by= ['-tcount',])[:12]
    #route_list = sorted(route_list, key=lambda x: -x.exercise_set.count())[:15]

    tag_list = Tag.objects.cloud_for_model(Exercise)

    # Top exercisers last 14 days
    today = datetimedate.today()
    days = timedelta(days=14)
    begin = today - days
    user_list = User.objects.filter(exercise__date__range=(begin, today)).annotate(Sum('exercise__duration')).filter(exercise__duration__gt=0).order_by('-exercise__duration__sum')

    return render_to_response('turan/index.html', locals(), context_instance=RequestContext(request))

def exercise_compare(request, exercise1, exercise2):

    trip1 = get_object_or_404(Exercise, pk=exercise1)
    trip2 = get_object_or_404(Exercise, pk=exercise2)
    if trip1.exercise_permission == 'N' or trip2.exercise_permission == 'N':
        return redirect_to_login(request.path)
        # TODO Friend check

    alt = tripdetail_js(None, trip1.id, 'altitude')
    #alt_max = trip1.get_details().aggregate(Max('altitude'))['altitude__max']*2

    datasets1 = js_trip_series(request, trip1.get_details().all(), time_xaxis=False, use_constraints=False)
    datasets2 = js_trip_series(request, trip2.get_details().all(), time_xaxis=False, use_constraints=False)
    if not datasets1 or not datasets2:
        return HttpResponse(_('Missing exercise details.'))
    datasets = mark_safe(datasets1 +',' +datasets2)

    return render_to_response('turan/exercise_compare.html', locals(), context_instance=RequestContext(request))

class TripsFeed(Feed):
    title = "lart.no turan trips"
    link = "http://turan.no/turan/"
    description = "Trips from turan.no/turan"

    def items(self):
        return Exercise.objects.order_by('-date')[:20]

    def item_author_name(self, obj):
        "Item author"
        return obj.user

    def item_link(self, obj):
        return  obj.get_absolute_url()

    def item_pubdate(self, obj):
        try:
            return datetime(obj.date.year, obj.date.month, obj.date.day, obj.time.hour, obj.time.minute, obj.time.second)
        except AttributeError:
            pass # Some trips just doesn't have time set
        return

def events(request, group_slug=None, bridge=None, username=None, latitude=None, longitude=None):
    object_list = []

    if bridge is not None:
        try:
            group = bridge.get_group(group_slug)
        except ObjectDoesNotExist:
            raise Http404
    else:
        group = None

    if group:
        exerciseqs = group.content_objects(Exercise)
    else:
        exerciseqs = Exercise.objects.select_related().filter(date__isnull=False)
        if username:
            user = get_object_or_404(User, username=username)
            exerciseqs = exerciseqs.filter(user=user)

    if latitude and longitude:
        # A litle aprox box around your area
        exerciseqs = exerciseqs.filter(route__start_lat__gt=float(latitude) - 0.5)
        exerciseqs = exerciseqs.filter(route__start_lat__lt=float(latitude) + 0.5)
        exerciseqs = exerciseqs.filter(route__start_lon__gt=float(longitude) - 1.0)
        exerciseqs = exerciseqs.filter(route__start_lon__lt=float(longitude) + 1.0)

    search_query = request.GET.get('q', '')
    if search_query:
        qset = (
            Q(route__name__icontains=search_query) |
            Q(comment__icontains=search_query) |
            Q(tags__contains=search_query)
        )
        exerciseqs = exerciseqs.filter(qset).distinct()

    object_list = exerciseqs

    return render_to_response('turan/event_list.html', locals(), context_instance=RequestContext(request))

def route_detail(request, object_id):
    object = get_object_or_404(Route, pk=object_id)
    usertimes = {}
    try:
        done_altitude_profile = False
        for trip in sorted(object.get_trips(), key=lambda x:x.date):
            if not trip.user in usertimes:
                usertimes[trip.user] = ''
            try:
                time = trip.duration.seconds/60
                if trip.avg_speed: # Or else graph bugs with None-values
                    usertimes[trip.user] += mark_safe('[%s, %s],' % (datetime2jstimestamp(trip.date), trip.avg_speed))
            except AttributeError:
                pass # stupid decimal value in trip duration!

            if trip.avg_speed and trip.get_details().count() and not done_altitude_profile: # Find trip with speed or else tripdetail_js bugs out
                                                             # and trip with details
                alt = tripdetail_js(None, trip.id, 'altitude')
                alt_max = trip.get_details().aggregate(Max('altitude'))['altitude__max']*2
                done_altitude_profile = True

    except TypeError:
        # bug for trips without date
        pass
    except UnboundLocalError:
        # no trips found
        pass
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

def statistics(request, year=None, month=None, day=None, week=None):

    month_format = '%m' 
    date_field = 'date'
    now = datetime.now()
    if not year:
        tt = strptime("%s-%s" % (now.year, now.month), '%s-%s' % ('%Y', month_format))
    elif not month:
        tt = strptime("%s-%s" % (now.year, now.month), '%s-%s' % ('%Y', month_format))
    else:
        tt = strptime("%s-%s" % (year, month), '%s-%s' % ('%Y', month_format))
    date = datetimedate(*tt[:3])
    allow_future = True

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
    
    # Calculate the next month, if applicable.
    if allow_future:
        next_month = last_day
    elif last_day <= date.today():
        next_month = last_day
    else:
        next_month = None

    # Calculate the previous month
    if first_day.month == 1:
        previous_month = first_day.replace(year=first_day.year-1,month=12)
    else:
        previous_month = first_day.replace(month=first_day.month-1)


    if year:
        datefilter = {"user__exercise__date__year": year}
        if month:
            datefilter["user__exercise__date__month"] = month
            if day:
                datefilter["user__exercise__date__day"] = day
        if week:
            tt = strptime(year+'-1-' + str(int(week)-1), '%Y-%w-%W')
            date = datetimedate(*tt[:3])
            first_day = date
            last_day = date + timedelta(days=7)
            datefilter= {"user__exercise__date__gte":  first_day, 'user__exercise__date__lt': last_day}
    else:
        # silly, but can't find a suitable noop for filter, and ** can't unpack
        # empty dict into zero arguments - wah
        dummystart = datetime(1970,1,1)
        datefilter = { "user__exercise__date__gte": dummystart }

    teamname = request.GET.get('team')
    statsprofiles = Profile.objects.all()
    if teamname:
        team = get_object_or_404(Tribe, slug=teamname)
        statsusers = team.members.all()
        statsprofiles = statsprofiles.filter(user__in=statsusers)

    exercisename = request.GET.get('exercise')

    if exercisename:
        exercise = get_object_or_404(ExerciseType, name=exercisename)
    else:
        exercise = get_object_or_404(ExerciseType, name='Cycling')

    exercisefilter = { "user__exercise__exercise_type": exercise }
    datefilter["user__exercise__exercise_type"] = exercise

    tfilter = {}
    tfilter.update(exercisefilter)
    tfilter.update(datefilter)
    stats_dict = Exercise.objects.filter(**tfilter).aggregate(Max('avg_speed'), Avg('avg_speed'), Avg('route__distance'), Max('route__distance'), Sum('route__distance'), Avg('duration'), Max('duration'), Sum('duration'))
    total_duration = stats_dict['duration__sum']
    total_distance = stats_dict['route__distance__sum']
    total_avg_speed = stats_dict['avg_speed__avg']
    longest_trip = stats_dict['route__distance__max']
    if not total_duration:
        return HttpResponse('No trips found')

    exercise_count = Exercise.objects.all().count()

    userstats = statsprofiles.filter(**tfilter).annotate( \
            avg_avg_speed = Avg('user__exercise__avg_speed'), \
            max_avg_speed = Max('user__exercise__avg_speed'), \
            max_speed = Max('user__exercise__max_speed'), \
            num_trips = Count('user__exercise'), \
            sum_distance = Sum('user__exercise__route__distance'), \
            sum_duration = Sum('user__exercise__duration'), \
            sum_energy = Sum('user__exercise__kcal'), \
            sum_ascent = Sum('user__exercise__route__ascent'), \
            avg_avg_hr = Avg('user__exercise__avg_hr') \
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

    routefilter = {"ascent__gt" : 0, "distance__gt" : 0 }
    validroutes = Route.objects.filter(**routefilter)

    tfilter["user__exercise__route__in"] = validroutes
    climbstats = statsprofiles.filter(**tfilter).annotate( \
            distance = Sum('user__exercise__route__distance'), \
            height = Sum('user__exercise__route__ascent'),  \
            duration = Sum('user__exercise__duration'), \
            trips = Count('user__exercise') \
            ).filter(duration__gt=0).filter(distance__gt=0).filter(height__gt=0).filter(trips__gt=0)

    for u in climbstats:
        u.avgclimb = u.height/u.distance
        u.avgclimbperhour = u.height/(float(u.duration)/10**6/3600)
        u.avglen = float(u.distance)/u.trips
    climbstats = sorted(climbstats, key=lambda x: -x.avgclimb)
    climbstatsbytime = sorted(climbstats, key=lambda x:-x.avgclimbperhour)
    lengthstats = sorted(climbstats, key=lambda x: -x.avglen)

#    hikestats = statsprofiles.filter(**hikefilter).annotate( \
#            hike_avg_avg_speed = Avg('user__hike__avg_speed'), \
#            hike_max_avg_speed = Max('user__hike__avg_speed'), \
#            hike_max_speed = Max('user__hike__max_speed'), \
#            hike_num_trips = Count('user__hike'), \
#            hike_sum_distance = Sum('user__hike__route__distance'), \
#            hike_sum_duration = Sum('user__hike__duration'), \
#            hike_sum_energy = Sum('user__hike__kcal'), \
#            hike_sum_ascent = Sum('user__hike__route__ascent'), \
#            hike_avg_avg_hr = Avg('user__hike__avg_hr') \
#            )

#    hike_maxavgspeeds = hikestats.filter(hike_max_avg_speed__gt=0.0).order_by('hike_max_avg_speed').reverse()
#    hike_maxspeeds = hikestats.filter(hike_max_speed__gt=0.0).order_by('hike_max_speed').reverse()
#    hike_avgspeeds = hikestats.filter(hike_avg_avg_speed__gt=0.0).order_by('hike_avg_avg_speed').reverse()
#    hike_numtrips = hikestats.filter(hike_num_trips__gt=0).order_by('hike_num_trips').reverse()
#    hike_distsums = hikestats.filter(hike_sum_distance__gt=0).order_by('hike_sum_distance').reverse()
#    hike_dursums = hikestats.filter(hike_sum_duration__gt=0).order_by('hike_sum_duration').reverse()
#    hike_energysums = hikestats.filter(hike_sum_energy__gt=0).order_by('hike_sum_energy').reverse()
#    hike_ascentsums = hikestats.filter(hike_sum_ascent__gt=0).order_by('hike_sum_ascent').reverse()
#    hike_avgavghrs = hikestats.filter(hike_avg_avg_hr__gt=0).filter(max_hr__gt=0)

#    for u in hike_avgavghrs:
#        u.avgavghrpercent = float(u.hike_avg_avg_hr)/u.max_hr*100
#    hike_avgavghrs = sorted(hike_avgavghrs, key=lambda x:-x.avgavghrpercent)
#
#    hike_climbstats = statsprofiles.filter(**hikefilter).filter(user__hike__route__in=validroutes).annotate( \
#            distance = Sum('user__hike__route__distance'), \
#            height = Sum('user__hike__route__ascent'), \
#            duration = Sum('user__hike__duration'), \
#            hikes = Count('user__hike') \
#            ).filter(duration__gt=0).filter(distance__gt=0).filter(height__gt=0).filter(hikes__gt=0)

#    for u in hike_climbstats:
#        u.avgclimb = u.height/u.distance
#        u.avgclimbperhour = u.height/(float(u.duration)/10**6/3600)
#        u.avglen = float(u.distance)/u.hikes
#    hike_climbstats = sorted(hike_climbstats, key=lambda x: -x.avgclimb)
#    hike_climbstatsbytime = sorted(hike_climbstats, key=lambda x:-x.avgclimbperhour)
#    hike_lengthstats = sorted(hike_climbstats, key=lambda x: -x.avglen)

    team_list = Tribe.objects.all()

    return render_to_response('turan/statistics.html', locals(), context_instance=RequestContext(request))


def hr2zone(hr_percent):
    ''' Given a HR percentage return sport zone based on Olympiatoppen zones'''

    zone = 0

    if hr_percent > 97:
        zone = 6
    elif hr_percent > 92:
        zone = 5
    elif hr_percent > 87:
        zone = 4
    elif hr_percent > 82:
        zone = 3
    elif hr_percent > 72:
        zone = 2
    elif hr_percent > 60:
        zone = 1

    return zone

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


def calendar(request):
    now = datetime.now()
    return calendar_month(request, now.year, now.month)

def calendar_month(request, year, month):
    ''' the calendar view, some code stolen from archive_month generic view '''

    month_format = '%m' 
    allow_future = True
    date_field = 'date'
    tt = strptime("%s-%s" % (year, month), '%s-%s' % ('%Y', month_format))
    date = datetimedate(*tt[:3])
    now = datetime.now()


    # Calculate first and last day of month, for use in a date-range lookup.
    first_day = date.replace(day=1)
    start_delta = timedelta(days=first_day.weekday())
    start_of_week = first_day - start_delta
    week_start = [start_of_week + timedelta(days=i) for i in range(7)][0]

    if first_day.month == 12:
        last_day = first_day.replace(year=first_day.year + 1, month=1)
    else:
        last_day = first_day.replace(month=first_day.month + 1)

    start_delta = timedelta(days=last_day.weekday())
    start_of_week = last_day - start_delta
    week_end = [start_of_week + timedelta(days=i) for i in range(7)][-1]
    lookup_kwargs = {
        '%s__gte' % date_field: week_start,
        '%s__lt' % date_field: week_end,
    }

    # Only bother to check current date if the month isn't in the past and future objects are requested.
    if last_day >= now.date() and not allow_future:
        lookup_kwargs['%s__lte' % date_field] = now


    # Do explicit select_related on route since it can be null, and then select_related does not work by default
    exercices = Exercise.objects.select_related('route', 'exercise_type', 'user').order_by('date').filter(**lookup_kwargs)
    # Filter by username
    username = request.GET.get('username', '')
    if username:
        user = get_object_or_404(User, username=username)
        exercices = exercices.filter(user=user)

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



   # FIXME django locale
    # stupid calendar needs int
    year, month = int(year), int(month)
    cal = WorkoutCalendar(exercices, locale.getdefaultlocale()).formatmonth(year, month)

    e_by_week = [(week, list(items)) for week, items in groupby(exercices, lambda workout: int(workout.date.strftime('%W')))]


    return render_to_response('turan/calendar.html',
            {'calendar': mark_safe(cal),
             'months': months,
             'username': username,
             'previous_month': previous_month,
             'next_month': next_month,
             'e_by_week': e_by_week,
             },
            context_instance=RequestContext(request))

def powerjson(request, object_id):

    object = get_object_or_404(Exercise, pk=object_id)

    start, stop = request.GET.get('start', ''), request.GET.get('stop', '')
    start, stop = int(start), int(stop)
    all_details = object.get_details()

    details = list(all_details.all()[start:stop])
    ascent, descent = calculate_ascent_descent_gaussian(details)

    #ret = object.get_details().all()[start:stop].aggregate( Avg('speed'), Avg('hr'), Avg('cadence'), Avg('power'), Min('speed'), Min('hr'), Min('cadence'), Min('power'), Max('speed'), Max('hr'), Max('cadence'), Max('power'))

    val_types = ('speed', 'hr', 'cadence', 'power')
    ret = {
            'speed__min': 9999,
            'hr__min': 9999,
            'cadence__min': 9999,
            'power__min': 9999,
            'speed__max': 0,
            'hr__max': 0,
            'cadence__max': 0,
            'power__max': 0,
            'speed__avg': 0,
            'hr__avg': 0,
            'cadence__avg': 0,
            'power__avg': 0,
    }
    for d in details:
        for val in val_types:
            ret[val+'__min'] =  min(ret[val+'__min'], getattr(d, val))
            ret[val+'__max'] = max(ret[val+'__max'], getattr(d, val))
            if getattr(d, val):
                ret[val+'__avg'] += getattr(d, val)
    for val in val_types:
        ret[val+'__avg'] = ret[val+'__avg']/len(details)

    ret['ascent'] = ascent
    ret['descent'] = descent

    details = list(details)

    if filldistance(details):
        #Shit that only works for distance, like power
        distance = details[-1].distance - details[0].distance
        gradient = ascent/distance
        duration = (details[-1].time - details[0].time).seconds
        speed = ret['speed__avg']
        userweight = object.user.get_profile().get_weight(object.date)

        # EQweight hard coded to 10! 
        ret['power__avg_est'] = calcpower(userweight, 10, gradient*100, speed/3.6)
        ret['duration'] = duration
        ret['distance'] = distance
        ret['gradient'] = gradient*100
    for a, b in ret.items():
        # Do not return empty values
        if not b:
            del ret[a]
    return HttpResponse(simplejson.dumps(ret), mimetype='application/json')

#@decorator_from_middleware(GZipMiddleware)
#@cache_page(86400*7)
def geojson(request, object_id):
    ''' Return GeoJSON with coords as linestring for use in openlayers stylemap,
    give each line a zone property so it can be styled differently'''

    qs = ExerciseDetail.objects.filter(exercise=object_id)
    qs = list(qs.exclude(lon=0).exclude(lat=0))

    start, stop = request.GET.get('start', ''), request.GET.get('stop', '')
    if start and stop:
        start, stop = int(start), int(stop)
        qs = qs[start:stop]

    if len(qs) == 0:
        return HttpResponse('{}')

    max_hr = qs[0].exercise.user.get_profile().max_hr

    class Feature(object):

        linestrings = []

        def __init__(self, zone):
            self.jsonhead = '''
            { "type": "Feature", "properties":
                { "ZONE": %s },
                "geometry": {
                    "type": "LineString", "coordinates": [ ''' %zone
            self.jsonfoot = '''] }
            },'''

        def addLine(self, a, b, c, d):
            self.linestrings.append('[%s,%s],[%s,%s],' %(a,b,c,d))

        @property
        def json(self):
            if not self.linestrings:
                # Don't return empty feature
                return ''
            return self.jsonhead + ''.join(self.linestrings) + self.jsonfoot

    features = []

    previous_lon, previous_lat, previous_zone = 0, 0, 0
    previous_feature = False
    for d in qs:
        if previous_lon and previous_lat:
            hr_percent = float(d.hr)*100/max_hr
            zone = hr2zone(hr_percent)
            if zone == 0: # TODO WTF? Bug in this shit
                zone = 1

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
    gjstr += ','.join([f.json for f in features])
    gjstr += gjfoot

    return HttpResponse(gjstr, mimetype='text/javascript')

def tripdetail_js(event_type, object_id, val, start=False, stop=False):
    if start:
        start = int(start)
    if stop:
        stop = int(stop)

    qs = ExerciseDetail.objects.filter(exercise=object_id)

    x = 0
    distance = 0
    previous_time = False
    js = ''
    for i, d in enumerate(qs.all().values('time', 'speed', val)):
        if start and start < i:
            continue
        if stop and i > stop:
            break
        if not previous_time:
            previous_time = d['time']
        time = d['time'] - previous_time
        previous_time = d['time']
        distance += ((d['speed']/3.6) * time.seconds)/1000
        # time_xaxis = x += float(time.seconds)/60
        dval = d[val]
        if dval > 0: # skip zero values (makes prettier graph)
            js += '[%.4f,%s],' % (distance, dval)
    return js

def js_trip_series(request, details,  start=False, stop=False, time_xaxis=True, use_constraints=True):
    ''' Generate javascript to be used directly in flot code
    Argument use_constraints can be used to disable flot constraints for HR, used for compare feature '''

    if not details:
        return

    # The JS arrays
    js_strings = {
            'speed': [],
            'power': [],
            'poweravg30s': [],
            'altitude': [],
            'cadence': [],
            'hr': [],
            'index': [],
        }

    x = 0
    previous_time = False

    exercise = details[0].exercise
    # User always has permission for their own shit
    if not exercise.user == request.user:

        is_friend = False
        if request.user.is_authenticated():
            is_friend = Friendship.objects.are_friends(request.user, exercise.user)
        # Check for permission to display attributes
        try:
            # Try to find permission object for this exercise
            permission = exercise.exercisepermission

            for val in js_strings.keys():
                # Can't remove altitude for example 
                if hasattr(permission, val):
                    permission_val = getattr(permission, val)
                    if permission_val == 'A':
                        continue
                    elif permission_val == 'F' and is_friend:
                        continue
                    else: #'N' or not friends
                        del js_strings[val]
                        if val == 'power':
                            # we don't store poweravg30s in db, but if you cant see power you shouldn't see that
                            del js_strings['poweravg30s']

        except ExercisePermission.DoesNotExist:
            # No permissionojbect found
            pass

# Check if we should export altitude to graph
    has_altitude = details[0].exercise.exercise_type.altitude
    if not has_altitude:
        del js_strings['altitude']

    for i, d in enumerate(details):
        if start and start < i:
            continue
        if stop and i > stop:
            break
        if not previous_time:
            previous_time = d.time
        time = d.time - previous_time
        previous_time = d.time
        if not time_xaxis:
            x += ((d.speed/3.6) * time.seconds)/1000
        else:
            x += float(time.seconds)/60

        for val in js_strings.keys():
            try:
                if val == 'index':
                    js_strings['index'] += '%.4f,' % (x)

                dval = getattr(d, val)
                if dval > 0: # skip zero values (makes prettier graph)
                    js_strings[val] += '[%.4f,%s],' % (x, dval)

            except AttributeError: # not all formats support all values
                pass


    # Convert lists into strings
    for val in js_strings.keys():
        js_strings[val] = ''.join(js_strings[val])

    t = loader.get_template('turan/js_datasets.js')
    js_strings['use_constraints'] = use_constraints
    c = Context(js_strings)
    js = t.render(c)

    return js

def json_tripdetail(request, event_type, object_id, val, start=False, stop=False):

    #response = HttpResponse()
    #serializers.serialize('json', qs, fields=('id', val), indent=4, stream=response)
    js = tripdetail_js(event_type, object_id, val, start, stop)
    return HttpResponse(js)

def getinclinesummary(values):
    inclines = SortedDict({
        -1: 0,
        0: 0,
        1: 0,
        })

    previous_time = False
    previous_altitude = 0
    for d in values:
        if not previous_time:
            previous_time = d.time
            continue
        time = d.time - previous_time
        previous_time = d.time
        if time.seconds > 60:
            continue


        if d.altitude == previous_altitude:
            inclines[0] += time.seconds
        elif d.altitude > previous_altitude:
            inclines[1] += time.seconds
        elif d.altitude < previous_altitude:
            inclines[-1] += time.seconds

        previous_altitude = d.altitude

    return inclines

def getzones(values):
    ''' Calculate time in different sport zones given trip details '''

    max_hr = values[0].exercise.user.get_profile().max_hr
    if not max_hr:
        return []

    zones = SortedDict({
            0: 0,
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            6: 0,
        })
    previous_time = False
    for i, d in enumerate(values):
        if not previous_time:
            previous_time = d.time
            continue
        time = d.time - previous_time
        previous_time = d.time
        if time.seconds > 60:
            continue
        hr_percent = 0
        if d.hr:
            hr_percent = float(d.hr)*100/max_hr
        zone = hr2zone(hr_percent)
        zones[zone] += time.seconds

    zones_with_legend = SortedDict()

    for zone, val in zones.items():
        if zone == 0:
            zones_with_legend['0 (0% - 60%)'] = val
        elif zone == 1:
            zones_with_legend['1 (60% - 72%)'] = val
        elif zone == 2:
            zones_with_legend['2 (72% - 82%)'] = val
        elif zone == 3:
            zones_with_legend['3 (82% - 87%)'] = val
        elif zone == 4:
            zones_with_legend['4 (87% - 92%)'] = val
        elif zone == 5:
            zones_with_legend['5 (92% - 97%)'] = val
        elif zone == 6:
            zones_with_legend['6 (97% - 100%'] = val

    return zones_with_legend

def gethrhzones(values):
    ''' Calculate time in different sport zones given trip details '''

    max_hr = values[0].exercise.user.get_profile().max_hr
    #resting_hr = values[0].exercise.user.get_profile().resting_hr
    if not max_hr: #or not resting_hr:
        return []

    zones = SortedDict()
    previous_time = False
    for i, d in enumerate(values):
        if not previous_time:
            previous_time = d.time
            continue
        time = d.time - previous_time
        previous_time = d.time
        if time.seconds > 60:
            continue
        hr_percent = 0
        if d.hr:
            hr_percent = int(round(float(d.hr)*100/max_hr))
        #hr_percent = (float(d.hr)-resting_hr)*100/(max_hr-resting_hr)
        if not hr_percent in zones:
            zones[hr_percent] = 0
        zones[hr_percent] += time.seconds

    filtered_zones = [SortedDict(),SortedDict(),SortedDict(),SortedDict(),SortedDict(),SortedDict(),SortedDict()]
    #for i in range(40,100):
    #    filtered_zones[i] = 0

    if d.exercise.duration:
        total_seconds = d.exercise.duration.seconds
        for hr in sorted(zones):
            #if 100*float(zones[hr])/total_seconds > 0:
            if hr > 40 and hr < 101:
                percentage = float(zones[hr])*100/total_seconds
                if percentage > 0.5:

                    zone = hr2zone(hr)
                    filtered_zones[zone][hr] = percentage

    return filtered_zones

def getgradients(values):
    ''' Iterate over details, return list with tuples with distances and gradients '''

    altitudes = []
    distances = []
    inclinesums = {}


    for d in values:
        altitudes.append(d.altitude)
        # Distances is used in the graph, so divide by 1000 to get graph xasis in km
        distances.append(d.distance/1000)

    # Smooth 10 Wide!
    altitudes = smoothListGaussian(altitudes, 10)

    gradients = []
    previous_altitude = 0
    previous_distance = 0
    for i, d in enumerate(distances):
        if previous_distance:

            h_delta = altitudes[i] -  previous_altitude
            d_delta = d*1000 - previous_distance
            if d_delta:
                gradient = h_delta*100/d_delta
                if gradient < 50 and gradient > -50:
                    gradients.append(gradient)
                    roundedgradient = int(round(gradient))
                    if not roundedgradient in inclinesums:
                        inclinesums[roundedgradient] = 0
                    inclinesums[roundedgradient] += d_delta/1000

        previous_altitude = altitudes[i]
        previous_distance = d*1000

    if gradients: # Don't try to smooth empty list
        gradients = smoothListGaussian(gradients)


    # Clean values to reduce clutter
    # and round distance values
    cutoff = 1 # 1 km
    inclinesums = dict((k, round(v, 1)) for k, v in inclinesums.items() if v >= 1)
    # sort the dictionary on gradient
    inclinesums = [ (k,inclinesums[k]) for k in sorted(inclinesums.keys())]

    return zip(distances, gradients), inclinesums

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
            try:
                if (values[i+1].time - values[i].time).seconds > 60:
                    stop_duration = max( \
                            (values[i+1].time - values[i].time).seconds, \
                            stop_duration )
            except IndexError:
                pass
            if values[i].altitude < values[cur_start].altitude + hdelta*0.9 \
                    or i == len(values)-1 \
                    or stop_duration > 60:
                if stop_duration > 60:
                    cur_stop = stop_since
                inslope = False
                if hdelta >= min_slope:
                    distance = values[cur_end].distance - values[cur_start].distance
                    if distance > 10:
                        slopes.append(Slope(cur_start, cur_end, distance, hdelta, hdelta/distance * 100, values[cur_start].distance/1000))
                cur_start = i+1
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
    return d

def getavghr(values, start, end):
    hr = 0
    for i in xrange(start+1, end+1):
        delta_t = (values[i].time - values[i-1].time).seconds
        if values[i].hr:
            hr += values[i].hr*delta_t
    delta_t = (values[end].time - values[start].time).seconds
    return float(hr)/delta_t

def getavgpwr(values, start, end):
    pwr = 0
    for i in xrange(start+1, end+1):
        delta_t = (values[i].time - values[i-1].time).seconds
        try:
            pwr += values[i].power*delta_t
        except TypeError:
            return None
    delta_t = (values[end].time - values[start].time).seconds
    return float(pwr)/delta_t

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

#@profile("exercise_detail")
def exercise(request, object_id):
    ''' View for exercise detail '''

    object = get_object_or_404(Exercise, pk=object_id)

    # Permission checks
    power_show = True
    poweravg30_show = True
    if not object.user == request.user:  # Allow self
        is_friend = False
        if request.user.is_authenticated():
            is_friend = Friendship.objects.are_friends(request.user, object.user)
        if object.exercise_permission == 'N':
            return redirect_to_login(request.path)
        elif object.exercise_permission == 'F':
            if not is_friend:
                return redirect_to_login(request.path)

        # Check for permission to display attributes
        try:
            # Try to find permission object for this exercise
            permission = object.exercisepermission

            if hasattr(permission, "power"):
                permission_val = getattr(permission, "power")
                if permission_val == 'A':
                    power_show = True
                elif permission_val == 'F' and is_friend:
                    power_show = True
                else: #'N' or not friends
                    power_show = False
            if hasattr(permission, "poweravg30s"):
                permission_val = getattr(permission, "poweravg30s")
                if permission_val == 'A':
                    poweravg30_show = True
                elif permission_val == 'F' and is_friend:
                    poweravg30_show = True
                else: #'N' or not friends
                    poweravg30_show = False
        except ExercisePermission.DoesNotExist:
            # No permissionobject found
            # Allowed to see.
            pass

    # Provide template string for maximum yaxis value for HR, for easier comparison
    maxhr_js = ''
    if object.user.get_profile().max_hr:
        max_hr = int(object.user.get_profile().max_hr)
        maxhr_js = ', max: %s' %max_hr
    else:
        max_hr = 200 # FIXME, maybe demand from user ?

    details = object.exercisedetail_set.all()
    # Default is false, many exercises don't have distance, we try to detect later
    time_xaxis = True
    if details:
        if filldistance(details): # Only do this if we actually have distance
            # xaxis by distance if we have distance in details unless user requested time !
            req_t = request.GET.get('xaxis', '')
            if not req_t == 'time':
                time_xaxis = False
            userweight = object.user.get_profile().get_weight(object.date)
            slopes = getslopes(details)
            for slope in slopes:
                slope.duration = details[slope.end].time - details[slope.start].time
                slope.speed = slope.length/slope.duration.seconds * 3.6
                slope.avg_hr = getavghr(details, slope.start, slope.end)
                slope.avg_power = calcpower(userweight, 10, slope.gradient, slope.speed/3.6)
                slope.actual_power = getavgpwr(details, slope.start, slope.end)
                try:
                    if slope.actual_power:
                        slope.avg_power_kg = slope.actual_power / userweight
                    else:
                        slope.avg_power_kg = slope.avg_power / userweight
                except ZeroDivisionError:
                    slope.avg_power_kg = 0


            gradients, inclinesums = getgradients(details)

        zones = getzones(details)
        hrhzones = gethrhzones(details)
        #inclinesummary = getinclinesummary(details)

        if object.avg_power and power_show:
            object.normalized = power_30s_average(details)
            #for i in range(0, len(poweravg30s)):
            #    details[i].poweravg30s = poweravg30s[i]
            #object.normalized = normalized_power(poweravg30s)

    datasets = js_trip_series(request, details, time_xaxis=time_xaxis)

    return render_to_response('turan/exercise_detail.html', locals(), context_instance=RequestContext(request))

def json_serializer(request, queryset, root_name = None, relations = (), extras = ()):
    if root_name == None:
        root_name = queryset.model._meta.verbose_name_plural
    #hardcoded relations and extras while testing
    return HttpResponse(serializers.serialize('json', queryset, indent=4, relations=relations, extras=extras), mimetype='text/javascript')


def create_exercise_with_route(request):
    ''' Formset for exercise with permission and route inline '''

    if not request.user.is_authenticated():
        return redirect_to_login(request.path)
    ExerciseFormSet = inlineformset_factory(Exercise, ExercisePermission, form=ExerciseForm)

    if request.method == 'POST':
        form = ExerciseFormSet(request.POST, request.FILES)
        if form.is_valid():
            new_object = form.save(commit=False)
            if user_required:
                new_object.user = request.user
            if profile_required:
                new_object.userprofile = request.user.get_profile()
            new_object.save()

            # notify friends of new object
            if notification and user_required: # only notify for user owned objects
                notification.send(friend_set_for(request.user.id), 'exercise_create', {'sender': request.user, 'exercise': new_object}, [request.user])


            if request.user.is_authenticated():
                request.user.message_set.create(message=ugettext("The %(verbose_name)s was created successfully.") % {"verbose_name": Exercise._meta.verbose_name})
            return redirect(post_save_redirect, new_object)
    else:
        form = ExerciseFormSet()

    return render_to_response('turan/exercise_form.html', locals(), context_instance=RequestContext(request))

def create_object(request, model=None, template_name=None,
        template_loader=loader, extra_context=None, post_save_redirect=None,
        login_required=False, context_processors=None, form_class=None, user_required=False, profile_required=False):
    """
    Based on Generic object-creation function. 
    Modified for turan to always save user to model

    new parameters:
        * user_required: if the form needs user set to request.user
        * profile_required: if the form needs userprofile set to current user's profile
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
            if profile_required:
                new_object.userprofile = request.user.get_profile()
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

    latitude = request.GET.get('lat', '')
    longitude = request.GET.get('lon', '')

    if latitude and longitude:
        # A litle aprox box around your area
        queryset = queryset.filter(start_lat__gt=float(latitude) - 0.5)
        queryset = queryset.filter(start_lat__lt=float(latitude) + 0.5)
        queryset = queryset.filter(start_lon__gt=float(longitude) - 1.0)
        queryset = queryset.filter(start_lon__lt=float(longitude) + 1.0)

    username = request.GET.get('username', '')
    if username:
        user = get_object_or_404(User, username=username)
        queryset = queryset.filter(user=user)

    return object_list(request, queryset=queryset, extra_context=locals())


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


def ical(request, username):

    cal = ExerciseCalendar(username)

    return cal()

def turan_delete_object(request, model=None, post_delete_redirect='/turan/', object_id=None,
        slug=None, slug_field='slug', template_name=None,
        template_loader=loader, extra_context=None, login_required=False,
        context_processors=None, template_object_name='object'):
    ''' See django's generic view docs for help. This specific checks that a user is deleting his own objects'''


    obj = lookup_object(model, object_id, slug, slug_field)
    if not obj.user == request.user:
        return HttpResponseForbidden('Wat?')

    return delete_object(request, model, post_delete_redirect, object_id, login_required=login_required)

def turan_delete_detailset_value(request, model, object_id, value=False):
    ''' Delete value from exercise, like remove altitude from a spinning session '''


    obj = lookup_object(model, object_id, None, 'slug')
    if not obj.user == request.user:
        return HttpResponseForbidden('Wat?')

    for detail in obj.get_details().all():
        setattr(detail, value, 0)
        detail.save()

    return HttpResponseRedirect(obj.get_absolute_url())

class ImportForm(forms.Form):
    import_url = forms.CharField(label='Url to external exercise', required=True)

@login_required
def import_data(request):
    if request.method == 'POST':
        form = ImportForm(request.POST)
        url = form.data['import_url']
        if form.is_valid():
            # Sportypal
            id = 0
            # Support only route import for now
            if url.find("http://sportypal.com/Workouts/Details/") == 0:
                id = url.split("/")[-1].rstrip("/")
                url = "http://sportypal.com/Workouts/ExportGPX?workout_id=" + id

                if id > 0:
                    route = Route()
                    content = ContentFile(urlopen(url).read())

                    route.gpx_file.save("gpx/sporty_" + id + ".gpx", content)
                    form.save()

                    return HttpResponseRedirect(route.get_absolute_url())
                else:
                    raise Http404

            # Supports both route and exercise import
            elif url.find("http://connect.garmin.com/activity/") == 0:
                base_url = "http://connect.garmin.com"
                id = url.split("/")[-1].rstrip("/")

                tripdata = urlopen(url).read()
                tripsoup = BeautifulSoup(tripdata, convertEntities=BeautifulSoup.HTML_ENTITIES)

                gpx_url = tripsoup.find(id="actionGpx")['href']
                tcx_url = tripsoup.find(id="actionTcx")['href']

                route_name = tripsoup.find(id="activityName")
                if route_name.string:
                    route_name = route_name.string.strip()
                else:
                    route_name = "Unnamed"

                exercise_description = tripsoup.find(id="discriptionValue")
                if exercise_description.string:
                    exercise_description = exercise_description.string.strip()
                else:
                    exercise_description = None

                route = None

                if gpx_url:
                    route = Route()
                    content = ContentFile(urlopen(base_url + gpx_url).read())
                    route.gpx_file.save("gpx/garmin_connect_" + id + ".gpx", content)
                    route.name = route_name
                    route.save()

                if tcx_url:
                    content = ContentFile(urlopen(base_url + tcx_url).read())
                    exercise_filename = 'sensor/garmin_connect_' + id + '.tcx'

                    exercise = Exercise()
                    exercise.user = request.user
                    exercise.sensor_file.save(exercise_filename, content)
                    if exercise_description:
                        exercise.comment = exercise_description
                    if route:
                        exercise.route = route
                    exercise.save()

                return render_to_response("turan/import_stage2.html", {'route': route, 'exercise': exercise}, context_instance=RequestContext(request))
    else:
        form = ImportForm()

    return render_to_response("turan/import.html", {'form': form}, context_instance=RequestContext(request))

def power_30s_average(details):

    datasetlen = len(details)


    # FIXME implement for non 1 sec sample, for now return blank
    sample_len = (details[1].time - details[0].time).seconds
    if sample_len > 1:
        return 0

    normalized = 0.0
    fourth = 0.0
    power_avg_count = 0

    #EXPECTING 1 SEC SAMPLE INTERVAL!
    for i in xrange(0, datasetlen):
        foo = 0.0
        foo_element = 0.0
        for j in xrange(0,30):
            if (i+j-30) > 0 and (i+j-30) < datasetlen:
                delta_t = (details[i+j-30].time - details[i+j-31].time).seconds
                # Break if exerciser is on a break as well
                if delta_t < 60:
                    foo += details[i+j-30].power*delta_t
                    foo_element += 1.0
                else:
                    foo = 0
                    foo_element = 0.0
                    break
        if foo_element:
            poweravg30s = foo/foo_element
            details[i].poweravg30s = poweravg30s
            fourth += pow(poweravg30s, 4)
            power_avg_count += 1


    normalized = int(round(pow((fourth/power_avg_count), (0.25))))
    return normalized

