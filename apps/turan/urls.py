from django.conf import settings
from django.conf.urls.defaults import *
from models import Route, Exercise
from views import *
from forms import *
from feeds import *
from threadedcomments.models import ThreadedComment as Comment
from django.contrib.sitemaps import GenericSitemap
from djcelery import views as celery_views


sitemaps = {
        'trips': GenericSitemap({'queryset': Exercise.objects.all(), 'date_field': 'date'}, priority=0.5),
    'routes': GenericSitemap({'queryset': Route.objects.all(), 'date_field': 'created'}, priority=0.5),
}

feeds = {
    'trips': TripsFeed,
}
urlpatterns = patterns('',
    url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.index', {'sitemaps': sitemaps}),
    url(r'^sitemap-(?P<section>.+)\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    url(r'^events/?$', events, name='events'),
    url(r'^events/nearby/(?P<latitude>[\d.]+)/(?P<longitude>[\d.]+)/?$', events, name='events'),
    url(r'^events/user/(?P<username>\w+)', events, name='events'),
    url(r'^statistics/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)', statistics, name='statistics-day'),
    url(r'^statistics/(?P<year>\d+)/(?P<month>\d+)', statistics, name='statistics-month'),
    url(r'^statistics/(?P<year>\d+)', statistics, name='statistics-year'),
    url(r'^statistics/week/(?P<year>\d+)/(?P<week>\d+)', statistics, name='statistics-week'),
    url(r'^statistics/?', statistics, name='statistics'),
    url(r'^bestest/?', bestest, name='bestest'),
    url(r'^generate/tshirt', generate_tshirt, name='generate_tshirt'),
    url(r'^route/(?P<object_id>\d+)', route_detail, name='route'),
    url(r'^segment/(?P<object_id>\d+)', segment_detail, name='segment'),
    url(r'^week/(?P<week>\d+)', week, name='week-all'),
    url(r'^week/(?P<week>\d+)/(?P<user_id>)', week, name='week'),
    url(r'^import/$', 'turan.views.import_data', name='import_data'),

    url(r'^calendar/(?P<year>\d+)/(?P<month>\d+)', calendar_month, name='calendar'),
    url(r'^calendar/$', calendar, name='calendar-index'),

    url(r'^exercise/compare/(?P<exercise1>\d+)/(?P<exercise2>\d+)', exercise_compare, name='exercise_compare'),
    url(r'^json/comment/random/?$', json_serializer, { 'queryset': Comment.objects.order_by('?')[:10], 'relations': ('content_type',) }, name='json_comments'),
#    url(r'^json/(?P<event_type>\w+)/(?P<object_id>\d+)/(?P<val>\w+)/(?P<start>\d+)/(?P<stop>\d+)', json_tripdetail, name='json_tripdetail-startstop'),
#    url(r'^json/(?P<event_type>\w+)/(?P<object_id>\d+)/(?P<val>\w+)/?$', json_tripdetail, name='json_tripdetail'),
    url(r'^json/graph/(?P<object_id>\d+)', json_trip_series, name='json_trip_series'),
    url(r'^json/geo/(?P<object_id>\d+)', geojson, name='geojson'),
    url(r'^json/power/(?P<object_id>\d+)', powerjson, name='powerjson'),
    url(r'^json/wiki/(?P<slug>\w+)/?$', wikijson, name='wikijson'),
    url(r'^json/wiki/(?P<slug>\w+)/(?P<rev_id>\d+)/?', wikijson, name='wikijson'),


# celery
    url(r'^json/(?P<task_id>[\w\d\-]+)/done/?$', celery_views.is_task_successful,
                    name="celery-is_task_successful"),
    url(r'^json/(?P<task_id>[\w\d\-]+)/status/?$', celery_views.task_status,
                    name="celery-task_status"),
    url(r'^json/tasks/?$', celery_views.registered_tasks, name='celery-tasks'),

      url(r'^autocomplete/(?P<app_label>\w+)/(?P<model>\w+)/$', autocomplete_route, name='autocomplete_route'),

    url(r'^/?$', index, name='turanindex'),

# The Feeds
    (r'^feed/(?P<url>.*)/?$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
    url(r'^feeds/ical/(?P<username>\w+)/?$', ical, name='ical'),
)

# Lists and details
urlpatterns += patterns('django.views.generic.list_detail',
    url(r'^route/?$', turan_object_list, { 'queryset': Route.objects.select_related().filter(distance__gt=0).extra( select={ 'tcount': 'SELECT COUNT(*) FROM turan_exercise WHERE turan_exercise.route_id = turan_route.id' }) }, name='routes'),
    url(r'^slope/?$', slopes, { 'queryset': Slope.objects.select_related()}, name='slopes'),
    url(r'^segment/?$', segments, { 'queryset': Segment.objects.select_related().extra( select= {'tcount': 'SELECT COUNT(*) FROM turan_segmentdetail WHERE turan_segmentdetail.segment_id = turan_segment.id' }) }, name='segments'),

    url(r'^exercise/?$', turan_object_list, { 'queryset': Exercise.objects.select_related().order_by('-date') }, name='exercises'),
    url(r'^exercise/(?P<object_id>\d+)', exercise, name='exercise'),
    url(r'^exercise/parse/(?P<object_id>\d+)/(?P<task_id>.*)/?$', exercise_parse_progress, name='exercise_parse_progress'),
    url(r'^exercise/parse/(?P<object_id>\d+)/?$', exercise_parse, name='exercise_parse'),
)
urlpatterns += patterns('django.views.generic.simple',
    url(r'^about/', 'direct_to_template', {'template': 'turan/about.html'}, name='turan_about'),
    url(r'^todo/', 'direct_to_template', {'template': 'turan/todo.html'}, name='todo'),
)

urlpatterns += patterns('django.views.generic.create_update',
    url(r'^route/create/$', create_object, {'login_required': True, 'form_class': RouteForm},name='route_create'),
    url(r'^exercise/create/$', create_object, {'login_required': True, 'form_class': ExerciseForm, 'user_required':True}, name='exercise_create'),
    url(r'^exercise/r/create/$', create_exercise_with_route,  name='exercise_route_create'),
    url(r'^segment/create/$', create_object, {'login_required': True, 'form_class': SegmentForm},name='segment_create'),
    url(r'^segmentdetail/create/', create_object, {'login_required': True, 'form_class': SegmentDetailForm},name='segmentdetail_create'),


    url(r'^route/update/(?P<object_id>\d+)', 'update_object', {'login_required': True, 'form_class': FullRouteForm},name='route_update'),
    url(r'^slope/update/(?P<object_id>\d+)', 'update_object', {'login_required': True, 'form_class': FullSlopeForm},name='slope_update'),
    url(r'^segment/update/(?P<object_id>\d+)', 'update_object', {'login_required': True, 'form_class': FullSegmentForm},name='segment_update'),
    url(r'^exercise/update/(?P<object_id>\d+)', update_object_user, {'login_required': True, 'form_class': FullExerciseForm},name='exercise_update'),
    url(r'^segmentdetail/update/(?P<object_id>\d+)/?$', 'update_object', {'login_required': True, 'form_class': SegmentDetailForm},name='segmentdetail_update'),

    url(r'^exercise/delete/(?P<object_id>\d+)', turan_delete_object, {'model': Exercise, 'login_required': True,},name='exercise_delete'),
    url(r'^segmentdetail/delete/(?P<object_id>\d+)', turan_delete_object, {'model': SegmentDetail, 'login_required': True,},name='segmentdetail_delete'),

# Detail deletes
#    url(r'^exercise/detail_delete/(?P<object_id>\d+)/(?P<value>\w+)/', turan_delete_detailset_value, {'model': Exercise, },name='exercise_detail_delete'),
)



