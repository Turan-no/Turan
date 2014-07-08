from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from tagging.models import Tag, TaggedItem
from photos.models import Image
from bookmarks.models import BookmarkInstance
from turan.models import Route, Exercise

from wiki.models import Article as WikiArticle


def tags(request, tag, template_name='tags/index.html'):
    tag = get_object_or_404(Tag, name=tag)
    
    phototags = TaggedItem.objects.get_by_model(Image, tag)
    bookmarktags = TaggedItem.objects.get_by_model(BookmarkInstance, tag)
    
    wiki_article_tags = TaggedItem.objects.get_by_model(WikiArticle, tag)

    route_tags = TaggedItem.objects.get_by_model(Route, tag)

    exercise_tags = TaggedItem.objects.get_by_model(Exercise, tag)
    
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))
