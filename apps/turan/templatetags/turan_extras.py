from django import template
from django.conf import settings
#from django.template import render_to_string #Context, loader
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.template.defaultfilters import floatformat, stringfilter
from django_sorting.templatetags.sorting_tags import SortAnchorNode
from friends.models import Friendship
from endless_pagination import utils
from endless_pagination import settings as endless_settings
from endless_pagination.paginator import DefaultPaginator, LazyPaginator, EmptyPage
from time import mktime
import simplejson as json
import re
from django.contrib.contenttypes.models import ContentType
from phileo.models import Like

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
def player_icon(player, exercise_type,w=24,h=24):
    playercolors = [
        { "r": 255, "g": 20, "b": 20 },
        { "r": 20, "g": 20, "b": 255 },
        { "r": 20, "g": 255, "b": 255 },
        { "r": 255, "g": 20, "b": 255 },
        { "r": 255, "g": 255, "b": 20 },
        { "r": 80, "g": 80, "b": 80 }
    ]
    return "/generate/icon?i=/turan/%s&r=%d&g=%d&b=%d&h=%d&w=%d" % ( exercise_type.logo, playercolors[player]["r"], playercolors[player]["g"], playercolors[player]["b"], h, w )

@register.filter
def player_icon_huge(player, exercise_type,w=32,h=32):
    return player_icon(player, exercise_type, w, h)

@register.filter
def nbsp(value):
    """ Make sure string can't break """
    return mark_safe(unicode(value).replace(" ", "&nbsp;"))

@register.filter
def u_slugify(txt):
    """A custom version of slugify that retains non-ascii characters. The purpose of this
    function in the application is to make URLs more readable in a browser, so there are 
    some added heuristics to retain as much of the title meaning as possible while 
    excluding characters that are troublesome to read in URLs. For example, question marks 
    will be seen in the browser URL as %3F and are thereful unreadable. Although non-ascii
    characters will also be hex-encoded in the raw URL, most browsers will display them
    as human-readable glyphs in the address bar -- those should be kept in the slug."""
    txt = txt.strip() # remove trailing whitespace
    txt = re.sub('\s*-\s*','-', txt, re.UNICODE) # remove spaces before and after dashes
    txt = re.sub('[\s/]', '_', txt, re.UNICODE) # replace remaining spaces with underscores
    txt = re.sub('(\d):(\d)', r'\1-\2', txt, re.UNICODE) # replace colons between numbers with dashes
    txt = re.sub('"', "'", txt, re.UNICODE) # replace double quotes with single quotes
    txt = re.sub(r'[?,:!@#~`+=$%^&\\*()\[\]{}<>]','',txt, re.UNICODE) # remove some characters altogether
    return txt

@register.filter
def bodyfat(value):
    """ Converts a kcal value to bodyfat value """
    return float(value)/7800

@register.filter
def retarddurationformat(value, longFormat=False):
    """ Converts a number of retarded ms to textual string """
    return durationformat(int(value / 1000000), longFormat)

@register.filter
def durationformatshort(value):
    string = ""

    daySec = 86400
    hourSec = 3600
    minSec = 60

    years = months = days = hours = mins = secs = 0
    if value >= daySec:
        days = int(value / daySec)
        value = value - (days * daySec)
        dStr = ''
        string = u"%s%02d%s" % (string, days, dStr)

    if value >= hourSec:
        hours = int(value / hourSec)
        value = value - (hours * hourSec)
        hStr = ":"
        string = u"%s%02d%s" % (string, hours, hStr)

    if value >= minSec:
        mins = int(value / minSec)
        value = value - (mins * minSec)
        minStr = ":"
        string = u"%s%02d%s" % (string, mins, minStr)

    #if value > 0:
    secs = value
    sStr = ":"
    string = u"%s%02d%s" % (string, secs, sStr)

    if len(string) == 0:
        string = '0'

    return string.strip(':')

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
    if value and arg:
        return floatformat(float(value) * 100 / float(arg)) + u'%'
percent.is_safe = False

@register.filter
def divide(value, arg):
    try:
        return floatformat(float(value) / float(arg))
    except ValueError:
        return 0
    except TypeError:
        return 0
    except ZeroDivisionError:
        return 0

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

@register.inclusion_tag("turan/exercise/mouseover.html", takes_context=False)
def exercise_mouseover(obj, placement='right'):
    return {'object': obj, 'placement': placement}

@register.inclusion_tag("profile_hover.html", takes_context=False)
def profile_hover(obj, placement="right"):
    return {'object': obj, 'placement': placement}

@register.filter
def silk_icon(name):
    return settings.MEDIA_URL + 'pinax/img/silk/icons/%s.png' %name
@register.filter
def silk_sprite(name):
    return '<i class="ss_sprite ss_%s"></i>' %name
silk_sprite.is_safe = True

@register.filter
def as_json(obj):
    return json.dumps(obj)

@register.filter(name='truncatechars')
@stringfilter
def truncatechars(value, arg):
    """
    Truncates a string after a certain number of chars.

    Argument: Number of chars to truncate after.
    """
    try:
        length = int(arg)
    except ValueError: # Invalid literal for int().
        return value # Fail silently.
    if len(value) > length:
        return value[:length] + '...'
    return value
truncatechars.is_safe = True

@register.filter
def exercise_view_permission(exercise, user):
    if exercise.user == user:  # Allow self
        return True
    if exercise.exercise_permission == 'N':
        return False
        if exercise.exercise_permission == 'F':
            if user.is_authenticated():
                is_friend = Friendship.objects.are_friends(user, exercise.user)
                if is_friend:
                    return True
                else:
                    return False

            else:
                return False
    return True

@register.inclusion_tag("endless/show_more_table.html", takes_context=True)
def show_more_table(context, label=None, loading=endless_settings.LOADING):
    # this can raise a PaginationError 
    # (you have to call paginate before including the show more template)
    page = utils.get_page_from_context(context)
    # show the template only if there is a next page
    if page.has_next():
        request = context["request"]
        page_number = page.next_page_number()
        # querystring
        querystring_key = context["endless_querystring_key"]
        querystring = utils.get_querystring_for_page(request, page_number,
            querystring_key, default_number=context["endless_default_number"])
        return {
            'path': context["endless_override_path"] or request.path,
            'querystring_key': querystring_key,
            'querystring': querystring,
            'loading': loading,
            'label': label,
            'request': request,
        }
    # no next page, nothing to see
    return {}


@register.filter
def likes_list(obj):
    """
       Changed from phileo's likes_count tag
    """
    return Like.objects.filter(
        receiver_content_type=ContentType.objects.get_for_model(obj),
        receiver_object_id=obj.pk
    )
