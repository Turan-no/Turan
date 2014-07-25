from django.conf.urls import patterns, url, include
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


from django.contrib import admin
admin.autodiscover()

#if settings.ACCOUNT_OPEN_SIGNUP:
signup_view = "account.views.signup"
#else:
#    signup_view = "signup_codes.views.signup"


urlpatterns = patterns('',
    url(r'^admin/invite_user/$', 'signup_codes.views.admin_invite_user', name="admin_invite_user"),
    url(r'^account/signup/$', signup_view, name="acct_signup"),
    
    (r'^turan/', include('apps.turan.urls')),
    (r'^api/', include('api.urls')),
    (r'^about/', include('about.urls')),
    (r'^account/', include('account.urls')),
    # (r'^openid/(.*)', PinaxConsumer()), # TODO: Need to replace with something that exists
    (r'^bbauth/', include('bbauth.urls')),
    (r'^authsub/', include('authsub.urls')),
    (r'^profiles/', include('profiles.urls')),
    (r'^tags/', include('tag_app.urls')),
    (r'^invitations/', include('friends_app.urls')),
    (r'^notices/', include('notification.urls')),
    (r'^messages/', include('messages.urls')),
    (r'^announcements/', include('announcements.urls')),
    (r'^tribes/', include('pinax.apps.tribes.urls')),
    (r'^comments/', include('threadedcomments.urls')),
    (r'^robots.txt$', include('robots.urls')),
    (r'^i18n/', include('django.conf.urls.i18n')),
    #(r'^admin/(.*)', admin.site.root),
    (r'^admin/', include(admin.site.urls)),

    (r'^photos/', include('photos.urls')),
    (r'^avatar/', include('avatar.urls')),
    (r'^wiki/', include('wakawaka.urls.authenticated')),
    
    (r'', include('apps.turan.urls')),

    (r'', include('social_auth.urls')),
)
urlpatterns += patterns(
    'piston.authentication',
    url(r'^oauth/request_token/$','oauth_request_token'),
    url(r'^oauth/authorize/$','oauth_user_auth'),
    url(r'^oauth/access_token/$','oauth_access_token'),
)

if 'sentry' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        (r'^sentry/', include('sentry.urls')),
    )

handler500 = 'turan.views.internal_server_error'
## @@@ for now, we'll use friends_app to glue this stuff together

from photos.models import Image

friends_photos_kwargs = {
    "template_name": "photos/friends_photos.html",
    "friends_objects_function": lambda users: Image.objects.filter(member__in=users),
}

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
    url(r'^rosetta/', include('rosetta.urls')),
)



urlpatterns += patterns('',
    url('^photos/friends_photos/$', 'friends_app.views.friends_objects', kwargs=friends_photos_kwargs, name="friends_photos"),
)


urlpatterns += patterns('',
    url(r"^likes/", include("phileo.urls")),
)


if settings.DEBUG:
    urlpatterns += patterns('', 
            url(r'^site_media/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT }),
)
urlpatterns += staticfiles_urlpatterns()

