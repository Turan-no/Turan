from models import *
from turanprofiles.models import Profile
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, HttpResponsePermanentRedirect
from django.utils.translation import ugettext_lazy as _
from django.template import RequestContext, Context
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django import forms
from django.core.urlresolvers import reverse
from django.db.models import Avg, Max, Min, Count, Variance, StdDev, Sum
from django.contrib.syndication.feeds import Feed
from django.contrib.comments.models import Comment
from django.core.files.storage import FileSystemStorage
from django.utils.safestring import mark_safe
from django.core.paginator import Paginator
from django.core import serializers

from datetime import timedelta, datetime
from time import mktime
import locale

from svg import GPX2SVG
from turancalendar import WorkoutCalendar

from hrmparser import HRMParser
from gmdparser import GMDParser
from tcxparser import TCXParser

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

    route_list = Route.objects.all().order_by('name')
    cycletrip_list = CycleTrip.objects.all().order_by('-date')[:15]
    hike_list = Hike.objects.all().order_by('-date')[:15]
    exercise_list = OtherExercise.objects.all().order_by('-date')[:15]
    #user_list = UserProfile.objects.all()
    comment_list = Comment.objects.order_by('-submit_date')[:5]

    return render_to_response('turan/index.html', locals(), context_instance=RequestContext(request))

class UploadFileForm(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput())
    file = forms.FileField()

@login_required
def upload_eventdetails(request, object_id, event_type):
    ''' The view that takes care of parsing data file from sports equipment from polar or garmin and putting values into the detail-db, and also summarized values for trip. '''

    id = object_id

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            filename = file.name

            if filename.endswith('.hrm'): # Polar !
                parser = HRMParser()
            elif filename.endswith('.gmd'): # garmin-tools-dump
                parser = GMDParser()
            elif filename.endswith('.tcx'): # garmin training centre
                parser = TCXParser(gps_distance=False) #should have menu on
                                                       #upload page 
            else:
                return HttpResponse(_('Wrong filetype!'))
            parser.parse_uploaded_file(file)
            values = parser.entries
            id = form.cleaned_data['id']

            for val in values:
                if event_type == 'hike':
                    d = HikeDetail()
                elif event_type == 'cycletrip':
                    d = CycleTripDetail()
                elif event_type == 'exercise':
                    d = OtherExerciseDetail()

                d.trip_id = id
                d.time = val.time
                d.hr = val.hr
                d.altitude = val.altitude
                d.speed = val.speed
                d.cadence = val.cadence
                d.lat = val.lat
                d.lon = val.lon
                d.save()


            if event_type == 'hike':
                e = Hike.objects.get(pk=id)
                # TODO: add normalize for hikes
            elif event_type == 'cycletrip':
                e = CycleTrip.objects.get(pk=id)
                # Normalize altitude, that is, if it's below zero scale every value up
                normalize_altitude(id)
            elif event_type == 'exercise':
                e = OtherExercise.objects.get(pk=id)
                # TODO: add normalize for OtherExercise

            e.max_hr = parser.max_hr
            e.max_speed = parser.max_speed
            e.max_cadence = parser.max_cadence

            e.avg_hr = parser.avg_hr
            e.avg_speed = parser.avg_speed
            e.avg_cadence = parser.avg_cadence
            
            e.kcal = parser.kcal_sum

            e.duration = parser.duration

            if not e.route.distance:
                if parser.distance_sum:
                    e.route.distance = parser.distance_sum

            e.save()
            return HttpResponseRedirect(e.get_absolute_url())
    else:
        form = UploadFileForm(initial={'id': id})
    return render_to_response('turan/tripdetail_form.html', {'form': form, 'id': id, }, context_instance=RequestContext(request))


def trip_compare(request, trip1, trip2):
    trip1 = get_object_or_404(CycleTrip, pk=trip1)
    trip2 = get_object_or_404(CycleTrip, pk=trip2)

    t1_speed = tripdetail_js('cycletrip', trip1.id, 'speed')
    t2_speed = tripdetail_js('cycletrip', trip2.id, 'speed')
    t1_hr = tripdetail_js('cycletrip', trip1.id, 'hr')
    t2_hr = tripdetail_js('cycletrip', trip2.id, 'hr')
    t1_cad = tripdetail_js('cycletrip', trip1.id, 'cadence')
    t2_cad = tripdetail_js('cycletrip', trip2.id, 'cadence')

    alt = tripdetail_js('cycletrip', trip1.id, 'altitude')

    alt_max = trip1.cycletripdetail_set.aggregate(Max('altitude'))['altitude__max']*2

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

def events(request):
    object_list = []
    cycleqs = CycleTrip.objects.select_related()
    hikeqs = Hike.objects.select_related()
    exerciseqs = OtherExercise.objects.select_related()

    object_list.extend(cycleqs)
    object_list.extend(hikeqs)
    object_list.extend(exerciseqs)
    object_list = sorted(object_list, key=lambda x: x.date)
    object_list.reverse()

    paginator = Paginator(object_list, 15)
    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        events = paginator.page(page)
    except (EmptyPage, InvalidPage):
        events = paginator.page(paginator.num_pages)


    
    return render_to_response('turan/event_list.html', locals(), context_instance=RequestContext(request))

def route_detail(request, object_id):
    object = get_object_or_404(Route, pk=object_id)
    speeddataseries = ''

    def getjsdatapoint(trip):
        if trip.duration:
            time = trip.duration.seconds/60
            speeddataseries =  '[%s, %s],' % (datetime2jstimestamp(trip.date), time)
            return speeddataseries
        return ''
    for trip in object.hike_set.all():
        speeddataseries += getjsdatapoint(trip)
    for trip in object.cycletrip_set.all():
        speeddataseries += getjsdatapoint(trip)
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

def statistics(request):

    stats_dict = CycleTrip.objects.aggregate(Max('avg_speed'), Avg('avg_speed'), Avg('route__distance'), Max('route__distance'), Sum('route__distance'), Avg('duration'), Max('duration'), Sum('duration'))
    total_duration = stats_dict['duration__sum']
    total_distance = stats_dict['route__distance__sum']
    total_avg_speed = stats_dict['avg_speed__avg']
    longest_trip = stats_dict['route__distance__max']

    userstats = Profile.objects.annotate( \
            avg_avg_speed = Avg('user__cycletrip__avg_speed'), \
            max_avg_speed = Max('user__cycletrip__avg_speed'), \
            max_speed = Max('user__cycletrip__max_speed'), \
            num_trips = Count('user__cycletrip'), \
            sum_distance = Sum('user__cycletrip__route__distance'), \
            sum_duration = Sum('user__cycletrip__duration'), \
            sum_energy = Sum('user__cycletrip__kcal'), \
            sum_ascent = Sum('user__cycletrip__route__ascent') \
            )

    maxavgspeeds = userstats.filter(max_avg_speed__gt=0.0).order_by('max_avg_speed').reverse()
    maxspeeds = userstats.filter(max_speed__gt=0.0).order_by('max_speed').reverse()
    avgspeeds = userstats.filter(avg_avg_speed__gt=0.0).order_by('avg_avg_speed').reverse()
    numtrips = userstats.filter(num_trips__gt=0).order_by('num_trips').reverse()
    distsums = userstats.filter(sum_distance__gt=0).order_by('sum_distance').reverse()
    dursums = userstats.filter(sum_duration__gt=0).order_by('sum_duration').reverse()
    energysums = userstats.filter(sum_energy__gt=0).order_by('sum_energy').reverse()
    ascentsums = userstats.filter(sum_ascent__gt=0).order_by('sum_ascent').reverse()

    validroutes = Route.objects.filter(ascent__gt=0).filter(distance__gt=0)
    climbstats = Profile.objects.filter(user__cycletrip__route__in=validroutes).annotate( \
            distance = Sum('user__cycletrip__route__distance'), \
            height = Sum('user__cycletrip__route__ascent') \
            )

    for u in climbstats:
        u.avgclimb = u.height/u.distance
    climbstats = sorted(climbstats, key=lambda x: -x.avgclimb)

    hikestats = Profile.objects.annotate( \
            hike_avg_avg_speed = Avg('user__hike__avg_speed'), \
            hike_max_avg_speed = Max('user__hike__avg_speed'), \
            hike_max_speed = Max('user__hike__max_speed'), \
            hike_num_trips = Count('user__hike'), \
            hike_sum_distance = Sum('user__hike__route__distance'), \
            hike_sum_duration = Sum('user__hike__duration'), \
            hike_sum_energy = Sum('user__hike__kcal'), \
            hike_sum_ascent = Sum('user__hike__route__ascent') \
            )

    hike_maxavgspeeds = hikestats.filter(hike_max_avg_speed__gt=0.0).order_by('hike_max_avg_speed').reverse()
    hike_maxspeeds = hikestats.filter(hike_max_speed__gt=0.0).order_by('hike_max_speed').reverse()
    hike_avgspeeds = hikestats.filter(hike_avg_avg_speed__gt=0.0).order_by('hike_avg_avg_speed').reverse()
    hike_numtrips = hikestats.filter(hike_num_trips__gt=0).order_by('hike_num_trips').reverse()
    hike_distsums = hikestats.filter(hike_sum_distance__gt=0).order_by('hike_sum_distance').reverse()
    hike_dursums = hikestats.filter(hike_sum_duration__gt=0).order_by('hike_sum_duration').reverse()
    hike_energysums = hikestats.filter(hike_sum_energy__gt=0).order_by('hike_sum_energy').reverse()
    hike_ascentsums = hikestats.filter(hike_sum_ascent__gt=0).order_by('hike_sum_ascent').reverse()

    hike_climbstats = Profile.objects.filter(user__hike__route__in=validroutes).annotate( \
            distance = Sum('user__hike__route__distance'), \
            height = Sum('user__hike__route__ascent') \
            )

    for u in hike_climbstats:
        u.avgclimb = u.height/u.distance
    hike_climbstats = sorted(hike_climbstats, key=lambda x: -x.avgclimb)

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


class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ('name', 'distance', 'description', 'gpx_file')

@login_required
def route_new(request):
    if request.method == 'POST':
        routeform = RouteForm(request.POST, request.FILES)
        if routeform.is_valid():
            print 'valid!'
            gpxfile = request.FILES['gpx_file']
            filename = gpxfile.name
            print filename

            if not filename.endswith('.gpx'):
                return HttpResponse(_('Wrong filetype!'))
            
            route = routeform.save()
            return HttpResponseRedirect(route.get_absolute_url())
        else:
            return HttpResponse(_('Error while parsing form'))
    else:
        routeform = RouteForm()
        return render_to_response('turan/route_new.html', locals(), context_instance=RequestContext(request))


def calendar(request, year=False, month=False, user_id=False):
    if not year:
        year = datetime.now().year
        month = datetime.now().month
    else:
        year, month = int(year), int(month)
    cycletrips = CycleTrip.objects.order_by('date').filter(
            date__year=year, date__month=month)
    hikes = Hike.objects.order_by('date').filter(
            date__year=year, date__month=month)
    exercices = OtherExercise.objects.order_by('date').filter(
            date__year=year, date__month=month)

    if user_id:
        cycletrips = cycletrips.filter(user=user_id)
        hikes = hikes.filter(user=user_id)
        exercices = exercices.filter(user=user_id)


    months = []
    workouts = []
    workouts.extend(cycletrips)
    workouts.extend(hikes)
    workouts.extend(exercices)
    workouts = sorted(workouts, key=lambda x: x.date)

    #for x in cycletrips, hikes, exercices:
    #    dates = x.dates('date', 'month')
    #    if len(dates) > 0:
    #        for month in dates:
    #            if not month in months:
    #                months.append(month)
    #    else:
    #        if not dates in months:
    #            months.append(dates)


   # FIXME django locale
    cal = WorkoutCalendar(workouts, locale.getdefaultlocale()).formatmonth(year, month)
    return render_to_response('turan/calendar.html', {'calendar': mark_safe(cal), 'months': months,}, context_instance=RequestContext(request))

def tripdetail_js(event_type, object_id, val, start=False, stop=False):
    if start:
        start = int(start)
    if stop:
        stop = int(stop)
    if event_type == 'cycletrip':
        qs = CycleTripDetail.objects.filter(trip=object_id)

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
    inslope = False
    for i in xrange(1,len(values)):
        if inslope:
            if values[i].altitude > values[cur_end].altitude:
                cur_end = i
            hdelta = values[cur_end].altitude - values[cur_start].altitude
            if values[i].altitude < values[cur_start].altitude + hdelta*0.9 or i == len(values):
                inslope = False
                if hdelta >= min_slope:
                    distance = getdistance(values, cur_start, cur_end)
                    slopes.append(Slope(cur_start, cur_end, distance, hdelta, hdelta/distance * 100))
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

def getavghr(values, start, end):
    hr = 0
    for i in xrange(start+1, end+1):
        delta_t = (values[i].time - values[i-1].time).seconds
        hr += values[i].hr*delta_t
    delta_t = (values[end].time - values[start].time).seconds
    return float(hr)/delta_t

class Slope(object):
    def __init__(self, start, end, length, hdelta, gradient):
        self.start = start
        self.end = end
        self.length = length
        self.hdelta = hdelta
        self.gradient = gradient

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
    #userweight = object.user.userprofile_set.all()[0].weight
    userweight = object.user.get_profile().weight
    slopes = getslopes(details)
    for slope in slopes:
        delta_t = (details[slope.end].time - details[slope.start].time).seconds
        slope.speed = slope.length/delta_t * 3.6
        slope.avg_hr = getavghr(details, slope.start, slope.end)
        slope.avg_power = calcpower(userweight, 10, slope.gradient, slope.speed/3.6)
    
    speedjs = tripdetail_js('cycletrip', object_id, 'speed')
    hrjs = tripdetail_js('cycletrip', object_id, 'hr')
    cadencejs = tripdetail_js('cycletrip', object_id, 'cadence')
    altitudejs = tripdetail_js('cycletrip', object_id, 'altitude')
    return render_to_response('turan/cycletrip_detail.html', locals(), context_instance=RequestContext(request))
