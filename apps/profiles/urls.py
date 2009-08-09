from django.conf.urls.defaults import *
from views import profile, profiles

urlpatterns = patterns('',
    url(r'^username_autocomplete/$', 'autocomplete_app.views.username_autocomplete_friends', name='profile_username_autocomplete'),
    url(r'^$', profiles, name='profile_list'),
    url(r'^(?P<username>[\w\._-]+)/$', profile, name='profile_detail'),
)
