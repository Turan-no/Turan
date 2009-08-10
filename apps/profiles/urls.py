from django.conf.urls.defaults import *
from views import profile, profiles
from forms import UserProfileDetailForm

urlpatterns = patterns('',
    url(r'^username_autocomplete/$', 'autocomplete_app.views.username_autocomplete_friends', name='profile_username_autocomplete'),
    url(r'^$', profiles, name='profile_list'),
    url(r'^(?P<username>[\w\._-]+)/$', profile, name='profile_detail'),
)
urlpatterns += patterns('django.views.generic.create_update',
    url(r'^userprofiledetail/create/$', 'create_object', {'login_required': True, 'form_class': UserProfileDetailForm},name='userprofiledetail_create'),
)
