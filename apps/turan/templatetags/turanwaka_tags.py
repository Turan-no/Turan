from django import template
from django.utils.safestring import mark_safe
from wakawaka.models import WikiPage, Revision
from django.template.defaultfilters import linebreaksbr
from django.conf import settings

register = template.Library()

@register.filter
def wiki_help(keyword):
    p = WikiPage.objects.get(slug=keyword)

    if p:
        content = p.current.content
        # Linebreaks
        content = linebreaksbr(content)
        # Who needs a template system
        html = '<div class="tooltip_help" onmouseover="this.childNodes[1].style.display = \'block\'" onmouseout="this.childNodes[1].style.display = \'none\'"><img src="' + settings.MEDIA_URL + 'pinax/img/silk/icons/help.png" /><p class="tooltip_help_box" onclick="event.stopPropagation(); this.style.display = \'none\'">' + content + '</p></div>'
        return mark_safe(html)
    return ''

@register.filter
def wiki_content(keyword):
    p = WikiPage.objects.get(slug=keyword)

    if p:
        content = p.current.content
        # Linebreaks
        content = linebreaksbr(content)
        return mark_safe(content)
    return ''
