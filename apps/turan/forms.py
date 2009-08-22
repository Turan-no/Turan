from django import forms
from models import Route, CycleTrip, Hike, OtherExercise
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.text import truncate_words
from django.core.urlresolvers import reverse
from views import autocomplete_route

class ForeignKeySearchInput(forms.HiddenInput):
    """
    A Widget for displaying ForeignKeys in an autocomplete search input 
    instead in a <select> box.
    """
    class Media:
        css = {
            'all': ('django_extensions/css/jquery.autocomplete.css',)
        }
        js = (
            'jquery.bgiframe.js',
            'jquery.ajaxQueue.js',
            'jquery.autocomplete.js'
        )

    def label_for_value(self, value):
        obj = Route.objects.get(pk=value)
        return truncate_words(obj, 14)

    def __init__(self, rel, attrs=None):
        self.rel = rel
        super(ForeignKeySearchInput, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        if attrs is None:
            attrs = {}
        rendered = super(ForeignKeySearchInput, self).render(name, value, attrs)
        if value:
            label = self.label_for_value(value)
        else:
            label = u''
        return rendered + mark_safe(u'''
<tr><th><label>Route:</label></th><td>
            <style type="text/css" media="screen">
                #lookup_%(name)s {
                    padding-right:16px;
                    background: url(
                        %(admin_media_prefix)simg/admin/selector-search.gif
                    ) no-repeat right;
                }
                #del_%(name)s {
                    display: none;
                }
            </style>
<input type="text" id="lookup_%(name)s" value="%(label)s" />
            <script type="text/javascript">
            jQuery("#lookup_%(name)s").autocomplete('%(url)s', {
                max: 10,
                highlight: false,
                multiple: true,
                multipleSeparator: "\\n",
                scroll: true,
                scrollHeight: 300,
                matchContains: true,
                autoFill: true,
            }).result(function(event, data, formatted) {
                if (data) {
                    $('#id_%(name)s').val(data[1]);
                }
            });
            </script>
</td></tr>
        ''') % {
            'name': name,
            'label': label,
            'admin_media_prefix': settings.ADMIN_MEDIA_PREFIX,
            'url': reverse(autocomplete_route, args=('a','b')),
        }

class EventForm(forms.ModelForm):
    route = forms.CharField(widget=ForeignKeySearchInput('Route'))#, 'turan'))


    class Meta:
        model = CycleTrip
        fields = ('route', 'date', 'time', 'comment', 'tags', 'sensor_file', 'kcal', 'url')

    def clean_route(self):
        '''Translate number from autocomplete to object '''
        data = self.cleaned_data['route']
        data = Route.objects.get(pk=data)
        return data
    
class CycleTripForm(EventForm):
    pass

class HikeForm(EventForm):
    class Meta(EventForm.Meta):
        model = Hike

class ExerciseForm(EventForm):
    class Meta(EventForm.Meta):
        model = OtherExercise
        fields = ('route', 'date', 'time', 'exercise_type', 'comment', 'sensor_file', 'kcal', 'url')

class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        exclude = ('single_serving', 'start_lat', 'start_lon', 'end_lat', 'end_lon')

class FullCycleTripForm(forms.ModelForm):
    class Meta:
        model = CycleTrip
        exclude = ('user', 'content_type', 'object_id')

class FullHikeForm(forms.ModelForm):
    class Meta:
        model = Hike
        exclude = ('user', 'content_type', 'object_id')


class FullExerciseForm(forms.ModelForm):
    class Meta:
        model = OtherExercise
        exclude = ('user', 'content_type', 'object_id')


