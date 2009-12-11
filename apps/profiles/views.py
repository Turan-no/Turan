from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseForbidden
from django.conf import settings
from django.db.models import Avg, Max, Min, Count, Variance, StdDev, Sum

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from time import mktime
from datetime import timedelta, datetime

from friends.forms import InviteFriendForm
from friends.models import FriendshipInvitation, Friendship

from microblogging.models import Following

from profiles.models import Profile, UserProfileDetail
from profiles.forms import ProfileForm

from avatar.templatetags.avatar_tags import avatar

from itertools import groupby
#from gravatar.templatetags.gravatar import gravatar as avatar

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

def datetime2jstimestamp(obj):
    ''' Helper to generate js timestamp for usage in flot '''
    return mktime(obj.timetuple())*1000

def profiles(request, template_name="profiles/profiles.html", extra_context=None):
    if extra_context is None:
        extra_context = {}
    users = User.objects.all().order_by("-date_joined")
    search_terms = request.GET.get('search', '')
    order = request.GET.get('order')
    if not order:
        order = 'date'
    if search_terms:
        users = users.filter(username__icontains=search_terms)
    if order == 'date':
        users = users.order_by("-date_joined")
    elif order == 'name':
        users = users.order_by("username")
    elif order == 'time':

        users = users.annotate(c =
                Sum('cycletrip__duration'),h =
                Sum('hike__duration'),e =
                Sum('otherexercise__duration'))
        for u in users:
            if not u.e: u.e = 0
            if not u.h: u.h = 0
            if not u.c: u.c = 0
        users = sorted(users, key=lambda x: -x.c-x.h-x.e)
    return render_to_response(template_name, dict({
        'users': users,
        'order': order,
        'search_terms': search_terms,
    }, **extra_context), context_instance=RequestContext(request))

def profile(request, username, template_name="profiles/profile.html", extra_context=None):
    if extra_context is None:
        extra_context = {}
    other_user = get_object_or_404(User, username=username)
    if request.user.is_authenticated():
        is_friend = Friendship.objects.are_friends(request.user, other_user)
        is_following = Following.objects.is_following(request.user, other_user)
        other_friends = Friendship.objects.friends_for_user(other_user)
        if request.user == other_user:
            is_me = True
        else:
            is_me = False
    else:
        other_friends = []
        is_friend = False
        is_me = False
        is_following = False
    
    if is_friend:
        invite_form = None
        previous_invitations_to = None
        previous_invitations_from = None
        if request.method == "POST":
            if request.POST["action"] == "remove":
                Friendship.objects.remove(request.user, other_user)
                request.user.message_set.create(message=_("You have removed %(from_user)s from friends") % {'from_user': other_user})
                is_friend = False
                invite_form = InviteFriendForm(request.user, {
                    'to_user': username,
                    'message': ugettext("Let's be friends!"),
                })

    else:
        if request.user.is_authenticated() and request.method == "POST":
            if request.POST["action"] == "invite":
                invite_form = InviteFriendForm(request.user, request.POST)
                if invite_form.is_valid():
                    invite_form.save()
            else:
                invite_form = InviteFriendForm(request.user, {
                    'to_user': username,
                    'message': ugettext("Let's be friends!"),
                })
                invitation_id = request.POST.get("invitation", "")
                if request.POST["action"] == "accept": # @@@ perhaps the form should just post to friends and be redirected here
                    try:
                        invitation = FriendshipInvitation.objects.get(id=invitation_id)
                        if invitation.to_user == request.user:
                            invitation.accept()
                            request.user.message_set.create(message=_("You have accepted the friendship request from %(from_user)s") % {'from_user': invitation.from_user})
                            is_friend = True
                            other_friends = Friendship.objects.friends_for_user(other_user)
                    except FriendshipInvitation.DoesNotExist:
                        pass
                elif request.POST["action"] == "decline":
                    try:
                        invitation = FriendshipInvitation.objects.get(id=invitation_id)
                        if invitation.to_user == request.user:
                            invitation.decline()
                            request.user.message_set.create(message=_("You have declined the friendship request from %(from_user)s") % {'from_user': invitation.from_user})
                            other_friends = Friendship.objects.friends_for_user(other_user)
                    except FriendshipInvitation.DoesNotExist:
                        pass
        else:
            invite_form = InviteFriendForm(request.user, {
                'to_user': username,
                'message': ugettext("Let's be friends!"),
            })
    previous_invitations_to = FriendshipInvitation.objects.filter(to_user=other_user, from_user=request.user).exclude(status=8).exclude(status=6)
    previous_invitations_from = FriendshipInvitation.objects.filter(to_user=request.user, from_user=other_user).exclude(status=8).exclude(status=6)
    
    if is_me:
        if request.method == "POST":
            if request.POST["action"] == "update":
                profile_form = ProfileForm(request.POST, instance=other_user.get_profile())
                if profile_form.is_valid():
                    profile = profile_form.save(commit=False)
                    profile.user = other_user
                    profile.save()
            else:
                profile_form = ProfileForm(instance=other_user.get_profile())
        else:
            profile_form = ProfileForm(instance=other_user.get_profile())
    else:
        profile_form = None

    total_duration = timedelta()
    total_distance = 0
    total_avg_speed = 0
    total_avg_hr = 0

    nr_trips = 0
    nr_hr_trips = 0
    longest_trip = 0
    avg_length = 0
    avg_duration = 0

    bmidataseries = ''
    bmiline = ''
    pulsedataseries = ""
    tripdataseries = ""
    avgspeeddataseries = ""
    avghrdataseries = ""
    height = other_user.get_profile().height
    if height:
        height = float(other_user.get_profile().height)/100
        weightqs = other_user.get_profile().userprofiledetail_set.filter(weight__isnull=False).order_by('time')
        for wtuple in weightqs.values_list('time', 'weight'):
            bmidataseries += '[%s, %s],' % (datetime2jstimestamp(wtuple[0]), wtuple[1]/(height*height))
            bmiline += '[%s, 25],' %datetime2jstimestamp(wtuple[0])

    pulseqs = other_user.get_profile().userprofiledetail_set.filter(resting_hr__isnull=False).order_by('time')
    for hrtuple in pulseqs.values_list('time', 'resting_hr'):
        pulsedataseries += '[%s, %s],' % (datetime2jstimestamp(hrtuple[0]), hrtuple[1])

    exerciseqs = other_user.exercise_set.order_by('date')

    for trip in exerciseqs:
        tripdataseries += '[%s, %s],' % ( nr_trips, trip.route.distance)

        if trip.route.distance > longest_trip:
            longest_trip = trip.route.distance

        if trip.duration:
            total_duration += trip.duration
        total_distance += trip.route.distance
        if trip.avg_speed:
            # only increase counter if trip has speed
            avgspeeddataseries += '[%s, %s],' % (datetime2jstimestamp(trip.date), trip.avg_speed)
            total_avg_speed += trip.avg_speed
            nr_trips += 1
    if total_avg_speed:
        total_avg_speed = total_avg_speed/nr_trips

    for event in exerciseqs:
        if event.avg_hr:
            avghrdataseries += '[%s, %s],' % (datetime2jstimestamp(event.date), event.avg_hr)
            total_avg_hr += event.avg_hr
            nr_hr_trips += 1

    if total_avg_hr:
        total_avg_hr = total_avg_hr/nr_hr_trips

    total_kcals = max(0, other_user.exercise_set.aggregate(Sum('kcal'))['kcal__sum'])

# TODO fix total_duration for hike and otherexercise
# Todo filter ?

    for cycletrip in exerciseqs:
        if exerciseqs[0].date:
            days_since_start = (datetime.now() - datetime(exerciseqs[0].date.year, exerciseqs[0].date.month, exerciseqs[0].date.day, 0, 0, 0)).days
# TODO check in exercise and hike for first
            if days_since_start == 0: # if they only have one trip and it was today
                days_since_start = 1
            km_per_day = total_distance / days_since_start
            kcal_per_day = total_kcals / days_since_start
            time_per_day = total_duration / days_since_start



# TODO check for faulty date
    try:
        workouts_by_week =  dict( [(week, list(items)) for week, items in groupby(exerciseqs, lambda workout: workout.date.strftime('%W'))])
    except:
        pass
    return render_to_response(template_name, locals(),
            context_instance=RequestContext(request))
