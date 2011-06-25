from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db.models import Count
from django.utils.translation import ugettext_lazy as _
from django.utils import simplejson
from django.utils.safestring import mark_safe

from timezones.fields import TimeZoneField

class Profile(models.Model):
    
    user = models.ForeignKey(User, unique=True, verbose_name=_('user'))
    name = models.CharField(_('name'), help_text=_('Optional real name'), max_length=50, null=True, blank=True)
    about = models.TextField(_('about'), null=True, blank=True)
    location = models.CharField(_('location'), max_length=40, null=True, blank=True)
    website = models.URLField(_('website'), null=True, blank=True, verify_exists=False)
    
    height = models.IntegerField(blank=True, default=0, help_text=_('in cm'))
    weight = models.FloatField(blank=True, default=0, help_text=_('in kg'))
    resting_hr = models.IntegerField(blank=True, default=0, help_text=_('beats per minute'))
    ftp = models.IntegerField(blank=True,null=True, help_text=_('Functional Threshold Power'))
    max_hr = models.IntegerField(blank=True, default=0, help_text=_('beats per minute'))
    motto = models.CharField(max_length=160)

    image = models.ImageField(upload_to='turan', blank=True)
    cycle = models.CharField(max_length=99, blank=True)
    cycle_image = models.ImageField(upload_to='turan', blank=True)

    def __unicode__(self):
        return self.get_name()

    def get_name(self):
        if self.name and self.name.strip() != "":
            return self.name
        return self.user.username
    
    def get_absolute_url(self):
        return ('profile_detail', None, {'username': self.user.username})
    get_absolute_url = models.permalink(get_absolute_url)
    
    def get_exercise_types_by_count_json(self):
        return mark_safe(simplejson.dumps(list(self.user.exercise_set.values('exercise_type__id').annotate(c=Count('exercise_type__id')).order_by('-c'))[:3]))

    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')
        ordering = ('user__username',)

    def get_weight(self, date=None):
        ''' Returns weight of user, optionally given date, try to find weight close to date '''
        userweight = self.weight
        if date:
            try:
                userweight = self.userprofiledetail_set.filter(weight__isnull=False).filter(time__lt=date).order_by("-time")[0].weight
            except IndexError:
                # when no weight is found
                pass
        return userweight

    def get_ftp(self, date=None):
        ''' Returns ftp of user, optionally given date, try to find ftp close to date '''
        userftp = self.ftp
        if date:
            try:
                userftp = self.userprofiledetail_set.filter(ftp__isnull=False).filter(time__lt=date).order_by("-time")[0].ftp
            except IndexError:
                # when no ftp is found
                pass
        return userftp

class UserProfileDetail(models.Model):
    userprofile = models.ForeignKey(Profile)
    time = models.DateTimeField(help_text=_('2009-08-27 08:00:00, time optional'))
    weight = models.FloatField(blank=True, null=True, help_text=_('in kg'))
    resting_hr = models.IntegerField(blank=True,null=True, help_text=_('beats per minute'))
    ftp = models.IntegerField(blank=True,null=True, help_text=_('Functional Threshold Power'))

    def save(self, force_insert=False, force_update=False):

        ''' Overriden to update UserProfile with new data '''
        super(UserProfileDetail, self).save(force_insert, force_update)
        if self.weight:
            self.userprofile.weight = self.weight
        if self.resting_hr:
            self.userprofile.resting_hr = self.resting_hr
        if self.ftp:
            self.userprofile.ftp = self.ftp
        self.userprofile.save()

    def __unicode__(self):
        return unicode(self.userprofile.user)

    class Meta:
        verbose_name = _("Profile Detail")
        verbose_name_plural = _("Profile Details")

    def get_absolute_url(self):
        # TODO: maybe have separate views for all the details in the future?
        return self.userprofile.get_absolute_url()

def create_profile(sender, instance=None, **kwargs):
    if instance is None:
        return
    profile, created = Profile.objects.get_or_create(user=instance)

post_save.connect(create_profile, sender=User)
