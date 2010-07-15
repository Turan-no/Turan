from calendar import LocaleHTMLCalendar
from datetime import date, timedelta
from itertools import groupby

from django.utils.html import conditional_escape as esc

class WorkoutCalendar(LocaleHTMLCalendar):
    sums = {
                'kcal_sum': 0,
                'distance_sum': 0,
                'duration_sum': timedelta(0),
                }

    def __init__(self, workouts, locale):
        super(WorkoutCalendar, self).__init__(locale=locale)
        self.workouts = self.group_by_day(workouts)
        self.workouts_by_week = self.group_by_week(workouts)
        self.week_sums = self.get_week_sums()
        self.current_week = 0

    def formatday(self, day, weekday):
        if day != 0:
            cssclass = self.cssclasses[weekday]
            if date.today() == date(self.year, self.month, day):
                cssclass += ' today'
            if day in self.workouts:
                cssclass += ' filled'
                body = ['<ul>']
                for workout in self.workouts[day]:
                    body.append('<li>')
                    body.append('<a href="%s">' % workout.get_absolute_url())
                    body.append('<img src="' + workout.icon() + '" />')
                    body.append(esc(workout))
                    body.append('</a>')
                    body.append('<p class="fade">')
                    if workout.route and workout.route.distance:
                        body.append('%.1f&nbsp;km' %workout.route.distance)
                        body.append(', ')
                    body.append(esc(workout.kcal) + '&nbsp;kcal')
                    body.append(', ')
                    body.append(esc(str(workout.duration).replace(" ", "&nbsp;")))
                    body.append('</p>')
                    body.append('</li>')
                body.append('</ul>')
                return self.day_cell(cssclass, '<div class="day">%d</div> %s' % (day, ''.join(body)))
            return self.day_cell(cssclass, '<div class="day">%d</div>' % (day))
        return self.day_cell('noday', '&nbsp;')

    def get_week_sums(self):
        week_sums = {}
        i = 0
        for week, workouts in self.workouts_by_week.items():
            w_sums = self.sums.copy()
            for workout in workouts:
                w_sums['kcal_sum'] += workout.kcal
                try:
                    w_sums['distance_sum'] += workout.route.distance
                except AttributeError:
                    pass # some exercises doesn't have distance
                try:
                    w_sums['duration_sum'] += workout.duration
                except TypeError:
                    pass # fukken durationfield is sometimes decimal
            week_sums[i] = w_sums
            i += 1
            

        return week_sums

    def formatweek(self, theweek):
        """
        Return a complete week as a table row.
        """

        s = ''.join(self.formatday(d, wd) for (d, wd) in theweek)
        week = { 'days': s }
        if self.current_week in self.week_sums:
            week.update(self.week_sums[self.current_week])
        else:
            week.update(self.sums)
        self.current_week += 1
        return '<tr>%(days)s<td> \
                <p>\
                <span class="label">Distance:</span> %(distance_sum)s<br>\
                <span class="label">Kcal:</span> %(kcal_sum)s<br>\
                <span class="label">Duration:</span> %(duration_sum)s\
                </p>\
                </td></tr>' % week

    def formatmonth(self, year, month):
        self.year, self.month = year, month
        return super(WorkoutCalendar, self).formatmonth(year, month)


    def group_by_week(self, workouts):
        field = lambda workout: int(workout.date.strftime('%W'))+1
        return dict(
            [(week, list(items)) for week, items in groupby(workouts, field)]
        )

    def group_by_day(self, workouts):
        field = lambda workout: workout.date.day
        return dict(
            [(day, list(items)) for day, items in groupby(workouts, field)]
        )

    def day_cell(self, cssclass, body):
        return '<td class="%s">%s</td>' % (cssclass, body)

