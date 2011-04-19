from calendar import LocaleHTMLCalendar
from datetime import date, timedelta
from itertools import groupby
from django.utils.translation import ugettext_lazy as _
from django.utils.html import conditional_escape as esc
from turan.templatetags.turan_extras import exercise_mouseover

class WorkoutCalendar(LocaleHTMLCalendar):
    sums = {
                'kcal_sum': 0,
                'distance_sum': 0,
                'duration_sum': timedelta(0),
                }

    def __init__(self, workouts, locale):
        super(WorkoutCalendar, self).__init__(locale=locale)
        self.current_week = 0
        self.workouts = self.group_by_day(workouts)
        self.workouts_by_week = self.group_by_week(workouts)
        self.week_sums = self.get_week_sums()

    def formatmonthname(self, *args, **kwargs):
        ''' We do not want monthname displayed on top '''
        return ''

    def formatday(self, day, weekday):
        # Day outside month are 0
        #week = int(working_date.strftime('%W'))+1

        try:
            working_date = date(self.year, self.month, day)
            if date.today() == working_date:
                cssclass += ' today'
        except:
            pass # Code excepts for day = 0 outside month
        if self.current_week in self.workouts_by_week:
            cssclass = self.cssclasses[weekday]
            workouts_by_weekday = self.group_by_weekday(self.workouts_by_week[self.current_week])
            #assert False, (week, weekday)
            body =[]
            if weekday in workouts_by_weekday:
                cssclass += ' filled'
                body = ['<ul>']
                mouseover_html = []
                for workout in workouts_by_weekday[weekday]:
                    body.append('<li class="hoverpoint" id="workout_%s">' %workout.id)
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
                    mouseover_html.append(unicode(exercise_mouseover(workout)))
                body.append('</ul>')

                body.append(''.join(mouseover_html))
                dayhtml = '<div class="day">%d</div>' %day
                if day == 0:
                    dayhtml = ''
                return self.day_cell(cssclass, '%s %s' % (dayhtml, ''.join(body)))
        return self.day_cell('noday', '&nbsp;')

    def get_week_sums(self):
        week_sums = {}
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
            week_sums[week] = w_sums
        if not self.current_week:
            if self.workouts_by_week.keys():
                self.current_week = sorted(self.workouts_by_week.keys())[0]

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
        week['week'] = self.current_week
        week['distance_sum'] = round(week['distance_sum'], 1) # Haters

        # Translate 
        for t_key in ('Week', 'Distance', 'Kcal', 'Duration'):
            week[t_key] = _(t_key)

        self.current_week += 1
        return '<tr>%(days)s<td> \
                <p>\
                <span class="label">%(Week)s:</span> %(week)s<br>\
                <span class="label">%(Distance)s:</span> %(distance_sum)s<br>\
                <span class="label">%(Kcal)s:</span> %(kcal_sum)s<br>\
                <span class="label">%(Duration)s:</span> %(duration_sum)s\
                </p>\
                </td></tr>' % week

    def formatmonth(self, year, month):
        self.year, self.month = year, month
        return super(WorkoutCalendar, self).formatmonth(year, month)


    def group_by_week(self, workouts):
        field = lambda workout: int(workout.date.strftime('%W'))
        return dict(
            [(week, list(items)) for week, items in groupby(workouts, field)]
        )

    def group_by_day(self, workouts):
        field = lambda workout: workout.date.day
        return dict(
            [(day, list(items)) for day, items in groupby(workouts, field)]
        )
    def group_by_weekday(self, workouts):
        field = lambda workout: workout.date.weekday()
        return dict(
            [(weekday, list(items)) for weekday, items in groupby(workouts, field)]
        )

    def day_cell(self, cssclass, body):
        return '<td class="%s">%s</td>' % (cssclass, body)

