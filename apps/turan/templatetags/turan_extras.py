from django import template
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import floatformat
from time import mktime

register = template.Library()

@register.filter
def bodyfat(value):
    """ Converts a kcal value to bodyfat value """
    return float(value)/7800

@register.filter
def retarddurationformat(value, longFormat=True):
    """ Converts a number of retarded ms to textual string """
    return durationformat(int(value / 1000000), longFormat)

@register.filter
def durationformat(value, longFormat=True):
    """ Converts a number of seconds to a textual string """

    string = ""

    yearSec = 31536000
    monthSec = 2592000
    daySec = 86400
    hourSec = 3600
    minSec = 60

    years = months = days = hours = mins = secs = 0

    if value >= yearSec:
        years = int(value / yearSec)
        value = value - (years * yearSec)
        if longFormat == False:
            yStr = _("y")
        elif years > 1:
            yStr = _(" years")
        else:
            yStr = _(" year")
        if len(string) > 0 and string[-1] != ' ':
            string = string + " "
        string = u"%s%s%s" % (string, years, yStr)

    if value >= monthSec:
        months = int(value / monthSec)
        value = value - (months * monthSec)
        if longFormat == False:
            mStr = _("mth")
        elif months > 1:
            mStr = _(" months")
        else:
            mStr = _(" month")
        if len(string) > 0 and string[-1] != ' ':
            string = string + " "

        string = u"%s%s%s" % (string, months, mStr)

    if value >= daySec:
        days = int(value / daySec)
        value = value - (days * daySec)
        if longFormat == False:
            dStr = _("d")
        elif days > 1:
            dStr = _(" days")
        else:
            dStr = _(" day")
        if len(string) > 0 and string[-1] != ' ':
            string = string + " "

        string = u"%s%s%s" % (string, days, dStr)

    if value >= hourSec:
        hours = int(value / hourSec)
        value = value - (hours * hourSec)
        if longFormat == False:
            hStr = _("h")
        elif hours > 1:
            hStr = _(" hours")
        else:
            hStr = _(" hour")
        if len(string) > 0 and string[-1] != ' ':
            string = string + " "

        string = u"%s%s%s" % (string, hours, hStr)

    if value >= minSec:
        mins = int(value / minSec)
        value = value - (mins * minSec)
        if longFormat == False:
            minStr = _("m")
        elif mins > 1:
            minStr = _(" minutes")
        else:
            minStr = _(" minute")
        if len(string) > 0 and string[-1] != ' ':
            string = string + " "

        string = u"%s%s%s" % (string, mins, minStr)

    if value > 0:
        secs = value
        if longFormat == False:
            sStr = _("s")
        elif secs > 1:
            sStr = _(" seconds")
        else:
            sStr = _(" second")
        if len(string) > 0 and string[-1] != ' ':
            string = string + " "

        string = u"%s%s%s" % (string, secs, sStr)

    if len(string) == 0:
        string = _("Zero time")

    return string

@register.filter
def percent(value, arg):
    "Divides the value by the arg * 100"
    return floatformat(float(value) * 100 / float(arg)) + u'%'
percent.is_safe = False

@register.filter
def divide(value, arg):
    return floatformat(float(value) / float(arg))
percent.is_safe = False

@register.filter
def jstimestamp(value):
    ''' Helper to generate js timestamp for usage in flot '''
    return mktime(value.timetuple())*1000

@register.filter
def model_verbose_name(obj):
    ''' Return a model's verbose name '''
    return obj._meta.verbose_name

@register.filter
def model_verbose_name_plural(obj):
    ''' Return a model's verbose plural name '''
    return obj._meta.verbose_name_plural

