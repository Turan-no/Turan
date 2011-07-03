from django import forms
from models import Route, Exercise, Segment, Slope, SegmentDetail, ExerciseType, permission_choices, Equipment
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.text import truncate_words
from django.core.urlresolvers import reverse
#from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import StrAndUnicode, force_unicode
from django.utils.html import escape, conditional_escape
from cStringIO import StringIO
import zipfile


class ImageSelect(forms.Select):

    def render_option(self, selected_choices, option_value, option_label):
        option_value = force_unicode(option_value)
        et = ExerciseType.objects.get(pk=option_value)
        selected_html = (option_value in selected_choices) and u' selected="selected"' or ''
        return u'<option title="%s" value="%s"%s>%s</option>' % (
            et.icon(),
            escape(option_value), selected_html,
            conditional_escape(force_unicode(option_label)))

class HorizRadioRenderer(forms.RadioSelect.renderer):
    """ this overrides widget method to put radio buttons horizontally
        instead of vertically.
    """
    def render(self):
        """Outputs radios"""
        return mark_safe(u'<div class="inlineLabels"' + u'\n'.join([u'%s\n' % w for w in self]) + u'</div>')



class ExerciseForm(forms.ModelForm):
    route = forms.CharField(widget=forms.HiddenInput(),required=False)
#    exercise_type = forms.ModelChoiceField(widget=ImageSelect())
#    exercise_type = forms.ChoiceField(label=_("Exercise Type"), choices=(),
#                                                    widget=forms.Select(attrs={'class':'selector'}))
    def __init__(self, *args, **kwargs):
        super(ExerciseForm, self).__init__(*args, **kwargs)
        #qs = Equipment.objects.filter(user=self.instance.user)
        #assert False, self.fields['equipment'].queryset

        #if qs.count():
        #    self.fields['equipment'].initial = qs[0].pk

    class Meta:
        model = Exercise
        fields = ['route', 'sensor_file', 'exercise_type', 'equipment', 'comment', 'tags', 'url', 'kcal','exercise_permission' ]
        widgets = {
                'exercise_type': ImageSelect(),
                'exercise_permission': forms.RadioSelect(renderer=HorizRadioRenderer)#,choices=permission_choices,label=_('Visible control'),max_length=1, default='A',help_text='Test')
                }

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

    def __init__(self, *args, **kwargs):
        super(FullExerciseForm, self).__init__(*args, **kwargs)
        qs = Equipment.objects.filter(user = self.instance.user)
        self.fields['equipment'].queryset = qs


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
        widgets = { 
                'exercise': forms.HiddenInput(),
            }

        #fields = ('segment', 'comment' )
#   TODO Need two forms

class FullSlopeForm(forms.ModelForm):
    class Meta:
        model = Slope

class FullEquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        exclude = ('user',)

class ImportForm(forms.Form):
    import_url = forms.CharField(label='Url to external exercise', required=True)

def clean_zipfile(zip_file, wat):
    if not zip_file.name.endswith('.zip'):
        msg = _('File upload must be a valid ZIP archive.')
        raise forms.ValidationError( msg )
    else:
        try:
            zip = zipfile.ZipFile( zip_file)
        except:
            raise forms.ValidationError( _("Could not unzip file." ))
        bad_file = zip.testzip()
        zip.close()
        del zip
        if bad_file:
            raise forms.ValidationError( msg )
    return zip_file # Return the clean zip_file

class BulkImportForm(forms.Form):

    zip_file = forms.FileField(label=_('ZIP file containing multiple exercise files'))


    # The line below hooks the function above into the base form.
    # When the form calls full_clean() it will automatically clean the 
    # zip_file field and add it to the form's clean_data dictionary.
    zip_file.clean = clean_zipfile

