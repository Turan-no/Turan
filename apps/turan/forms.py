from django import forms
from models import Route, Exercise, Segment, Slope, SegmentDetail
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.text import truncate_words
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _



class ExerciseForm(forms.ModelForm):
    route = forms.CharField(widget=forms.HiddenInput(),required=False)

    class Meta:
        model = Exercise
        fields = ['route', 'sensor_file', 'exercise_type', 'comment', 'tags', 'kcal','exercise_permission', 'url']

    def clean_route(self):
        '''Translate number from autocomplete to object.
           If not number, just create a new route with the text given as name
         '''

        data = self.cleaned_data['route']
        try:
            data = Route.objects.get(pk=data)
        except ValueError: # not int, means name
            if data: # Check that string i set, if not, leave it to exercise.save() to create autoroute
                r = Route()
                r.name = data
                r.single_serving = True
                r.save()
                data = r
            else:
                return None
        return data


class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        exclude = ('single_serving', 'start_lat', 'start_lon', 'end_lat', 'end_lon')

class FullRouteForm(forms.ModelForm):
    class Meta:
        model = Route

class FullExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        exclude = ('user', 'content_type', 'object_id')

class SegmentForm(forms.ModelForm):
    class Meta:
        model = Segment
        fields =('name', 'description')

class FullSegmentForm(forms.ModelForm):
    class Meta:
        model = Segment

class SegmentDetailForm(forms.ModelForm):
    class Meta:
        model = SegmentDetail

class FullSlopeForm(forms.ModelForm):
    class Meta:
        model = Slope
