from django import template
#from django.template import render_to_string #Context, loader
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.template.defaultfilters import floatformat
from django_sorting.templatetags.sorting_tags import SortAnchorNode
from time import mktime

register = template.Library()

# Annoying anchor lib doesn't support translations so I copied it here
@register.tag
def anchortrans(parser, token):
    """
    Parses a tag that's supposed to be in this format:
    {% anchor field title anchor_class anchor_rel %}
    where the 'title', 'anchor_class' and 'anchor_rel' arguments are optional.
    """
    bits = [b.strip('"\'') for b in token.split_contents()]
    if len(bits) < 2:
        raise template.TemplateSyntaxError(
            "anchor tag takes at least 1 argument")
    try:
        title = bits[2]
    except IndexError:
        title = bits[1].capitalize()

    title = _(title.strip())

    if len(bits) >= 4:
        # User specified the anchor_class and anchor_rel arguments
        anchor_class = bits[len(bits)-2]
        anchor_rel = bits[len(bits)-1]
        return SortAnchorNode(bits[1].strip(), title,
                              anchor_class.strip(), anchor_rel.strip())
    return SortAnchorNode(bits[1].strip(), title.strip())

@register.filter
def nbsp(value):
    """ Make sure string can't break """
    return mark_safe(unicode(value).replace(" ", "&nbsp;"))

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

@register.filter
def distanceformat(value):
    if value:
        if value > 9999.9:
            return str(round(value / 1000.0, 1)) + " km"
        else:
            return str(int(round(value, 0))) + " m"
    return value

@register.filter
def exercise_mouseover(obj):
    #t = loader.get_template('turan/exercise/mouseover.html')
    #c = Context({'object': obj})
    #html = t.render(c)
    #return html
    return render_to_string('turan/exercise/mouseover.html', {'object': obj})
