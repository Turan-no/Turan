from django.contrib.auth.models import User
from django.http import Http404

from datetime import datetime

from models import Route, Exercise
from tribes.models import Tribe

from ical import ICalendarFeed
from django.contrib.syndication.feeds import Feed
from django.contrib.syndication import views
from django.utils.translation import ugettext_lazy as _

class ExerciseCalendar(ICalendarFeed):
    ''' Return ical for one user '''


#    def __call__(self, request, username):
#        super(ICalendarFeed, self).__call__(*args, **kwargs)
#

    def __init__(self, username):
        self.user = User.objects.get(username=username)

    def items(self):
        return Exercise.objects.filter(user=self.user)

    def item_uid(self, item):
        return str(item.id)

    def item_start(self, item):
        # Returns combination of date and time if object has one
        # else return the day of the event
        if item.time:
            return datetime(item.date.year, item.date.month, item.date.day,
                    item.time.hour, item.time.minute,
                    item.time.second)

        return item.date

    def item_end(self, item):
        if item.time:
            duration = item.duration
            start = self.item_start(item)
            return start + duration


        # return none
        return

    def item_summary(self, item):
        return item.comment


    def item_location(self, item):
        return unicode(item.route)

class UserTripsFeed(Feed):
    def get_object(self, bits):
        result = User.objects.get(username=bits[0])
        return result

    def title(self, obj):
        return _("Events for %(username)s") % obj.username

    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return obj.get_absolute_url()

    def description(self, obj):
        return "Exercise for %(username)s" % obj.user

    def items(self, obj):
       return Exercise.objects.filter(user=obj.user)

    def item_author_name(self, obj):
        return obj.user


class TeamTripsFeed(views.Feed):

    def get_object(self, request, slug):
        result = Tribe.objects.get(slug=slug)
        return result

    def title(self, obj):
        return _("Events for %s") % obj.name

    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return obj.get_absolute_url()

    def description(self, obj):
        return "Exercises for team %s" % obj.name

    def items(self, obj):
        statsusers = obj.members.all()
        return Exercise.objects.filter(user__in=statsusers)[:20]

    def item_pubdate(self, obj):
        try:
            return datetime(obj.date.year, obj.date.month, obj.date.day, obj.time.hour, obj.time.minute, obj.time.second)
        except AttributeError:
            pass # Some trips just doesn't have time set
        return
