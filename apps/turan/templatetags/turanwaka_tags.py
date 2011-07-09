from django import template
from django.utils.safestring import mark_safe
from wakawaka.models import WikiPage, Revision
from django.conf import settings

register = template.Library()

@register.filter
def wiki_help(keyword):
    p = WikiPage.objects.get(slug=keyword)

    if p:
        # Who needs a template system
        html = '<div class="tooltip_help" onmouseover="this.childNodes[1].style.display = \'block\'" onmouseout="this.childNodes[1].style.display = \'none\'"><img src="' + settings.MEDIA_URL + 'pinax/img/silk/icons/help.png" /><p class="tooltip_help_box" onclick="event.stopPropagation(); this.style.display = \'none\'">' + p.current.content + '</p></div>'
        return mark_safe(html)
    else:
        return ''
