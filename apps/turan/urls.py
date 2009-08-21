from django.conf import settings
from django.conf.urls.defaults import *
from models import Route, CycleTrip, Hike, OtherExercise
from views import index, trip_compare, logout, events, route_detail, week, statistics, generate_tshirt, calendar, calendar_month, cycletrip, json_tripdetail, TripsFeed, json_serializer, create_object, update_object_user, turan_object_list, autocomplete_route, geojson
from forms import *
from threadedcomments.models import ThreadedComment as Comment

feeds = {
    'trips': TripsFeed,
}
urlpatterns = patterns('',
    url(r'^events/?$', events, name='events'),
    url(r'^events/user/(?P<username>\w+)', events, name='events'),
    url(r'^statistics$', statistics, name='statistics'),
    url(r'^statistics/(?P<year>\d+)$', statistics, name='statistics'),
    url(r'^statistics/(?P<year>\d+)/(?P<month>\d+)$', statistics, name='statistics'),
    url(r'^generate/tshirt', generate_tshirt, name='generate_tshirt'),
    url(r'^(?P<event_type>\w+)/compare/(?P<trip1>\d+)/(?P<trip2>\d+)', trip_compare, name='trip_compare'),
    #url(r'^trip/compare', trip_compare, { 'trip1': None, 'trip2': None }, name='trip_compare_base'),
    url(r'^route/(?P<object_id>\d+)', route_detail, name='route'),
    url(r'^week/(?P<week>\d+)', week, name='week-all'),
    url(r'^week/(?P<week>\d+)/(?P<user_id>)', week, name='week'),

    url(r'^calendar/(?P<year>\d+)/(?P<month>\d+)/(?P<user_id>\d+)', calendar_month, name='calendar-date-user'),
    url(r'^calendar/(?P<year>\d+)/(?P<month>\d+)', calendar_month, name='calendar'),
    url(r'^calendar/user/(?P<user_id>\d+)/$', calendar, name='calendar-user'),
    url(r'^calendar/$', calendar, name='calendar-index'),

    url(r'^json/comment/random/?$', json_serializer, { 'queryset': Comment.objects.order_by('?')[:10], 'relations': ('content_type',) }, name='json_comments'),
    url(r'^json/(?P<event_type>\w+)/(?P<object_id>\d+)/(?P<val>\w+)/(?P<start>\d+)/(?P<stop>\d+)', json_tripdetail, name='json_tripdetail-startstop'),
    url(r'^json/(?P<event_type>\w+)/(?P<object_id>\d+)/(?P<val>\w+)/?$', json_tripdetail, name='json_tripdetail'),
    url(r'^geojson/(?P<event_type>\w+)/(?P<object_id>\d+)/?$', geojson, name='geojson'),

      url(r'^autocomplete/(?P<app_label>\w+)/(?P<model>\w+)/$', autocomplete_route, name='autocomplete_route'),

    url(r'^$', index, name='turanindex'),

# The RSS Feeds
    (r'^feed/(?P<url>.*)/?$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
)

# Lists and details
urlpatterns += patterns('django.views.generic.list_detail',
    url(r'^route/?$', turan_object_list, { 'queryset': Route.objects.select_related().filter(distance__gt=0), }, name='routes'),

    url(r'^trip/?$', turan_object_list, { 'queryset': CycleTrip.objects.select_related() }, name='cycletrips'),
    url(r'^trip/(?P<object_id>\d+)', cycletrip, name='cycletrip'),


    url(r'^hike/?$', turan_object_list, { 'queryset': Hike.objects.select_related() }, name='hikes'),
    url(r'^hike/(?P<object_id>\d+)', 'object_detail', { 'queryset': Hike.objects.select_related(), }, name='hike'),
    url(r'^exercise/?$', turan_object_list, { 'queryset': OtherExercise.objects.select_related() }, name='exercises'),
    url(r'^exercise/(?P<object_id>\d+)', 'object_detail', { 'queryset': OtherExercise.objects.select_related(), }, name='exercise'),
)
urlpatterns += patterns('django.views.generic.simple',
    url(r'^about/', 'direct_to_template', {'template': 'turan/about.html'}, name='turan_about'),
    url(r'^todo/', 'direct_to_template', {'template': 'turan/todo.html'}, name='todo'),
)

urlpatterns += patterns('django.views.generic.create_update',
    url(r'^route/create/$', create_object, {'login_required': True, 'form_class': RouteForm},name='route_create'),
    url(r'^trip/create/$', create_object, {'login_required': True, 'form_class': CycleTripForm, 'user_required':True}, name='trip_create'),
    url(r'^hike/create/$', create_object, {'login_required': True, 'form_class': HikeForm, 'user_required':True}, name='hike_create'),
    url(r'^exercise/create/$', create_object, {'login_required': True, 'form_class': ExerciseForm, 'user_required':True}, name='exercise_create'),

    url(r'^route/update/(?P<object_id>\d+)', 'update_object', {'login_required': True, 'form_class': RouteForm},name='route_update'),
    url(r'^trip/update/(?P<object_id>\d+)', update_object_user, {'login_required': True, 'form_class': FullCycleTripForm},name='trip_update'),
    url(r'^hike/update/(?P<object_id>\d+)', update_object_user, {'login_required': True, 'form_class': FullHikeForm},name='hike_update'),
    url(r'^exercise/update/(?P<object_id>\d+)', update_object_user, {'login_required': True, 'form_class': FullExerciseForm},name='exercise_update'),
)

