from models import *
from geojson import GeoJSONFeature, GeoJSONFeatureCollection
from tasks import smoothListGaussian, power_30s_average \
        , hr2zone, detailslice_info, search_trip_for_possible_segments_matches, filldistance, \
        create_gpx_from_details, smoothList
from itertools import groupby, islice
from forms import ExerciseForm, ImportForm, BulkImportForm
from profiles.models import Profile, UserProfileDetail
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, HttpResponsePermanentRedirect, HttpResponseForbidden, Http404, HttpResponseServerError
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.template import RequestContext, Context, loader
from django.template.response import TemplateResponse
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
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.base import ContentFile
from django.utils.safestring import mark_safe
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.views import redirect_to_login
from django.views.generic.create_update import get_model_and_form_class, apply_extra_context, redirect, update_object, lookup_object, delete_object
from django.db.models import get_model
from django.views.generic.list_detail import object_list
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.core.cache import cache
from django.utils.decorators import decorator_from_middleware
from django.views.decorators.gzip import gzip_page
from django.utils.datastructures import SortedDict
from django.middleware.gzip import GZipMiddleware

from turan.middleware import Http403
from tempfile import NamedTemporaryFile
import urllib2
import cookielib
import urllib
import os
import zipfile
import re
import locale
import simplejson

from BeautifulSoup import BeautifulSoup

from tagging.models import Tag
from tribes.models import Tribe
from friends.models import Friendship
from wakawaka.models import WikiPage, Revision
from photos.models import Pool, Image
from photos.forms import PhotoUploadForm
from avatar.models import Avatar
from endless_pagination.decorators import page_template

from datetime import timedelta, datetime
from datetime import date as datetimedate
from datetime import time as datetimetime
from time import mktime, strptime

from turancalendar import WorkoutCalendar
from templatetags.turan_extras import durationformatshort
from feeds import ExerciseCalendar

#from simplejson import encoder
#encoder.c_make_encoder = None
#encoder.FLOAT_REPR = lambda o: format(o, '.4f')

from profiler import profile

from groupcache.decorators import cache_page_against_model, cache_page_against_models

from celery.result import AsyncResult

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

from friends.models import friend_set_for
from djpjax import pjax



def datetime2jstimestamp(obj):
    ''' Helper to generate js timestamp for usage in flot '''
    return mktime(obj.timetuple())*1000

@cache_page_against_models(Tribe, Friendship, Avatar, Exercise, Route,
                           Segment, SegmentDetail, ThreadedComment,
                           Profile, User, notification.Notice)
@vary_on_cookie
def index(request):
    ''' Index view for Turan '''


    e_lookup_kwargs =  {}
    u_lookup_kwargs = {}
    c_lookup_kwargs = {}
    if 'friends' in request.GET:
        if request.user.is_authenticated():
            friend_set = friend_set_for(request.user.id)
            friend_set = list(friend_set)
            friend_set.append(request.user)
            e_lookup_kwargs['user__in'] = friend_set
            usernames = [u.username for u in friend_set]
            u_lookup_kwargs['username__in'] = usernames
            c_lookup_kwargs = e_lookup_kwargs

    team =  request.GET.get('team', '')
    if team:
        friend_set =  get_object_or_404(Tribe, slug=team)
        friend_set = friend_set.members.all()
        e_lookup_kwargs['user__in'] = friend_set
        usernames = [u.username for u in friend_set]
        u_lookup_kwargs['username__in'] = usernames
        c_lookup_kwargs = e_lookup_kwargs

    exercise_list = Exercise.objects.exclude(exercise_permission='N').filter(**e_lookup_kwargs).select_related('route', 'tagging_tag', 'tagging_taggeditem', 'exercise_type', 'user__profile', 'user', 'user__avatar', 'avatar')[:10]
    comment_list = ThreadedComment.objects.filter(**c_lookup_kwargs).filter(is_public=True).order_by('-date_submitted')[:5]

    route_list = Route.objects.annotate( tcount=Count('exercise') ).order_by('-tcount')[:12]
    #route_list = sorted(route_list, key=lambda x: -x.exercise_set.count())[:15]

    segment_list = Segment.objects.annotate(tcount=Count('segmentdetail'),last_date=Max('segmentdetail__exercise__date'),last_time=Max('segmentdetail__exercise__time')).order_by('-last_date','-last_time')

    tag_list = Tag.objects.cloud_for_model(Exercise)

    # Top exercisers last 14 days
    today = datetimedate.today()
    days = timedelta(days=14)
    begin = today - days
    user_list = User.objects.filter(**u_lookup_kwargs).filter(exercise__date__range=(begin, today)).annotate(Sum('exercise__duration')).exclude(exercise__duration__isnull=True).order_by('-exercise__duration__sum')[:15]
    team_list = Tribe.objects.all()

    return render_to_response('turan/index.html', locals(), context_instance=RequestContext(request))

def exercise_compare(request, exercise1, exercise2):

    trip1 = get_object_or_404(Exercise, pk=exercise1)
    trip2 = get_object_or_404(Exercise, pk=exercise2)
    if trip1.exercise_permission == 'N' or trip2.exercise_permission == 'N':
        return redirect_to_login(request.path)
        # TODO Friend check

    alt = tripdetail_js(trip1.id, 'altitude')
    #alt_max = trip1.get_details().aggregate(Max('altitude'))['altitude__max']*2

    datasets1 = js_trip_series(request, trip1, trip1.get_details().all().values(), time_xaxis=False, use_constraints=False)
    datasets2 = js_trip_series(request, trip2, trip2.get_details().all().values(), time_xaxis=False, use_constraints=False)
    if not datasets1 or not datasets2:
        return HttpResponse(_('Missing exercise details.'))
    datasets1, datasets2 = mark_safe(datasets1), mark_safe(datasets2)
    #datasets = mark_safe(datasets1 + ',' +datasets2)

    return render_to_response('turan/exercise_compare.html', locals(), context_instance=RequestContext(request))

class TripsFeed(Feed):
    title = "Turan.no exercises"
    link = "http://turan.no/"
    description = "Exercises from http://turan.no"

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

@cache_page_against_models(Exercise)
@vary_on_cookie
@pjax('turan/event_list-pjax.html')
@page_template('turan/event_list_page.html')
def events(request, template='turan/event_list.html', group_slug=None, bridge=None, username=None, latitude=None, longitude=None, extra_context=None):
    if bridge is not None:
        try:
            group = bridge.get_group(group_slug)
        except ObjectDoesNotExist:
            raise Http404
    else:
        group = None

    if group:
        object_list = group.content_objects(Exercise)
    else:
        object_list = Exercise.objects.select_related().filter(date__isnull=False)
        if username:
            user = get_object_or_404(User, username=username)
            object_list = object_list.filter(user=user)

    if latitude and longitude:
        # A litle aprox box around your area
        object_list = object_list.filter(route__start_lat__gt=float(latitude) - 0.5)
        object_list = object_list.filter(route__start_lat__lt=float(latitude) + 0.5)
        object_list = object_list.filter(route__start_lon__gt=float(longitude) - 1.0)
        object_list = object_list.filter(route__start_lon__lt=float(longitude) + 1.0)

    search_query = request.GET.get('q', '')
    if search_query:
        qset = (
                Q(route__name__icontains=search_query) |
                Q(comment__icontains=search_query) |
                Q(tags__contains=search_query)
                )
        object_list = object_list.filter(qset).distinct()

    context = locals()
    if extra_context:
        context.update(extra_context)

    return TemplateResponse(request, template, context)

@page_template('turan/route_detail_page.html')
def route_detail(request, object_id, template='turan/route_detail.html', extra_context=None):
    object = get_object_or_404(Route, pk=object_id)
    usertimes = {}
    object_list = object.get_trips()
    try:
        done_altitude_profile = False
        for trip in sorted(object_list, key=lambda x:x.date):
            if not trip.user in usertimes:
                usertimes[trip.user] = ''
            try:
                time = trip.duration.total_seconds()/60
                if trip.avg_speed: # Or else graph bugs with None-values
                    usertimes[trip.user] += mark_safe('[%s, %s],' % (datetime2jstimestamp(trip.date), trip.avg_speed))
            except AttributeError:
                pass # stupid decimal value in trip duration!

            if trip.avg_speed and trip.get_details().exists() and not done_altitude_profile: # Find trip with speed or else tripdetail_js bugs out
                                                             # and trip with details
                alt = tripdetail_js(trip.id, 'altitude')
                alt_max, alt_min = trip.get_details().aggregate(max=Max('altitude'),min=Min('altitude')).values()
                done_altitude_profile = True

    except TypeError:
        # bug for trips without date
        pass
    except UnboundLocalError:
        # no trips found
        pass

    context = locals()
    if extra_context:
        context.update(extra_context)
    return render_to_response(template, context, context_instance=RequestContext(request))

@page_template('turan/segment_detail_page.html')
def segment_detail(request, object_id, template='turan/segment_detail.html', extra_context=None):
    ''' View for a single segment '''
    object = get_object_or_404(Segment, pk=object_id)
    # Workaround for http://turan.no/sentry/group/147/messages/3326 and googlebot being persistent.
    if request.GET.get('sort', '') == 'object.exercise.user':
        raise Http404
    usertimes = {}
    slopes = object.get_slopes().select_related('exercise', 'exercise__route', 'exercise__exercise_type', 'exercise__user__profile', 'segment', 'profile', 'exercise__user')
    if request.GET.get('distinct', ''):
        # I do not know how to trick the ORM to return this directly
        # I think I need a DISTINCT ON patch
        sds = SegmentDetail.objects.filter(segment=object_id).values('id','exercise__user','duration').order_by('duration')
        id_list = []
        u_list = []
        for s in sds:
            if not s['exercise__user'] in u_list:
                u_list.append(s['exercise__user'])
                id_list.append(s['id'])
        slopes = SegmentDetail.objects.filter(id__in=id_list)
    username = request.GET.get('username', '')
    if username:
        other_user = get_object_or_404(User, username=username)
        slopes = slopes.filter(exercise__user=other_user)

    if not request.is_ajax(): #code not needed for page_template

        series = {}
        t_offset = 0
        for i, slope in enumerate(sorted(slopes, key=lambda x:x.duration)[0:20]):
            other_user = slope.exercise.user
            if not other_user in series:
                series[other_user] = []
            time = slope.duration
            if not t_offset: # initialize time offsett
                t_offset = time
            series[other_user].append((i, time))
        for key, val in series.items():
            series[key]= simplejson.dumps(val)
        if slopes:
            exercise_type = slope.exercise.exercise_type

        gradients = simplejson.dumps(list(object.segmentaltitudegradient_set.values_list('xaxis', 'gradient')))
        alt = simplejson.dumps(list(object.segmentaltitudegradient_set.values_list('xaxis', 'altitude')))
        lonlats = simplejson.dumps(list(object.segmentaltitudegradient_set.values_list('lon', 'lat')))
        alt_max, alt_min = object.segmentaltitudegradient_set.aggregate(max=Max('altitude'),min=Min('altitude')).values()

    context = locals()
    if extra_context:
        context.update(extra_context)
    #if request.is_ajax():
    #    return HttpResponse(str(slopes))
    return render_to_response(template, context, context_instance=RequestContext(request))

def week(request, week, user_id='all'):

    object_list = []
    cycleqs = CycleTrip.objects.filter(date__month=week)
    hikeqs = Hike.objects.filter(date__month=week)

    for e in cycleqs:
        object_list.append(e)
    for e in hikeqs:
        object_list.append(e)

    return render_to_response('turan/event_list.html', locals(), context_instance=RequestContext(request))

@cache_page_against_models(Exercise, Profile, User, UserProfileDetail)
@vary_on_cookie
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

    exercisetypes = ExerciseType.objects.all()

    tfilter = {}
    if exercisename:
        exercise = get_object_or_404(ExerciseType, name=exercisename)
        exercisefilter = { "user__exercise__exercise_type": exercise }
        datefilter["user__exercise__exercise_type"] = exercise
        tfilter.update(exercisefilter)
    tfilter.update(datefilter)
    #else:
    #    exercise = get_object_or_404(ExerciseType, name='Cycling')

    stats_dict = Exercise.objects.filter(**tfilter).aggregate(
            Max('avg_speed'),
            Avg('avg_speed'),
            Avg('route__distance'),
            Max('route__distance'),
            Sum('route__distance'),
            Avg('duration'),
            Max('duration'),
            Sum('duration'))
    total_duration = stats_dict['duration__sum']
    total_distance = stats_dict['route__distance__sum']
    total_avg_speed = stats_dict['avg_speed__avg']
    longest_trip = stats_dict['route__distance__max']
    if not total_duration:
        raise Http404('No trips found')

    userstats = statsprofiles.filter(**tfilter).annotate(
            avg_avg_speed = Avg('user__exercise__avg_speed'),
            max_avg_speed = Max('user__exercise__avg_speed'),
            max_speed = Max('user__exercise__max_speed'),
            num_trips = Count('user__exercise'),
            sum_distance = Sum('user__exercise__route__distance'),
            sum_duration = Sum('user__exercise__duration'),
            sum_energy = Sum('user__exercise__kcal'),
            avg_normalized_power = Avg('user__exercise__normalized_power'),
            max_normalized_power = Max('user__exercise__normalized_power'),
            avg_avg_pedaling_power = Avg('user__exercise__avg_pedaling_power'),
            max_avg_pedaling_power = Max('user__exercise__avg_pedaling_power'),
            max_max_power = Max('user__exercise__max_power'),
            sum_ascent = Sum('user__exercise__route__ascent'),
            avg_avg_hr = Avg('user__exercise__avg_hr'),
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
    maxnormalizedpower =  userstats.filter(max_normalized_power__gt=0).order_by('-max_normalized_power')
    avgpedalingpower =  userstats.filter(avg_avg_pedaling_power__gt=0).order_by('-avg_avg_pedaling_power')
    maxpedalingpower =  userstats.filter(max_avg_pedaling_power__gt=0).order_by('-max_avg_pedaling_power')
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
    climbstats = statsprofiles.filter(**tfilter).annotate(
            distance = Sum('user__exercise__route__distance'),
            height_sum = Sum('user__exercise__route__ascent'),
            duration = Sum('user__exercise__duration'),
            trips = Count('user__exercise')
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
        .annotate(
            duration = Sum('user__exercise__hrzonesummary__duration')
            )\
        .order_by('-duration'))
    hrzonestats = zip(hrzones, hrzonestats)


    bestest_power = []
    intervals = [5, 10, 30, 60, 240, 300, 600, 1200, 1800, 3600]
    for i in intervals:
        userweight_tmp = []
        best_power_tmp = statsprofiles.filter(**tfilter)\
        .extra(where=['turan_bestpowereffort.duration = %s' %i])\
        .annotate( max_power = Max('user__exercise__bestpowereffort__power'))\
        .order_by('-max_power')
        for a in best_power_tmp:
            if a.get_weight():
                userweight_tmp.append(a.max_power/a.get_weight())
            else:
                userweight_tmp.append(0)
        best_power_tmp = zip(best_power_tmp, userweight_tmp)
        best_power_tmp = sorted(best_power_tmp, key=lambda x: -x[1])
        bestest_power.append(best_power_tmp)
    bestest_power = zip(intervals, bestest_power)

    team_list = Tribe.objects.all()


    # Limit the number of resulsts
    resultsize = 10
    numtrips = numtrips[:resultsize]
    dursums = dursums[:resultsize]
    distsums = distsums[:resultsize]
    lengthstats = lengthstats[:resultsize]
    maxavgspeeds = maxavgspeeds[:resultsize]
    avgspeeds = avgspeeds[:resultsize]
    maxspeeds = maxspeeds[:resultsize]
    energysums = energysums[:resultsize]
    avgavghrs = avgavghrs[:resultsize]
    avgnormalizedpower = avgnormalizedpower[:resultsize]
    maxnormalizedpower = maxnormalizedpower[:resultsize]
    avgpedalingpower = avgpedalingpower[:resultsize]
    maxpedalingpower = maxpedalingpower[:resultsize]
    ascentsums = ascentsums[:resultsize]
    climbstats = climbstats[:resultsize]
    climbstatsbytime = climbstatsbytime[:resultsize]
    maxpowers = maxpowers[:resultsize]


    return render_to_response('turan/statistics.html', locals(), context_instance=RequestContext(request))

def bestest(request):

    bestest_speed = []
    bestest_power = []
    intervals = [5, 30, 60, 240, 300, 600, 1200, 1800, 3600]
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

@cache_page(86400*7)
def colorize_and_scale(request):
    ''' Can scale and colorize any image.
    Used to generate player icons in player and map '''
    import Image
    from cStringIO import StringIO

    if 'i' in request.GET:
        i = settings.MEDIA_ROOT + request.GET['i']
        if not os.path.abspath(i).startswith(settings.MEDIA_ROOT):
            return HttpResponseServerError()
    else:
        return HttpResponseServerError()

    if 'w' in request.GET:
        try:
            w = int(request.GET['w'])
        except ValueError,e:
            w = 24
    else:
        w = 24

    if 'h' in request.GET:
        try:
            h = int(request.GET['h'])
        except ValueError,e:
            h = 24
    else:
        h = 24

    if 'r' in request.GET:
        try:
            r = int(request.GET['r'])
        except ValueError,e:
            r = 255
    else:
        r = 255

    if 'g' in request.GET:
        try:
            g = int(request.GET['g'])
        except ValueError,e:
            g = 255
    else:
        g = 0

    if 'b' in request.GET:
        try:
            b = int(request.GET['b'])
        except ValueError,e:
            b = 255
    else:
        b = 0

    try:
        i = Image.open(i)
    except IOError, e:
        raise Http404()

    sized = i.resize((w, h), Image.ANTIALIAS)

    channels = sized.split()

    if len(channels) == 4:
        channels = (channels[0].point(lambda i: r), channels[1].point(lambda i: g), channels[2].point(lambda i: b), channels[3])
    elif len(channels) == 3:
        channels = (channels[0].point(lambda i: r), channels[1].point(lambda i: g), channels[2].point(lambda i: b))
    else:
        pass

    sized = Image.merge(sized.mode, channels)

    data = StringIO()
    sized.save(data, "png")
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
        other_user = get_object_or_404(User, username=username)
        exercises = exercises.filter(user=other_user)
    else:
        other_user = ''

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

    hz_by_week = {}
    pz_by_week = {}

    if username: # Only give zone week graph for individuals
        for week, es in e_by_week:
            zones =[0,0,0,0,0,0,0]
            dbzones = HRZoneSummary.objects.filter(exercise__in=es).values('zone').annotate(duration=Sum('duration'))
            for dbzone in dbzones:
                zones[dbzone['zone']] += dbzone['duration']
            hz_by_week[week] = zones#[float(zone)/60/60 for zone in zones if zone]
            zones =[0,0,0,0,0,0,0,0]
            dbzones = WZoneSummary.objects.filter(exercise__in=es).values('zone').annotate(duration=Sum('duration'))
            for dbzone in dbzones:
                zones[dbzone['zone']] += dbzone['duration']
            pz_by_week[week] = zones#[float(zone)/60/60 for zone in zones if zone]

    return render_to_response('turan/calendar.html',
            {'calendar': mark_safe(cal),
             'months': months,
             'username': username,
             'previous_month': previous_month,
             'next_month': next_month,
             'e_by_week': e_by_week,
             'pz_by_week': pz_by_week,
             'hz_by_week': hz_by_week,
             'other_user': other_user,
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
        return HttpResponse(simplejson.dumps({}), mimetype='application/json')
    all_details = object.get_details()

    details = all_details.all()[start:stop]
    ret = detailslice_info(details)
    # Post proc for nicer numbers
    if ret['distance'] >= 1000:
        ret['distance'] = '%s %s' %(round(ret['distance']/1000,2), 'km')
    else:
        ret['distance'] = '%s %s' %(round(ret['distance'],2), 'm')
    if ret['duration']:
        ret['duration'] = durationformatshort(ret['duration'])


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

    return HttpResponse(serializers.serialize('json', [rev], indent=4), mimetype='application/json')

#@decorator_from_middleware(GZipMiddleware)
#@cache_page(86400*7)
#@profile("geojson")
def exercise_geojson(request, object_id):
    ''' Return GeoJSON with coords as linestring for use in openlayers stylemap,
    give each line a zone property so it can be styled differently'''

    qs = ExerciseDetail.objects.filter(exercise=object_id).exclude(lon=0).exclude(lat=0).filter(lon__isnull=False,lat__isnull=False,hr__isnull=False).values('hr','lon','lat')

    start, stop = request.GET.get('start', ''), request.GET.get('stop', '')
    if start and stop:
        start, stop = int(start), int(stop)
        if start and stop:
            qs = qs[start:stop+1]

    if not len(qs) > 1:
        return HttpResponse('{}')

    cache_key = 'exercise_geojson_%s' %object_id
    # Try and get the most common value from cache
    if not start and not stop:
        gjstr = cache.get(cache_key)
        if gjstr:
            response = HttpResponse(gjstr, mimetype='application/json')
            response['Content-Encoding'] = 'gzip'
            response['Content-Length'] = len(gjstr)
            return response


    max_hr = Exercise.objects.get(pk=object_id).user.get_profile().max_hr
    if not max_hr: # sigh
        max_hr = 200


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
                previous_feature = GeoJSONFeature(zone)

            previous_zone = zone
        previous_lon = d['lon']
        previous_lat = d['lat']

    # add last segment
    if previous_zone == zone:
        previous_feature.addLine(previous_lon, previous_lat, d['lon'], d['lat'])
    if previous_feature:
        features.append(previous_feature)


    gjstr = compress_string(str(GeoJSONFeatureCollection(features)))

    # save to cache if no start and stop
    if not start and not stop:
        cache.set(cache_key, gjstr, 86400)

    response = HttpResponse(gjstr, mimetype='application/json')
    response['Content-Encoding'] = 'gzip'
    response['Content-Length'] = len(gjstr)
    return response

def segment_geojson(request, object_id):
    ''' Return GeoJSON with coords as linestring for use in openlayers stylemap,
    give each line a zone property so it can be styled differently'''


    object = get_object_or_404(Segment, pk=object_id)

    # Check for cache and return
    cache_key = 'segment_geojson_%s' %object_id
    gjstr = cache.get(cache_key)
    if gjstr:
        response = HttpResponse(gjstr, mimetype='application/json')
        response['Content-Encoding'] = 'gzip'
        response['Content-Length'] = len(gjstr)
        return response

    slopes = object.get_slopes().select_related('exercise', 'exercise__route', 'exercise__user__profile', 'segment', 'profile', 'exercise__user')
    details = []
    for slope in slopes:
        trip = slope.exercise
        if trip.get_details().exclude(lon=0.0).count(): # Find trip with lon, lat
            tripdetails = trip.get_details().all()
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
            d_offset = tripdetails[start].distance
            #alt = simplejson.dumps([((d.distance-d_offset)/1000, d.altitude) for d in tripdetails[start:stop]])
            details = tripdetails[start:stop]
            break
    else:
        return HttpResponse('{}')

    gradients, inclinesums = getgradients(details, d_offset=d_offset)
    gradientslen = len(gradients) # TODO why isn't this same nr as details ?

    features = []
    previous_lon, previous_lat, previous_zone = 0, 0, -1
    previous_feature = False
    for i, d in enumerate(details):
        if previous_lon and previous_lat:
            if i == gradientslen: # we ran out of gradients! Why?
                break

            gradient = gradients[i][1]
            if gradient < 3: # TODO share this constraint list with gradient_tab.html somehow
                zone = 0
            elif gradient < 6:
                zone = 1
            elif gradient < 8:
                zone = 2
            elif gradient < 10:
                zone = 3
            elif gradient < 15:
                zone = 4
            elif gradient < 20:
                zone = 5
            elif gradient < 25:
                zone = 6
            else:
                zone = 7

            if previous_zone == zone:
                if not d.lon:
                    d.lon = previous_lon
                if not d.lat:
                    d.lat = previous_lat
                previous_feature.addLine(previous_lon, previous_lat, d.lon, d.lat)
            else:
                if previous_feature:
                    features.append(previous_feature)
                previous_feature = GeoJSONFeature(zone)

            previous_zone = zone
        previous_lon = d.lon
        previous_lat = d.lat

    # add last segment
    if previous_zone >= 0 and previous_zone == zone:
        previous_feature.addLine(previous_lon, previous_lat, d.lon, d.lat)
    if previous_feature:
        features.append(previous_feature)

    gjstr = compress_string(str(GeoJSONFeatureCollection(features)))

    # save to cache if no start and stop
    if not start and not stop:
        cache.set(cache_key, gjstr, 86400)

    response = HttpResponse(gjstr, mimetype='application/json')
    response['Content-Encoding'] = 'gzip'
    response['Content-Length'] = len(gjstr)
    return response

def json_trip_details(request, object_id, start=False, stop=False):
    pass

def tripdetail_js(object_id, val, start=False, stop=False):
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
        dval = d[val]
        if d['speed'] != None:
            distance += ((d['speed']/3.6) * time.seconds)/1000
            js.append((distance, dval))
        else:
            x += float(time.seconds)/60
            js.append((x, dval))
        #time_xaxis = 
    return simplejson.dumps(js)

#@profile("json_trip_series")
def json_trip_series(request, object_id, start=False):
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
    start =  request.GET.get('start', '')
    if start:
        try:
            start = int(start)
        except:
            start = False

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
    js = None
    if not start and not exercise.live_state == 'L': # Caching not involved in slices or live exercises
        js = cache.get(cache_key)
    if not js:
        details = exercise.exercisedetail_set.all().values('altitude', 'cadence', 'distance', 'hr', 'lat', 'lon', 'power', 'speed', 'temp', 'time')

        if start:
            details = details[start:]
        if exercise.avg_power:
            #generate_30s_power = power_30s_average(details)
            vals = smoothList( [e['power'] for e in details])
            for e, v in zip(details, vals):
                e['poweravg30s'] = v
        has_distance = 0
        if exercise.route and exercise.route.distance > 0:
            has_distance = 1
        if not has_distance:
            time_xaxis = True
        js = js_trip_series(request, exercise, details, start=start, time_xaxis=time_xaxis, smooth=smooth, use_constraints = False)
        if not js: # if start and no elements returner, we get None
            return HttpResponse('{}', mimetype='application/javascript')
        js = js.encode('UTF-8')
        js = compress_string(js)
        if not start and not exercise.live_state == 'L': # Do not cache slices or live exercises
            cache.set(cache_key, js, 86400)
    response = HttpResponse(js, mimetype='application/javascript')
    response['Content-Encoding'] = 'gzip'
    response['Content-Length'] = len(js)
    return response

def js_trip_series(request, exercise, details,  start=False, stop=False, time_xaxis=True, use_constraints=True, smooth=0):
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
    has_altitude = exercise.exercise_type.altitude
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
    if not exercise.avg_speed:
        del js_strings['speed']
    if not exercise.avg_cadence:
        del js_strings['cadence']

    if not 'poweravg30s' in details[0] and 'poweravg30s' in js_strings:
        del js_strings['poweravg30s']


    x = 0
    previous_time = False

    for i, d in enumerate(details):
        if start and start < i:
            continue
        if stop and i > stop:
            break
        if not previous_time: # For first value
            previous_time = d['time']
        time = d['time'] - previous_time
        previous_time = d['time']
        if time_xaxis:
            x += float(time.seconds)/60
        else:
            if d['distance']:
                x = d['distance']/1000

        for val in js_strings.keys():
            try:
                dval = d[val]
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
            js_strings[val] = thevals

    res = {}
    _ = ugettext
    if 'hr' in js_strings:
        res['hr'] =  {
            "data": js_strings['hr'],
            "label": _('HR'),
            "lines": {
                "show": True,
                "fill": 0.0
            },
            "color": 2,
            "yaxis": 2
            }
    if 'speed' in js_strings:
        res['speed'] =  {
                "data": js_strings['speed'],
                "label": _('Speed'),
                "color": 0
            }
    if 'cadence' in js_strings:
        res['cadence'] =  {
            "data": js_strings['cadence'],
            "label": _('Cadence'),
            "color": 1,
            "yaxis": 6
            }
    if 'altitude' in js_strings:
        res['altitude'] =  {
            "data": js_strings['altitude'],
            "label": _('Altitude'),
            "lines": {
                "show": True,
                "fill": 0.3
            },
            "color": 3,
            "yaxis": 4
            }
    if 'power' in js_strings:
        res['power'] =  {
            "data": js_strings['power'],
            "label": _('Power'),
            "color": 5,
            "yaxis": 3
            }
    if 'poweravg30s' in js_strings:
        res['poweravg30s'] =  {
            "data": js_strings['poweravg30s'],
            "label": _('Power Avg30'),
            "color": 4,
            "yaxis": 3
            }
    if 'temp' in js_strings:
        res['temp'] =  {
            "data": js_strings['temp'],
            "label": _('Temperature'),
            "color": 6,
            "yaxis": 5
            }
    if 'lon' in js_strings:
        res['lon'] = js_strings['lon']
        res['lat'] = js_strings['lat']

    res = simplejson.dumps(res, separators=(',',':'))
        #    js_strings[val] =  simplejson.dumps(thevals, separators=(',',':'))
    return res

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

    #if gradients: # Don't try to smooth empty list
    #    gradients = smoothListGaussian(gradients)

    # Clean values to reduce clutter
    # and round distance values
    cutoff = 0.1 # km
    inclinesums = dict((k, round(v, 1)) for k, v in inclinesums.items() if v >= cutoff)
    # sort the dictionary on gradient
    inclinesums = [ (k,inclinesums[k]) for k in sorted(inclinesums.keys())]

    return zip(distances, gradients), inclinesums

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
                'exercisepermission', 'exercise_type').get(pk=object_id)
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
        max_hr = 190 # FIXME, maybe demand from user ?

    # Default is false, many exercises don't have distance, we try to detect later
    time_xaxis = True
    smooth = 0
    if object.sensor_file or object.live_state == 'L': # Instead of running details.exists, 
        #we make the assumption that if exercise has file, it has details
        #if filldistance(details): # Only do this if we actually have distance
            # xaxis by distance if we have distance in details unless user requested time !
        req_t = request.GET.get('xaxis', '')
        # TODO make exercise_type matrix for xaxis, like for altitude
        if not (req_t == 'time' or str(object.exercise_type).lower().endswith(('rollers', 'spinning'))):
            time_xaxis = False
        req_s = request.GET.get('smooth', '')
        if req_s:
            try:
                smooth = int(req_s)
            except:
                smooth = 0
        slopes = []
        # add both segment details and slopes
        slopes += object.slope_set.all().order_by('start')
        slopes += object.segmentdetail_set.all()
        slopes = sorted(slopes, key=lambda x: x.start)


    userweight = profile.get_weight(object.date)
    userftp = profile.get_ftp(object.date)
    intervals = object.interval_set.select_related().all()
    zones = getzones_with_legend(object)
    wzones = getwzones_with_legend(object)
    bestpowerefforts = object.bestpowereffort_set.all()
    userbestbestpowerefforts = []
    # fetch the all time best for comparison
    bestbestpowerefforts = BestPowerEffort.objects.filter(exercise__user=object.user).values('duration').annotate(power=Max('power'))
    if request.user.is_authenticated() and request.user != object.user:
        userbestbestpowerefforts = BestPowerEffort.objects.filter(exercise__user=request.user).values('duration').annotate(power=Max('power'))
    def freqobj_to_json(freq_type):
        f = Freq.objects.get_or_none(exercise=object.id,freq_type=freq_type)
        if f:
            return f.json

    hrhzones = freqobj_to_json('H')
    cadfreqs = freqobj_to_json('C')
    speedfreqs = freqobj_to_json('S')
    powerfreqs = []
    if power_show:
        powerfreqs = freqobj_to_json('P')

    return render_to_response('turan/exercise_detail.html', locals(), context_instance=RequestContext(request))

def json_serializer(request, queryset, root_name = None, relations = (), extras = ()):
    if root_name == None:
        root_name = queryset.model._meta.verbose_name_plural
    #hardcoded relations and extras while testing
    return HttpResponse(serializers.serialize('json', queryset, indent=4, relations=relations, extras=extras), mimetype='application/json')


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
                    #if request.user.is_authenticated():
                    #    request.user.message_set.create(message=ugettext("The %(verbose_name)s was created successfully.") % {"verbose_name": model._meta.verbose_name})
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
            #d = filldistance(details)
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
                request.user.message_set.create(message=ugettext("The %(verbose_name)s was added successfully.") % {"verbose_name": _('Segment')})
                return HttpResponseRedirect(new_object.get_absolute_url())
            form = form_class(initial=data)
        elif model == Exercise:
            data = {}
            #data['equipment']= Equipment.objects.filter(user=request.user)
            form = form_class(initial=data)
            qs = Equipment.objects.filter(user=request.user)
            form.fields['equipment'].queryset = qs
            if qs.count():
                form.fields['equipment'].initial = qs[0].id

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

@cache_page_against_models(ExerciseType, Exercise, Avatar, Route)
@vary_on_cookie
def turan_object_list(request, queryset, extra_context=None, template_name=None):

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
        page_user = get_object_or_404(User, username=username)
        queryset = queryset.filter(user=page_user)

    context = locals()
    if extra_context:
        context.update(extra_context)
        

    return object_list(request, template_name=template_name, queryset=queryset, extra_context=context)


def autocomplete_route(request, app_label, model):
    ''' ajax view to return list of matching routes to given query'''

    #try:
    #    model = ContentType.objects.get(app_label=app_label, model=model)
    #except:
    #    raise Http404

    if not request.GET.has_key('term'):
        raise Http404

    query = request.GET.get('term', '')
    qset = (
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__contains=query)
        )

    #limit = request.GET.get('limit', None)
    limit = 20

    routes = Route.objects.filter(qset).exclude(single_serving=1).annotate( tcount=Count('exercise') ).order_by('-tcount')[:limit]
    route_list = [{'id': f.pk, 'name': f.__unicode__(), 'description': f.description, 'tcount': f.tcount, 'icon': f.get_png_url()} for f in routes]

    return HttpResponse(simplejson.dumps(route_list), mimetype='application/json')

def ical(request, username):

    cal = ExerciseCalendar(username)

    return cal()

def turan_delete_object(request, model=None, post_delete_redirect='/turan/', object_id=None,
        slug=None, slug_field='slug', template_name=None,
        template_loader=loader, extra_context=None, login_required=False,
        context_processors=None, template_object_name='object'):
    """ See django's generic view docs for help. This specific checks that a user is deleting his own objects"""


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

@login_required
def import_bulk(request):
    form = ImportForm()
    if request.method == 'POST':
        bulkform = BulkImportForm(request.POST, request.FILES)
        if bulkform.is_valid():
            exercises = []
            zfile = zipfile.ZipFile( request.FILES['zip_file'])
            for info in zfile.infolist():
                fname = info.filename
                content = zfile.read(fname)
                content = ContentFile(content)
                fname = fname.lower()
                exercise_filename = os.path.join('sensor', fname)

                exercise = Exercise()
                exercise.user = request.user
                exercise.sensor_file.save(exercise_filename, content)
                exercise.save()
                exercises.append(exercise)
            # Done saving, now parse them all
            for e in exercises:
                task = e.parse()
            if task: # Display progress for last task
                return HttpResponseRedirect(\
                reverse('exercise_parse_progress', kwargs = {
                    'object_id': e.id,
                    'task_id': task.task_id}))
    else:
        bulkform = BulkImportForm()

    return render_to_response("turan/import.html", {'form': form, 'bulkform': bulkform}, context_instance=RequestContext(request))


@login_required
def import_data(request):
    bulkform = BulkImportForm()
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

                    return HttpResponseRedirect(route.get_absolute_url())
                else:
                    raise Http404

            elif url.find("http://app.strava.com/rides/") == 0:
                id = url.split("/")[-1].rstrip("/")
                url = "http://app.strava.com/api/v1/streams/" + id + "?streams[]=time,heartrate,speed,latlng,time,distance,altitude,watts,cadence"
                meta_url = "http://app.strava.com/api/v1/rides/" + id
                if id > 0:
                    strava = {}
                    stream_content = ContentFile(urllib2.urlopen(url).read())
                    strava["stream"] = simplejson.load(stream_content)
                    meta_content = ContentFile(urllib2.urlopen(meta_url).read())
                    strava["meta"] = simplejson.load(meta_content)
                    route = Route()
                    route.name = strava["meta"]["ride"]["name"]
                    route.single_serving = True
                    route.save()
                    exercise = Exercise()
                    exercise.route = route
                    exercise.user = request.user
                    comment = strava["meta"]["ride"]["description"]
                    if comment: 
                        exercise.comment = comment
                    exercise_filename = 'sensor/strava_' + id + '.strava_json'
                    exercise.sensor_file.save(exercise_filename, ContentFile(simplejson.dumps(strava)))
                    # exercise.sensor_file = exercise_filename
                    exercise.save()
                    exercise.parse()
                    return render_to_response("turan/import_stage2.html", {'exercise': exercise}, context_instance=RequestContext(request))

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

                try:
                    tripdata = urllib2.urlopen(url).read()
                except urllib2.HTTPError, e:

                    return render_to_response("turan/import.html", {'form': form, 'error': e}, context_instance=RequestContext(request))

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
                    try:
                        content = ContentFile(urllib2.urlopen(req).read())
                    except urllib2.HTTPError, e:

                        return render_to_response("turan/import.html", {'form': form, 'error': e}, context_instance=RequestContext(request))
                    route.gpx_file.save("gpx/garmin_connect_" + id + ".gpx", content)
                    route.name = route_name
                    # Until we have option to match existing route set it to single serving
                    route.single_serving = True
                    route.save()

                if tcx_url:
                    req = urllib2.Request(tcx_url, None, headers)
                    try:
                        content = ContentFile(urllib2.urlopen(req).read())
                    except urllib2.HTTPError, e:

                        return render_to_response("turan/import.html", {'form': form, 'error': e}, context_instance=RequestContext(request))
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

    return render_to_response("turan/import.html", {'form': form, 'bulkform': bulkform}, context_instance=RequestContext(request))


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

@vary_on_cookie
@cache_page_against_models(Route)
@page_template('turan/route_list_page.html')
def routes(request, queryset, template=None, extra_context=None):
    context = locals()
    if extra_context:
        context.update(extra_context)
    if request.is_ajax(): #override template
        return turan_object_list(request, template_name=template, queryset=queryset, extra_context=context)
    return turan_object_list(request, queryset=queryset, extra_context=context)

@vary_on_cookie
@cache_page_against_models(Exercise)
@page_template('turan/exercise_list_page.html')
def exercises(request, queryset, template=None, extra_context=None):
    context = locals()
    if extra_context:
        context.update(extra_context)
    exercise_type = request.GET.getlist('exercise_type')
    if exercise_type:
        queryset = queryset.filter(exercise_type__name__in=exercise_type)
    if request.is_ajax(): #override template
        return turan_object_list(request, template_name=template, queryset=queryset, extra_context=context)
    return turan_object_list(request, queryset=queryset, extra_context=context)

@cache_page_against_models(Segment, SegmentDetail, Avatar)
@vary_on_cookie
def segmentdetails(request, queryset):
    ''' Segment detail list view, based on turan_object_list. Changed a bit for search
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

@cache_page_against_models(Segment, SegmentDetail)
@vary_on_cookie
@page_template('turan/segment/segment_page.html')
def segments(request, queryset, template=None, extra_context=None):
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

    # Order by last ridden
    queryset = queryset.annotate(last_ride=Max('segmentdetail__exercise__date')).order_by('-last_ride')

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
        other_user = get_object_or_404(User, username=username)
        #queryset = queryset.filter(exercise__user=user)
        # Two step attack on this, do not know how to do it it one fell swoop
        s_list_ids = set(SegmentDetail.objects.filter(exercise__user=other_user).values_list('segment__id',flat=1))
        queryset = queryset.filter(id__in=s_list_ids)

    context = locals()
    if extra_context:
        context.update(extra_context)
    if request.is_ajax(): #override template
        return object_list(request, template_name=template, queryset=queryset, extra_context=context)
    return object_list(request, queryset=queryset, extra_context=context)

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
def segment_exercise_search(request, object_id):
    ''' View to display exercises found for a segment and make user able to
    add '''

    if request.user.is_superuser:

        segment = get_object_or_404(Segment, id=object_id)
        segments = {}
        for e in Exercise.objects.all():
            if len(segments) > 19:
                break
            if e.route and e.route.gpx_file:
                found_segments = search_trip_for_possible_segments_matches(e, search_in_segments=[segment])
                if found_segments:
                    segments[e] = found_segments

        return render_to_response('turan/segment_exercise_finder.html', locals(), context_instance=RequestContext(request))
    return HttpResponseForbidden()

@login_required
def exercise_parse_progress(request, object_id, task_id):
    ''' View to display progress on parsing and redirect user
    to fully parsed exercised when done '''

    exercise = get_object_or_404(Exercise, id=object_id)
    result = AsyncResult(task_id).status

    return render_to_response('turan/exercise_parse.html', locals(), context_instance=RequestContext(request))

@login_required
def exercise_create_live(request):
    ''' View to handle creation of new live exercise '''
    if not request.user.is_authenticated():
        return redirect_to_login(request.path)
    ExerciseFormSet = inlineformset_factory(Exercise, ExercisePermission, form=ExerciseForm)

    if request.method == 'POST':
        form = ExerciseFormSet(request.POST, request.FILES)
        if form.is_valid():
            new_object = form.save(commit=False)
            new_object.user = request.user
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

#@login_required TODO enable auth
def exercise_update_live(request, object_id):
    ''' View to handle submitted values from client, make them into exercise details

    They should arrive posted as a json object that looks like this

     should arrive posted as a json object that looks like this
     [
        {"power": 400, "hr": 62, "lon": 5.3, "time": 12312323, "lat": 60, "speed": 34.3},
        {"power": 410, "hr": 64, "lon": 5.4, "time": 12312324, "lat": 61, "speed": 35.3}
     ]

     Fields can vary from entry to entry.
     Supported fieldlist:
        time
        distance
        speed
        hr
        altitude
        lat
        lon
        cadence
        power
        temp

    '''

    exercise = get_object_or_404(Exercise, id=object_id)
    if not exercise.route.gpx_file:
        create_gpx_from_details(exercise)
    route = exercise.route

    if request.method == 'POST' or request.method == 'GET':
        data = request.raw_post_data
        data = simplejson.loads(data)
        #print 'JSON: %s' %data
        try:
            for item in data:
                new_object = ExerciseDetail(**item)
                new_object.time = datetime.fromtimestamp(float(new_object.time))
                new_object.exercise = exercise
                new_object.save()
                new_time = datetimetime(new_object.time.hour, \
                        new_object.time.minute, new_object.time.second)
                if not exercise.time:
                    exercise.time = new_time
                if not exercise.date:
                    exercise.date = datetimedate(new_object.time.year, \
                            new_object.time.month, new_object.time.day)
                if new_object.lon and not exercise.start_lon:
                    route.start_lon = float(new_object.lon)
                if new_object.lat and not exercise.start_lat:
                    route.start_lat = float(new_object.lat)
                if new_object.lon:
                    route.end_lon = float(new_object.lon)
                if new_object.lat:
                    route.end_lat = float(new_object.lat)

                old_duration = 0
                try:
                    old_duration = exercise.duration.total_seconds()
                except:
                    pass # Object is Decimal first time around, stupid durationfield

                # Use exercise start time as previous if no previous samples found (e.g. first sample)
                previous_time = exercise.time
                previous_sample = ExerciseDetail.objects.filter(exercise__id=exercise.pk).order_by('-time')[0]
                if previous_sample:
                    previous_time = previous_sample.time
                # Find time delta, to be used in updating distance, ascent, etc
                time_d = (new_object.time - previous_time).seconds

                # Calculate duration, to be used in calculating new averages
                new_duration = new_object.time - datetime.combine(exercise.date, exercise.time)
                exercise.duration = new_duration
                new_duration = new_duration.seconds

                if new_object.hr:
                    hr = int(new_object.hr)
                    exercise.max_hr = max(hr, exercise.max_hr)
                    if exercise.avg_hr and exercise.duration:
                        exercise.avg_hr = (exercise.avg_hr*old_duration+ hr) / new_duration
                    else:
                        exercise.avg_hr = hr
                if new_object.power:
                    power = int(new_object.power)
                    exercise.max_power = max(power, exercise.max_power)
                    if exercise.avg_power and exercise.duration:
                        exercise.avg_power = (exercise.avg_power*old_duration+ power) / new_duration
                    else:
                        exercise.avg_power = power
                if new_object.cadence:
                    cadence = int(new_object.cadence)
                    exercise.max_cadence = max(cadence, exercise.max_cadence)
                    if exercise.avg_cadence and exercise.duration:
                        exercise.avg_cadence = (exercise.avg_cadence*old_duration+ cadence) / new_duration
                    else:
                        exercise.avg_cadence = cadence
                if new_object.speed:
                    speed = float(new_object.speed)
                    # Update new distance
                    route.distance += speed * time_d

                    exercise.max_speed = max(speed, exercise.max_speed)
                    if exercise.avg_speed and exercise.duration:
                        exercise.avg_speed = (exercise.avg_speed*old_duration+ speed) / new_duration
                    else:
                        exercise.avg_speed = speed
                if new_object.temp:
                    temp = float(new_object.temp)
                    exercise.max_temperature = max(temp, exercise.max_temperature)
                    if exercise.temperature and exercise.duration:
                        exercise.temperature = (exercise.temperature*old_duration+ temp) / new_duration
                    else:
                        exercise.temperature = temp
                    exercise.min_temperature = min(temp, exercise.min_temperature)
                if new_object.altitude and previous_sample:
                    altitude = int(float(new_object.altitude)) # float maybe TODO ?
                    # We have a previous sample and an altitude reading, this 
                    # means we can calculate new ascent or descent
                    if previous_sample.altitude:
                        if altitude > previous_sample.altitude:
                            route.ascent += altitude - previous_sample.altitude
                        else:
                            route.descent += previous_sample.altitude - altitude
                    # Update max and min altitude
                    route.max_altitude = max(altitude, route.max_altitude)
                    route.min_altitude = min(altitude, route.min_altitude)

                route.save() # Save the route - save the world
                exercise.save() # Finally save the new values
                return HttpResponse('Saved OK')
        except Exception, e:
            raise
            return HttpResponse(str(e))

    return HttpResponse('Nothing saved')

def exercise_player(request):

    exercises = []
    ids = request.GET.getlist('id')
    for id in ids:
        try:
            object_id = int(id)
        except ValueError:
            raise Http404()
        exercise = get_object_or_404(Exercise, pk=object_id)
        if exercise.exercise_permission == 'N':
            return redirect_to_login(request.path)
            # TODO Friend check
        exercises.append(exercise)
    if not ids:
        raise Http404()

    for exercise in exercises:
        alt = simplejson.dumps(list(exercise.exercisealtitudegradient_set.values_list('xaxis', 'altitude')))
        alt_max, alt_min = exercise.exercisealtitudegradient_set.aggregate(max=Max('altitude'),min=Min('altitude')).values()
        break

    return render_to_response('turan/exercise_player.html', locals(), context_instance=RequestContext(request))

def exercise_live(request):

    exercise = Exercise.objects.get(pk=4570)

    return render_to_response('turan/exercise_live.html', locals(), context_instance=RequestContext(request))


def fetchRAAM(request):
    #callback = request.GET.get('callback', '')
    req = {}
    url = "http://live.raam.no/LastPing.aspx"
    req ['data'] = urllib2.urlopen(url).read().strip()
    response = simplejson.dumps(req)
    return HttpResponse(response, mimetype="application/json")

@page_template("turan/search/exercise_page.html")
@page_template("turan/search/route_page.html", key="route_page")
def search(request, template='turan/search.html', extra_context=None):
    ''' Global site Search view '''
    search_query = request.GET.get('q', '')
    if not search_query:
        raise Http404

    exercise_list = Exercise.objects.select_related('route', 'tagging_tag', 'tagging_taggeditem', 'exercise_type', 'user__profile', 'user', 'user__avatar', 'avatar')
    comment_list = ThreadedComment.objects.filter(is_public=True).order_by('-date_submitted')
    # Do not include routes with only 1 trip, since they wll be found by exercise search
    route_list = Route.objects.annotate( tcount=Count('exercise') ).filter(tcount__gt=1).order_by('-tcount')
    segment_list = Segment.objects.all()

    tag_list = Tag.objects.all()
    user_list = User.objects.all()
    profile_list = Profile.objects.all()
    qset = (
        Q(route__name__icontains=search_query) |
        Q(comment__icontains=search_query) |
        Q(tags__contains=search_query)
    )
    exercise_list = exercise_list.filter(qset).distinct().order_by('-date')
    uqset = (
        Q(username__icontains=search_query) |
        Q(first_name__icontains=search_query) |
        Q(last_name__icontains=search_query)
    )
    pqset = (
            Q(name__icontains=search_query)
    )
    profile_list = profile_list.filter(pqset).distinct()
    user_list = list(user_list.filter(uqset).distinct())
    for profil in profile_list:
        if not profil.user in user_list:
            user_list.append(profil.user)
    tag_list = tag_list.filter(name__icontains=search_query)
    rqset = (
        Q(name__icontains=search_query) |
        Q(description__icontains=search_query)
    )
    route_list = route_list.filter(rqset).distinct()
    sset = (
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
    )
    segment_list = segment_list.filter(sset).distinct()

    context = locals()
    if extra_context is not None:
        context.update(extra_context)


    return render_to_response(template, context,
            context_instance=RequestContext(request))


@login_required
def photo_add(request, content_type, object_id):
    content_type = get_model('turan', content_type)
    object = get_object_or_404(content_type, pk=object_id)
    photo_form = form_class()

    if request.method == "POST":
        if request.POST.get("action") == "upload":
            photo_form = form_class(request.user, request.POST, request.FILES)
            if photo_form.is_valid():
                photo = photo_form.save(commit=False)
                photo.member = request.user
                photo.save()
                pool = Pool(content_object=content_object, image=photo)
                pool.photo = photo
                pool.save()
                #messages.add_message(request, messages.SUCCESS,
                #    ugettext(_"Successfully uploaded photo '%s'") % photo.title
                #)
    return redirect(object.get_absolute_url())


def json_altitude_gradient(request, object_id):
    ''' Fetch common altitude gradient from db, and serve to javascript
    clients that renders the graph. Used in exercise detail incline sum tab. '''

    # TODO this function can be heavily cached
    # TODO should be class based view
    object = get_object_or_404(Exercise, pk=object_id)
    gradients = simplejson.dumps(list(object.exercisealtitudegradient_set.values_list('xaxis', 'gradient')))
    #js = compress_string(gradients)
    js = gradients
    response = HttpResponse(js, mimetype='application/json')
    #response['Content-Encoding'] = 'gzip'
    response['Content-Length'] = len(js)
    return response
