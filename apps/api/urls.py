from django.conf.urls.defaults import *
from piston.resource import Resource
from api.handlers import ExerciseHandler

from piston.authentication import HttpBasicAuthentication, OAuthAuthentication
from piston.doc import documentation_view

exercise_handler = Resource(ExerciseHandler)
auth = OAuthAuthentication(realm="Turan API")

urlpatterns = patterns('',
   url(r'^exercise/(?P<object_id>\d+)/?$', exercise_handler),
   url(r'^exercise/?$', exercise_handler),
)
