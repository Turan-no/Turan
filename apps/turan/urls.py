from django.conf import settings
from django.conf.urls.defaults import *
from models import Route, CycleTrip, Hike, OtherExercise
from views import index, upload_eventdetails, trip_compare, logout, events, route_detail, week, statistics, generate_tshirt, route_new, calendar, cycletrip, json_tripdetail

urlpatterns = patterns('',
#    url(r'^profile/(?P<object_id>\d+)', profile, name='profile'),
    url(r'^events', events, name='events'),
    url(r'^statistics', statistics, name='statistics'),
    url(r'^generate/tshirt', generate_tshirt, name='generate_tshirt'),
    url(r'^trip/compare/(?P<trip1>\d+)/(?P<trip2>\d+)', trip_compare, name='trip_compare'),
    url(r'^route/(?P<object_id>\d+)', route_detail, name='route'),
    #url(r'^route/svg/(?P<route_id>\d+)', generate_svg, name='generate_svg'),
    url(r'^route/new/', route_new, name='route_new'),
    url(r'^week/(?P<week>\d+)', week, name='week-all'),
    url(r'^week/(?P<week>\d+)/(?P<user_id>)', week, name='week'),

    url(r'^calendar/(?P<year>\d+)/(?P<month>\d+)/(?P<user_id>\d+)', calendar, name='calendar-date-user'),
    url(r'^calendar/user/(?P<user_id>\d+)/$', calendar, name='calendar-user'),
    url(r'^calendar/(?P<year>\d+)/(?P<month>\d+)', calendar, name='calendar'),
    url(r'^calendar/', calendar, name='calendar-index'),

    url(r'json/(?P<event_type>\w+)/(?P<object_id>\d+)/(?P<val>\w+)/(?P<start>\d+)/(?P<stop>\d+)', json_tripdetail, name='json_tripdetail-startstop'),
    url(r'json/(?P<event_type>\w+)/(?P<object_id>\d+)/(?P<val>\w+)/?$', json_tripdetail, name='json_tripdetail'),

    url(r'^$', index, name='turanindex'),
)
urlpatterns += patterns('django.views.generic.list_detail',
    url(r'^route/?$', 'object_list', { 'queryset': Route.objects.select_related().order_by('name'), }, name='routes'),

    url(r'^trip/?$', 'object_list', { 'queryset': CycleTrip.objects.select_related().order_by('-date'), }, name='cycletrips'),
    #    url(r'^trip/(?P<object_id>\d+)', 'object_detail', { 'queryset': CycleTrip.objects.select_related(), }, name='cycletrip'),
    url(r'^trip/(?P<object_id>\d+)', cycletrip, name='cycletrip'),

#    url(r'^profile/?$', 'object_list', { 'queryset': UserProfile.objects.select_related(), }, name='profiles'),

    url(r'^hike/?$', 'object_list', { 'queryset': Hike.objects.select_related().order_by('-date'), }, name='hikes'),
    url(r'^hike/(?P<object_id>\d+)', 'object_detail', { 'queryset': Hike.objects.select_related(), }, name='hike'),
    url(r'^exercise/?$', 'object_list', { 'queryset': OtherExercise.objects.select_related().order_by('-date'), }, name='exercies'),
    url(r'^exercise/(?P<object_id>\d+)', 'object_detail', { 'queryset': OtherExercise.objects.select_related(), }, name='exercise'),
    url(r'^upload/eventdetails/(?P<object_id>\d+)/(?P<event_type>\w+)/', upload_eventdetails, name='upload_eventdetails'),

#    url(r'^team/?$', 'object_list', { 'queryset': Team.objects.select_related(), }, name='teams'),
#    url(r'^team/(?P<object_id>\d+)', 'object_detail', { 'queryset': Team.objects.select_related(), }, name='team'),


)
urlpatterns += patterns('django.views.generic.simple',
#    (r'^map/', 'direct_to_template', {'template': 'turan/routeview.html'}),
    url(r'^about/', 'direct_to_template', {'template': 'turan/about.html'}, name='turan_about'),
    url(r'^todo/', 'direct_to_template', {'template': 'turan/todo.html'}, name='todo'),
)
