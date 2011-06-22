from django import template
from django.utils.safestring import mark_safe
from wakawaka.models import WikiPage, Revision

register = template.Library()

@register.filter
def wiki_help(keyword):
    p = WikiPage.objects.get(slug=keyword)

    if p:
        return mark_safe('<div style="cursor: pointer; background: silver; float: left; padding: 0 4px" onclick="this.nextSibling.style.display = \'block\'">?</div><p style="float: left; display: none">' + p.current.content + '</p>')
    else:
        return ''
