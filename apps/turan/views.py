from models import *
from tasks import smoothListGaussian, calcpower, power_30s_average \
        , hr2zone, detailslice_info, search_trip_for_possible_segments_matches
from itertools import groupby, islice
from forms import ExerciseForm
from profiles.models import Profile
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, HttpResponsePermanentRedirect, HttpResponseForbidden, Http404, HttpResponseServerError
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.template import RequestContext, Context, loader
from django.contrib.auth.decorators import login_required
from django.utils.text import compress_string

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
from django.views.decorators.gzip import gzip_page
from django.utils.datastructures import SortedDict
from django.middleware.gzip import GZipMiddleware

from django.core.files.base import ContentFile
from turan.models import Route
from turan.middleware import Http403
from tempfile import NamedTemporaryFile
import urllib2
import cookielib
import urllib
import os

from BeautifulSoup import BeautifulSoup

from tagging.models import Tag
from tribes.models import Tribe
from friends.models import Friendship
from wakawaka.models import WikiPage, Revision

import re
from datetime import timedelta, datetime
from datetime import date as datetimedate
from time import mktime, strptime
import locale

from svg import GPX2SVG
from turancalendar import WorkoutCalendar
from feeds import ExerciseCalendar

import simplejson
#from simplejson import encoder
#encoder.c_make_encoder = None
#encoder.FLOAT_REPR = lambda o: format(o, '.4f')

from profiler import profile

from celery.result import AsyncResult

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

    exercise_list = Exercise.objects.select_related('route', 'tagging_tag', 'tagging_taggeditem', 'exercise_type', 'user__profile', 'user', 'user__avatar', 'avatar')[:10]
    comment_list = ThreadedComment.objects.filter(is_public=True).order_by('-date_submitted')[:5]

    route_list = Route.objects.extra( select={ 'tcount': 'SELECT COUNT(*) FROM turan_exercise WHERE turan_exercise.route_id = turan_route.id' }).extra( order_by= ['-tcount',])[:12]
    #route_list = sorted(route_list, key=lambda x: -x.exercise_set.count())[:15]

    tag_list = Tag.objects.cloud_for_model(Exercise)

    # Top exercisers last 14 days
    today = datetimedate.today()
    days = timedelta(days=14)
    begin = today - days
    user_list = User.objects.filter(exercise__date__range=(begin, today)).annotate(Sum('exercise__duration')).exclude(exercise__duration__isnull=True).order_by('-exercise__duration__sum')

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
    title = "lart.no turan exercises"
    link = "http://turan.no/turan/"
    description = "Exercises from turan.no/turan"

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
    object_list = object.get_trips()
    try:
        done_altitude_profile = False
        for trip in sorted(object_list, key=lambda x:x.date):
            if not trip.user in usertimes:
                usertimes[trip.user] = ''
            try:
                time = trip.duration.seconds/60
                if trip.avg_speed: # Or else graph bugs with None-values
                    usertimes[trip.user] += mark_safe('[%s, %s],' % (datetime2jstimestamp(trip.date), trip.avg_speed))
            except AttributeError:
                pass # stupid decimal value in trip duration!

            if trip.avg_speed and trip.get_details().exists() and not done_altitude_profile: # Find trip with speed or else tripdetail_js bugs out
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

def segment_detail(request, object_id):
    object = get_object_or_404(Segment, pk=object_id)
    usertimes = {}
    slopes = object.get_slopes().select_related('exercise', 'exercise__route', 'exercise__user__profile', 'segment', 'profile', 'exercise__user')
    for slope in sorted(slopes, key=lambda x:x.exercise.date):
        if not slope.exercise.user in usertimes:
            usertimes[slope.exercise.user] = ''
        time = slope.duration/60
        usertimes[slope.exercise.user] += mark_safe('[%s, %s],' % (datetime2jstimestamp(slope.exercise.date), slope.duration))

    done_altitude_profile = False
    if slopes:
        slope = slopes[0] # Select first detail for details for gradients and altitude profile, TODO: save in db
        trip = slope.exercise
        if trip.avg_speed and trip.get_details().count() and not done_altitude_profile: # Find trip with speed or else tripdetail_js bugs out

            tripdetails = trip.get_details().all()
            if filldistance(tripdetails):
                i = 0
                start, stop= 0, 0
                for d in tripdetails:
                    if d.distance >= slope.start*1000 and not start:
                        start = i
                    elif start:
                        if d.distance > (slope.start*1000 + slope.length):
                            stop = i
                            break
                    i += 1
            #start =  trip.get_details().filter(lon=slope.start_lon).filter(lat=slope.start_lat)[0].id
            #stop =  trip.get_details().filter(lon=slope.end_lon).filter(lat=slope.end_lat)[0].id
            #alt = tripdetail_js(None, trip.id, 'altitude', start=start, stop=stop)
            d_offset = tripdetails[start].distance
            alt = simplejson.dumps([((d.distance-d_offset)/1000, d.altitude) for d in tripdetails[start:stop]])
            alt_max = trip.get_details().aggregate(Max('altitude'))['altitude__max']*2
            done_altitude_profile = True
        gradients, inclinesums = getgradients(tripdetails[start:stop],d_offset=d_offset)
    return render_to_response('turan/segment_detail.html', locals(), context_instance=RequestContext(request))

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

    tfilter = {}
    if exercisename:
        exercise = get_object_or_404(ExerciseType, name=exercisename)
        exercisefilter = { "user__exercise__exercise_type": exercise }
        datefilter["user__exercise__exercise_type"] = exercise
        tfilter.update(exercisefilter)
    tfilter.update(datefilter)
    #else:
    #    exercise = get_object_or_404(ExerciseType, name='Cycling')

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
            avg_normalized_power = Avg('user__exercise__normalized_power'), \
            max_max_power = Max('user__exercise__max_power'), \
            sum_ascent = Sum('user__exercise__route__ascent'), \
            avg_avg_hr = Avg('user__exercise__avg_hr'), \
            )

    maxavgspeeds = userstats.filter(max_avg_speed__gt=0.0).order_by('max_avg_speed').reverse()
    maxspeeds = userstats.filter(max_speed__gt=0.0).order_by('max_speed').reverse()
    avgspeeds = userstats.filter(avg_avg_speed__gt=0.0).order_by('-avg_avg_speed')
    numtrips = userstats.filter(num_trips__gt=0).order_by('num_trips').reverse()
    distsums = userstats.filter(sum_distance__gt=0).order_by('sum_distance').reverse()
    dursums = userstats.filter(sum_duration__gt=0).order_by('sum_duration').reverse()
    energysums = userstats.filter(sum_energy__gt=0).order_by('sum_energy').reverse()
    ascentsums = userstats.filter(sum_ascent__gt=0).order_by('sum_ascent').reverse()
    avgavghrs = userstats.filter(avg_avg_hr__gt=0).filter(max_hr__gt=0)
    avgnormalizedpower =  userstats.filter(avg_normalized_power__gt=0).order_by('-avg_normalized_power')
    maxpowers =  userstats.filter(max_max_power__gt=0).order_by('-max_max_power')

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
            height_sum = Sum('user__exercise__route__ascent'),  \
            duration = Sum('user__exercise__duration'), \
            trips = Count('user__exercise') \
            ).filter(duration__gt=0).filter(distance__gt=0).filter(height_sum__gt=0).filter(trips__gt=0)

    for u in climbstats:
        u.avgclimb = u.height_sum/u.distance
        u.avgclimbperhour = u.height_sum/(float(u.duration)/10**6/3600)
        u.avglen = float(u.distance)/u.trips
    climbstats = sorted(climbstats, key=lambda x: -x.avgclimb)
    climbstatsbytime = sorted(climbstats, key=lambda x:-x.avgclimbperhour)
    lengthstats = sorted(climbstats, key=lambda x: -x.avglen)

    hrzonestats = []
    hrzones = range(0,7)
    for i in hrzones:
        hrzonestats.append(statsprofiles.filter(**tfilter)\
        .extra(where=['turan_hrzonesummary.zone = %s' %i])\
        .annotate(\
            duration = Sum('user__exercise__hrzonesummary__duration')
            )\
        .order_by('-duration'))
    hrzonestats = zip(hrzones, hrzonestats)


    bestest_power = []
    intervals = [5, 10, 30, 60, 300, 600, 1200, 1800, 3600]
    for i in intervals:
        userweight_tmp = []
        #.filter(user__exercise__bestpowereffort__duration=i)\
        best_power_tmp = statsprofiles.filter(**tfilter)\
        .extra(where=['turan_bestpowereffort.duration = %s' %i])\
        .annotate( max_power = Max('user__exercise__bestpowereffort__power'))\
        .order_by('-max_power')
        for a in best_power_tmp:
            userweight_tmp.append(a.max_power/a.get_weight())#(a.exercise.date))
        bestest_power.append(zip(best_power_tmp, userweight_tmp))
    bestest_power = zip(intervals, bestest_power)

    team_list = Tribe.objects.all()

    return render_to_response('turan/statistics.html', locals(), context_instance=RequestContext(request))

def bestest(request):

    bestest_speed = []
    bestest_power = []
    intervals = [5, 30, 60, 300, 600, 1200, 1800, 3600]
    for i in intervals:
        userweight_tmp = []
        best_speed_tmp = BestSpeedEffort.objects.filter(exercise__exercise_type__name="Cycling", duration=i).order_by('-speed')[:10]
        for a in best_speed_tmp:
            userweight_tmp.append(a.exercise.user.get_profile().get_weight(a.exercise.date))
        bestest_speed.append(zip(best_speed_tmp, userweight_tmp))

        userweight_tmp = []
        best_power_tmp = BestPowerEffort.objects.filter(exercise__exercise_type__name="Cycling", duration=i).order_by('-power')[:10]
        for a in best_power_tmp:
            userweight_tmp.append(a.exercise.user.get_profile().get_weight(a.exercise.date))
        bestest_power.append(zip(best_power_tmp, userweight_tmp))

    bestest_speed = zip(intervals, bestest_speed)
    bestest_power = zip(intervals, bestest_power)
    return render_to_response('turan/bestest.html', locals(), context_instance=RequestContext(request))



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
    exercises = Exercise.objects.select_related('route', 'exercise_type', 'user').order_by('date').filter(**lookup_kwargs)
    # Filter by username
    username = request.GET.get('username', '')
    if username:
        user = get_object_or_404(User, username=username)
        exercises = exercises.filter(user=user)
    else:
        user = ''

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
    cal = WorkoutCalendar(exercises, locale.getdefaultlocale()).formatmonth(year, month)

    e_by_week = [(week, list(items)) for week, items in groupby(exercises, lambda workout: int(workout.date.strftime('%W')))]

    z_by_week = {}

    if username: # Only give zone week graph for individuals
        for week, es in e_by_week:
            zones =[0,0,0,0,0,0,0]
            dbzones = HRZoneSummary.objects.filter(exercise__in=es).values('zone').annotate(duration=Sum('duration'))
            for dbzone in dbzones:
                zones[dbzone['zone']] += dbzone['duration']
            z_by_week[week] = zones#[float(zone)/60/60 for zone in zones if zone]

    return render_to_response('turan/calendar.html',
            {'calendar': mark_safe(cal),
             'months': months,
             'username': username,
             'previous_month': previous_month,
             'next_month': next_month,
             'e_by_week': e_by_week,
             'z_by_week': z_by_week,
             'user': user,
             'year': year,
             'month': month,
             },
            context_instance=RequestContext(request))


def powerjson(request, object_id):

    object = get_object_or_404(Exercise, pk=object_id)

    start, stop = request.GET.get('start', ''), request.GET.get('stop', '')
    try:
        start, stop = int(start), int(stop)
    except ValueError:
        return {}
    all_details = object.get_details()

    details = all_details.all()[start:stop]
    d = filldistance(details) # FIXME

    ret = detailslice_info(details)

    return HttpResponse(simplejson.dumps(ret), mimetype='application/json')

def wikijson(request, slug, rev_id=None):
    '''
    JSON wiki page
    '''
    try:
        page = WikiPage.objects.get(slug=slug)
        rev = page.current

        # Display an older revision if rev_id is given
        if rev_id:
            rev_specific = Revision.objects.get(pk=rev_id)
            if rev.pk != rev_specific.pk:
                rev_specific.is_not_current = True
            rev = rev_specific

    except WikiPage.DoesNotExist:
        raise Http404

    return HttpResponse(serializers.serialize('json', [rev], indent=4), mimetype='text/javascript')

#@decorator_from_middleware(GZipMiddleware)
#@cache_page(86400*7)
#@profile("geojson")
def geojson(request, object_id):
    ''' Return GeoJSON with coords as linestring for use in openlayers stylemap,
    give each line a zone property so it can be styled differently'''

    qs = ExerciseDetail.objects.filter(exercise=object_id).exclude(lon=0).exclude(lat=0).filter(lon__isnull=False,lat__isnull=False,hr__isnull=False).values('hr','lon','lat')
    #qs = list(qs.exclude(lon=0).exclude(lat=0))

    start, stop = request.GET.get('start', ''), request.GET.get('stop', '')
    if start and stop:
        start, stop = int(start), int(stop)
        if start and stop:
            qs = qs[start:stop+1]

    if len(qs) == 0:
        return HttpResponse('{}')

    cache_key = 'geojson_%s' %object_id
    # Try and get the most common value from cache
    if not start and not stop:
        gjstr = cache.get(cache_key)
        if gjstr:
            response = HttpResponse(gjstr, mimetype='text/javascript')
            response['Content-Encoding'] = 'gzip'
            response['Content-Length'] = len(gjstr)
            return response


    max_hr = Exercise.objects.get(pk=object_id).user.get_profile().max_hr

    class Feature(object):

        def __init__(self, zone):
            self.linestrings = []
            self.jsonhead = '''
            { "type": "Feature",
              "properties": {
                  "ZONE": %s
                },
                "geometry": {
                    "type": "LineString", "coordinates": [ ''' %zone
            self.jsonfoot = ''']
                }
            }'''

        def addLine(self, a, b, c, d):
            self.linestrings.append('[%s,%s],[%s,%s]' %(a,b,c,d))

        @property
        def json(self):
            if not self.linestrings:
                # Don't return empty feature
                return ''
            return self.jsonhead + ','.join(self.linestrings) + self.jsonfoot

    features = []

    previous_lon, previous_lat, previous_zone = 0, 0, -1
    previous_feature = False
    for d in qs:
        if previous_lon and previous_lat:
            hr_percent = 0
            if d['hr']: # To prevent zerodivision
                hr_percent = float(d['hr'])*100/max_hr
            zone = hr2zone(hr_percent)
            #if zone == 0: # Stylemap does not support zone 0. FIXME
            #    zone = 1

            if previous_zone == zone:
                previous_feature.addLine(previous_lon, previous_lat, d['lon'], d['lat'])
            else:
                if previous_feature:
                    features.append(previous_feature)
                previous_feature = Feature(zone)

            previous_zone = zone
        previous_lon = d['lon']
        previous_lat = d['lat']

    # add last segment
    if previous_zone == zone:
        previous_feature.addLine(previous_lon, previous_lat, d['lon'], d['lat'])
    features.append(previous_feature)


    gjhead = '''{
    "type": "FeatureCollection",
        "features": ['''
    gjstr = '%s%s]}' % (gjhead, ','.join(filter(lambda x: x, [f.json for f in features])))
    gjstr = compress_string(gjstr)

    # save to cache if no start and stop
    if not start and not stop:
        cache.set(cache_key, gjstr, 86400)

    response = HttpResponse(gjstr, mimetype='text/javascript')
    response['Content-Encoding'] = 'gzip'
    response['Content-Length'] = len(gjstr)
    return response

def tripdetail_js(event_type, object_id, val, start=False, stop=False):
    if start:
        start = int(start)
    if stop:
        stop = int(stop)

    qs = ExerciseDetail.objects.filter(exercise=object_id)

    x = 0
    distance = 0
    previous_time = False
    js = []
    for i, d in enumerate(qs.all().values('time', 'speed', val)):
        if start and i < start:
            continue
        if stop and i >= stop:
            break
        if not previous_time:
            previous_time = d['time']
        time = d['time'] - previous_time
        previous_time = d['time']
        distance += ((d['speed']/3.6) * time.seconds)/1000
        # time_xaxis = x += float(time.seconds)/60
        dval = d[val]
        if dval > 0: # skip zero values (makes prettier graph)
            js.append((distance, dval))
    return simplejson.dumps(js)

#@profile("json_trip_series")
def json_trip_series(request, object_id):
    ''' Generate a json file to be retrieved by web browsers and renderend in flot '''
    exercise = get_object_or_404(Exercise, pk=object_id)

    time_xaxis = True
    smooth = 0
    req_t = request.GET.get('xaxis', '')
    if exercise.avg_speed:
        if not (req_t == 'time' or str(exercise.exercise_type) == 'Rollers'): # TODO make exercise_type matrix for xaxis, like for altitude
            time_xaxis = False
    req_s = request.GET.get('smooth', '')
    if req_s:
        try:
            smooth = int(req_s)
        except:
            smooth = 0

    if not exercise.user == request.user:  # Allow self
        is_friend = False
        if request.user.is_authenticated():
            is_friend = Friendship.objects.are_friends(request.user, exercise.user)
        if exercise.exercise_permission == 'N':
            raise Http403()
        elif exercise.exercise_permission == 'F':
            if not is_friend:
                raise Http403()
    power_show = exercise_permission_checks(request, exercise)

    cache_key = 'json_trip_series_%s_%dtime_xaxis_%dpower_%dsmooth' %(object_id, time_xaxis, smooth, power_show)
    js = cache.get(cache_key)
    if not js:
        details = exercise.exercisedetail_set.all()
        if exercise.avg_power:
            generate_30s_power = power_30s_average(details)
        has_distance = filldistance(details)
        if not has_distance:
            time_xaxis = True
        js = compress_string(js_trip_series(request, details, time_xaxis=time_xaxis, smooth=smooth, use_constraints = False))
        cache.set(cache_key, js, 86400)
    response = HttpResponse(js, mimetype='text/javascript')
    response['Content-Encoding'] = 'gzip'
    response['Content-Length'] = len(js)
    return response

def js_trip_series(request, details,  start=False, stop=False, time_xaxis=True, use_constraints=True, smooth=0):
    ''' Generate javascript to be used directly in flot code
    Argument use_constraints can be used to disable flot constraints for HR, used for compare feature
    Argument smooth to reduce number of elements by averaging by the number given in smooth'''

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
            'temp': [],
            'lon': [],
            'lat': [],
        }

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

    # Check if we should export temperature to graph
    has_temperature = False
    if exercise.max_temperature:
        has_temperature = True
    if not has_temperature:
        del js_strings['temp']
    if not exercise.avg_power:
        del js_strings['power']
        del js_strings['poweravg30s']
    if not exercise.avg_hr:
        del js_strings['hr']
    if not exercise.avg_cadence:
        del js_strings['cadence']


    x = 0
    previous_time = False

    for i, d in enumerate(details):
        if start and start < i:
            continue
        if stop and i > stop:
            break
        if not previous_time: # For first value
            previous_time = d.time
        time = d.time - previous_time
        previous_time = d.time
        if time_xaxis:
            x += float(time.seconds)/60
        else:
            if d.distance:
                x = d.distance/1000

        for val in js_strings.keys():
            try:
                dval = getattr(d, val)
                ### Export every single item to graph, this because indexes are used in zooming, etc
                if dval == None:
                    dval = 0
                if val in ('lon', 'lat'): # No distance needed for these, uses indexes
                    js_strings[val].append(dval)
                else:
                    js_strings[val].append((x, dval))
            except AttributeError: # not all formats support all values
                pass

    # Convert lists into strings
    for val in js_strings.keys():
        thevals = js_strings[val]
        if smooth:
            if val in ('lon', 'lat'): # No Distance needed for these
                thevals = [sum(thevals[i*smooth:(i+1)*smooth])/smooth for i in xrange(len(thevals)/smooth)]
            else:
                #if not dists: # Only do this once
                dists = islice([d[0] for d in thevals], None,None, smooth)
                vals = [v[1] for v in thevals]
                thevals = [sum(vals[i*smooth:(i+1)*smooth])/smooth for i in xrange(len(vals)/smooth)]
                thevals = zip(dists, thevals)
        if len(thevals):
            js_strings[val] =  simplejson.dumps(thevals, separators=(',',':'))

    js_strings['use_constraints'] = use_constraints

    t = loader.get_template('turan/js_datasets.js')
    c = Context(js_strings)
    js = t.render(c)
    # Remove last comma for nazi json parsing
    js = js.rstrip(', \n') + '}'
    return js

def getzones_with_legend(exercise):

    zones = exercise.hrzonesummary_set.all()
    zones_with_legend = SortedDict()

    for zone in zones:
        if zone.zone == 0:
            zones_with_legend['0 (0% - 60%)'] = zone.duration
        elif zone.zone == 1:
            zones_with_legend['1 (60% - 72%)'] = zone.duration
        elif zone.zone == 2:
            zones_with_legend['2 (72% - 82%)'] = zone.duration
        elif zone.zone == 3:
            zones_with_legend['3 (82% - 87%)'] = zone.duration
        elif zone.zone == 4:
            zones_with_legend['4 (87% - 92%)'] = zone.duration
        elif zone.zone == 5:
            zones_with_legend['5 (92% - 97%)'] = zone.duration
        elif zone.zone == 6:
            zones_with_legend['6 (97% - 100%'] = zone.duration
    return zones_with_legend

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

def getwzones_with_legend(exercise):
    ''' Calculate time in different coggans ftp watt zones given trip details '''


    zones = exercise.wzonesummary_set.all()
    zones_with_legend = SortedDict()

    for zone in zones:
        if zone.zone == 1:
            zones_with_legend['1 (0% - 55%)'] = zone.duration
        elif zone.zone == 2:
            zones_with_legend['2 (55% - 75%)'] = zone.duration
        elif zone.zone == 3:
            zones_with_legend['3 (75% - 90%)'] = zone.duration
        elif zone.zone == 4:
            zones_with_legend['4 (90% - 105%)'] = zone.duration
        elif zone.zone == 5:
            zones_with_legend['5 (105% - 121%)'] = zone.duration
        elif zone.zone == 6:
            zones_with_legend['6 (121% - 150%)'] = zone.duration
        elif zone.zone == 7:
            zones_with_legend['7 (150% - '] = zone.duration

    return zones_with_legend


def gethrhzones(exercise, values, max_hr):
    ''' Calculate time in different sport zones given trip details '''

    #max_hr = values[0].exercise.user.get_profile().max_hr
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

    if exercise.duration:
        total_seconds = exercise.duration.seconds
        for hr in sorted(zones):
            #if 100*float(zones[hr])/total_seconds > 0:
            if hr > 40 and hr < 101:
                percentage = float(zones[hr])*100/total_seconds
                if percentage > 0.5:

                    zone = hr2zone(hr)
                    filtered_zones[zone][hr] = percentage

    return filtered_zones

def getfreqs(values, val_type, min=0, max=0, val_cutoff=0):
    ''' given values, create freqency structure for display in flot '''

    freqs = SortedDict()
    previous_time = False
    for d in values:
        if not previous_time:
            previous_time = d.time
            continue
        time = d.time - previous_time
        previous_time = d.time
        if time.seconds > 60: # Skip samples with pause ?
            continue
        val = getattr(d, val_type)
        if val == None: # Drop nonesamples
            continue
        val = int(round(val))
        if not val in freqs:
            freqs[val] = 0
        freqs[val] += time.seconds

    for freq, val in freqs.iteritems():
        if min and freq < min:
            del freqs[freq]
        elif max and freq > max:
            del freqs[freq]
        elif val_cutoff and val < val_cutoff:
            del freqs[freq]

    return freqs

def getgradients(values, d_offset=0):
    ''' Iterate over details, return list with tuples with distances and gradients '''

    altitudes = []
    distances = []
    inclinesums = {}

    for d in values:
        altitudes.append(d.altitude)
        # Distances is used in the graph, so divide by 1000 to get graph xasis in km
        if d.distance:
            distances.append((d.distance-d_offset)/1000)
        else:
            distances.append(0)

    # Smooth 3 Wide!
    altitudes = smoothListGaussian(altitudes, 3)

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
    cutoff = 0.1 # km
    inclinesums = dict((k, round(v, 1)) for k, v in inclinesums.items() if v >= cutoff)
    # sort the dictionary on gradient
    inclinesums = [ (k,inclinesums[k]) for k in sorted(inclinesums.keys())]

    return zip(distances, gradients), inclinesums


#def getdistance(values, start, end):
#    d = 0
#    for i in xrange(start+1, end+1):
#        delta_t = (values[i].time - values[i-1].time).seconds
#        d += values[i].speed/3.6 * delta_t
#    return d

def filldistance(values):
    d = 0
    if values.exists():
        d_check = values[len(values)-1].distance
        if d_check > 0:
            return d_check
        values[0].distance = 0
        for i in xrange(1,len(values)):
            delta_t = (values[i].time - values[i-1].time).seconds
            if values[i].speed:
                d += values[i].speed/3.6 * delta_t
            values[i].distance = d
    return d


def exercise_permission_checks(request, exercise):
    '''Given a request object and a exercise object, return a tuple with
    boolean for permissions or not '''
    # Permission checks
    power_show = True
    poweravg30_show = True

    is_friend = False
    if request.user.is_authenticated():
        is_friend = Friendship.objects.are_friends(request.user, exercise.user)

    # Check for permission to display attributes
    try:
        # Try to find permission object for this exercise
        permission = exercise.exercisepermission

        if hasattr(permission, "power"):
            permission_val = getattr(permission, "power")
            if permission_val == 'A':
                power_show = True
            elif permission_val == 'F' and is_friend:
                power_show = True
            else: #'N' or not friends
                power_show = False
        if hasattr(permission, "poweravg30s"): # FIXME by tor: why was this created, doesn't seem to be used??
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
    return power_show


#@profile("exercise_detail")
def exercise(request, object_id):
    ''' View for exercise detail '''

    # Can't be used with select_related so do this manually object = get_object_or_404(Exercise, pk=object_id)
    try:
        object = Exercise.objects.select_related('route', 'user', \
                'exercisepermission', 'hrzonesummary', 'wzonesummary'\
                'exercise_type', 'slope', 'segmentdetail'
                )\
                .get(pk=object_id)
    except Exercise.DoesNotExist:
        raise Http404

    if not object.user == request.user:  # Allow self
        is_friend = False
        if request.user.is_authenticated():
            is_friend = Friendship.objects.are_friends(request.user, object.user)
        if object.exercise_permission == 'N':
            raise Http403()
            return redirect_to_login(request.path)
        elif object.exercise_permission == 'F':
            if not is_friend:
                raise Http403()
                return redirect_to_login(request.path)
    power_show = exercise_permission_checks(request, object)

    # Provide template string for maximum yaxis value for HR, for easier comparison
    maxhr_js = ''
    profile = object.user.get_profile()
    if profile.max_hr:
        max_hr = int(profile.max_hr)
        maxhr_js = ', max: %s' %max_hr
    else:
        max_hr = 200 # FIXME, maybe demand from user ?

    details = object.exercisedetail_set.all()
    # Default is false, many exercises don't have distance, we try to detect later
    time_xaxis = True
    smooth = 0
    if details.exists():
        if filldistance(details): # Only do this if we actually have distance
            # xaxis by distance if we have distance in details unless user requested time !
            req_t = request.GET.get('xaxis', '')
            if not (req_t == 'time' or str(object.exercise_type) == 'Rollers'): # TODO make exercise_type matrix for xaxis, like for altitude
                time_xaxis = False
            req_s = request.GET.get('smooth', '')
            if req_s:
                try:
                    smooth = int(req_s)
                except:
                    smooth = 0
            userweight = profile.get_weight(object.date)
            userftp = profile.get_ftp(object.date)
            slopes = []
            # add both segment details and slopes
            slopes += object.slope_set.all().order_by('start')
            slopes += object.segmentdetail_set.all()
            slopes = sorted(slopes, key=lambda x: x.start)

            # TODO: maybe put this in json details for cache etc
            #lonlats = []
            #for d in details:
            #    if d.lon == None:
            #        d.lon = 0.0
            #    if d.lat == None:
            #        d.lat = 0.0
            #    lonlats.append((d.lon, d.lat))
            #    [(d.lon, d.lat) for d in details if d.lon and d.lat])
            # Todo, maybe calculate and save in db or cache ?
            gradients, inclinesums = getgradients(details)
        intervals = object.interval_set.select_related().all()
        zones = getzones_with_legend(object)
        wzones = getwzones_with_legend(object)
        hrhzones = gethrhzones(object, details, max_hr)
        cadfreqs = []
        bestpowerefforts = object.bestpowereffort_set.all()
        # fetch the all time best for comparison
        #bestbestpowerefforts = []
        #for bpe in bestpowerefforts:
        #    bbpes = BestPowerEffort.objects.filter(exercise__user=object.user,duration=bpe.duration).order_by('-power')[0]
        #    bestbestpowerefforts.append(bbpes)
        bestbestpowerefforts = BestPowerEffort.objects.filter(exercise__user__username='tor').values('duration').annotate(power=Max('power'))
        speedfreqs = []
        if object.avg_cadence:
            cadfreqs = getfreqs(details, 'cadence', min=1)
        if object.avg_speed:
            speedfreqs = getfreqs(details, 'speed', min=1, max=150)
        #inclinesummary = getinclinesummary(details)

        if object.avg_power and power_show:
            #object.normalized = power_30s_average(details)
            powerfreqs = getfreqs(details, 'power', min=1, val_cutoff=5)
            #for i in range(0, len(poweravg30s)):
            #    details[i].poweravg30s = poweravg30s[i]

    #datasets = js_trip_series(request, details, time_xaxis=time_xaxis, smooth=smooth)

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



            if model == Exercise:
                # notify friends of new object
                if notification and user_required: # only notify for user owned objects
                    notification.send(friend_set_for(request.user.id), 'exercise_create', {'sender': request.user, 'exercise': new_object}, [request.user])

                task = new_object.parse()
                if task:
                    if request.user.is_authenticated():
                        request.user.message_set.create(message=ugettext("The %(verbose_name)s was created successfully.") % {"verbose_name": model._meta.verbose_name})
                    return HttpResponseRedirect(\
                            reverse('exercise_parse_progress', kwargs = {
                                'object_id': new_object.id,
                                'task_id': task.task_id}))


            return redirect(post_save_redirect, new_object)
    else:
        if model == SegmentDetail: # prefill variables
            exercise = request.GET.get('exercise', '')
            start = request.GET.get('start', '')
            stop = request.GET.get('stop', '')
            segment = request.GET.get('segment', '')
            try:
                exercise = int(exercise)
                start = int(start)
                stop = int(stop)
                if segment:
                    segment = int(segment)
            except ValueError:
                return HttpResponseForbidden('Invalid request')
            exercise = Exercise.objects.get(pk=exercise)
            details = exercise.get_details().all()
            # Run filldistance on all dtails because filldistance doesn't support detail slices yet
            # this is a TODO
            details = details[0:stop+1]
            d = filldistance(details)
            ret = detailslice_info(details[start:stop])
            data = {}
            data['exercise'] = exercise
            data['start'] = ret['start']
            data['length'] = ret['distance']
            data['ascent'] = int(ret['ascent'])
            data['grade'] = ret['gradient']
            data['duration'] = ret['duration']
            data['speed'] = ret['speed__avg']
            data['est_power'] = ret['power__avg_est']
            data['act_power'] = ret['power__avg']
            data['vam'] = ret['vam']
            data['avg_hr'] = ret['hr__avg']
            data['start_lon'] = ret['start_lon']
            data['start_lat'] = ret['start_lat']
            data['end_lon'] = ret['end_lon']
            data['end_lat'] = ret['end_lat']
            data['power_per_kg'] = ret['power_per_kg']
            if segment:
                data['segment'] = Segment.objects.get(pk=segment)
                new_object = SegmentDetail(**data)
                new_object.save()
                return HttpResponseRedirect(new_object.get_absolute_url())
            form = form_class(initial=data)
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
    if model == SegmentDetail:
        if not obj.exercise.user == request.user:
            return HttpResponseForbidden('Wat?')
    else:
        if not obj.user == request.user:
            return HttpResponseForbidden('Wat?')

    # Check if exercise has singelserving route, if so, delete it
    #if model == Exercise:
    #    if obj.route:
    #        if obj.route.single_serving == True:
    #            obj.route.delete()


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
                    content = ContentFile(urllib2.urlopen(url).read())

                    route.gpx_file.save("gpx/sporty_" + id + ".gpx", content)
                    form.save()

                    return HttpResponseRedirect(route.get_absolute_url())
                else:
                    raise Http404

            # Supports both route and exercise import
            elif url.find("http://connect.garmin.com/activity/") == 0:
                cj = cookielib.LWPCookieJar()
                opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
                urllib2.install_opener(opener)

                headers = {
                        'User-agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'
                }
                post = {
                    'login': 'login',
                    'login:loginUsernameField': 'turan.no',
                    'login:password': 'turan.no',
                    'login:signInButton': 'a',
                    'javax.faces.ViewState': 'j_id1'
                }

                # Login needs to get some cookies or something so we try twice
                u1 = "https://connect.garmin.com/signin"
                req = urllib2.Request(u1, urllib.urlencode(post), headers)
                f = urllib2.urlopen(req)
                req = urllib2.Request(u1, urllib.urlencode(post), headers)
                f = urllib2.urlopen(req)

                base_url = "http://connect.garmin.com"
                id = url.split("/")[-1].rstrip("/")

                tripdata = urllib2.urlopen(url).read()
                tripsoup = BeautifulSoup(tripdata, convertEntities=BeautifulSoup.HTML_ENTITIES)
                # Lets hope these ones work for a while
                gpx_url = base_url + "/proxy/activity-service-1.1/gpx/activity/%s?full=true" % ( id )
                # Website used 1.0 for tcx and 1.1 for gpx when this was written
                # although 1.1 also seems to work for tcx
                tcx_url = base_url + "/proxy/activity-service-1.0/tcx/activity/%s?full=true" % ( id )

                route_name = tripsoup.find(id="activityName")
                if route_name and route_name.string:
                    route_name = route_name.string.strip()
                else:
                    route_name = "Unnamed"

                exercise_description = tripsoup.find(id="discriptionValue")
                if exercise_description and exercise_description.string:
                    exercise_description = exercise_description.string.strip()
                else:
                    exercise_description = None

                route = None

                if gpx_url:
                    route = Route()
                    req = urllib2.Request(gpx_url, None, headers)
                    content = ContentFile(urllib2.urlopen(req).read())
                    route.gpx_file.save("gpx/garmin_connect_" + id + ".gpx", content)
                    route.name = route_name
                    route.save()

                if tcx_url:
                    req = urllib2.Request(gpx_url, None, headers)
                    content = ContentFile(urllib2.urlopen(req).read())
                    exercise_filename = 'sensor/garmin_connect_' + id + '.tcx'

                    exercise = Exercise()
                    exercise.user = request.user
                    exercise.sensor_file.save(exercise_filename, content)
                    if exercise_description:
                        exercise.comment = exercise_description
                    if route:
                        exercise.route = route
                    exercise.save()
                    exercise.parse()

                return render_to_response("turan/import_stage2.html", {'route': route, 'exercise': exercise}, context_instance=RequestContext(request))
    else:
        form = ImportForm()

    return render_to_response("turan/import.html", {'form': form}, context_instance=RequestContext(request))


def slopes(request, queryset):
    ''' Slope list view, based on turan_object_list. Changed a bit for search
    and filter purposes '''

    search_query = request.GET.get('q', '')
    if search_query:
        qset = (
            Q(exercise__route__name__icontains=search_query) |
            Q(exercise__route__description__icontains=search_query) |
            Q(exercise__tags__icontains=search_query)
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

    queryset = queryset.filter(vam__lt=1800) # humans.

    username = request.GET.get('username', '')
    if username:
        user = get_object_or_404(User, username=username)
        queryset = queryset.filter(exercise__user=user)

    return object_list(request, queryset=queryset, extra_context=locals())

def segments(request, queryset):
    ''' Segment list view, based on turan_object_list. Changed a bit for search
    and filter purposes '''

    search_query = request.GET.get('q', '')
    if search_query:
        qset = (
            Q(exercise__route__name__icontains=search_query) |
            Q(exercise__route__description__icontains=search_query) |
            Q(exercise__tags__icontains=search_query)
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
        queryset = queryset.filter(exercise__user=user)

    return object_list(request, queryset=queryset, extra_context=locals())

def internal_server_error(request, template_name='500.html'):
    ''' Custom http code 500 view, to include Context for MEDIA_URL and such '''

    t = loader.get_template(template_name)
    return HttpResponseServerError(t.render(RequestContext(request, {})))

@login_required
def exercise_parse(request, object_id):
    ''' View to trigger reparse of a single exercise given exercise id '''

    exercise = get_object_or_404(Exercise, id=object_id)
    task = exercise.parse()
    if task:
        return HttpResponseRedirect(\
                reverse('exercise_parse_progress', kwargs = {
                    'object_id': object_id,
                    'task_id': task.task_id}))

@login_required
def exercise_segment_search(request, object_id):
    ''' View to display segments found in an exercise and make user able to
    add to shared segments '''

    exercise = get_object_or_404(Exercise, id=object_id)
    segments = search_trip_for_possible_segments_matches(exercise)

    return render_to_response('turan/exercise_segments.html', locals(), context_instance=RequestContext(request))

@login_required
def exercise_parse_progress(request, object_id, task_id):
    ''' View to display progress on parsing and redirect user
    to fully parsed exercised when done '''

    exercise = get_object_or_404(Exercise, id=object_id)
    result = AsyncResult(task_id).status

    return render_to_response('turan/exercise_parse.html', locals(), context_instance=RequestContext(request))
