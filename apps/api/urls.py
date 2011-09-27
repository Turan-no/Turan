from django.conf.urls.defaults import *
from piston.resource import Resource
from api.handlers import ExerciseHandler
from api.handlers import RouteHandler

from piston.authentication import HttpBasicAuthentication, OAuthAuthentication
from piston.doc import documentation_view

exercise_handler = Resource(ExerciseHandler)
route_handler = Resource(RouteHandler)
auth = OAuthAuthentication(realm="Turan API")

urlpatterns = patterns('',
   url(r'^exercise/(?P<object_id>\d+)/?$', exercise_handler),
   url(r'^exercise/?$', exercise_handler),
   url(r'^route/(?P<object_id>\d+)/?$', route_handler),
   url(r'^route/?$', route_handler),
)
