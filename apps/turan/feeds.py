from django.contrib.auth.models import User
from django.http import Http404

from datetime import datetime

from models import Route, Exercise

from ical import ICalendarFeed

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
