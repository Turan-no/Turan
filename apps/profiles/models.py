from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from timezones.fields import TimeZoneField

class Profile(models.Model):
    
    user = models.ForeignKey(User, unique=True, verbose_name=_('user'))
    name = models.CharField(_('name'), max_length=50, null=True, blank=True)
    about = models.TextField(_('about'), null=True, blank=True)
    location = models.CharField(_('location'), max_length=40, null=True, blank=True)
    website = models.URLField(_('website'), null=True, blank=True, verify_exists=False)
    
    height = models.IntegerField(blank=True, default=0, help_text=_('in cm'))
    weight = models.FloatField(blank=True, default=0, help_text=_('in kg'))
    resting_hr = models.IntegerField(blank=True, default=0, help_text=_('beats per minute'))
    max_hr = models.IntegerField(blank=True, default=0, help_text=_('beats per minute'))
    motto = models.CharField(max_length=160)

    image = models.ImageField(upload_to='turan', blank=True)
    cycle = models.CharField(max_length=99, blank=True)
    cycle_image = models.ImageField(upload_to='turan', blank=True)

    def __unicode__(self):
        return self.user.username
    
    def get_absolute_url(self):
        return ('profile_detail', None, {'username': self.user.username})
    get_absolute_url = models.permalink(get_absolute_url)
    
    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')
        ordering = ('user__username',)

class UserProfileDetail(models.Model):
    userprofile = models.ForeignKey(Profile)
    time = models.DateTimeField(help_text=_('2009-08-27 08:00:00, time optional'))
    weight = models.FloatField(blank=True, null=True, help_text=_('in kg'))
    resting_hr = models.IntegerField(blank=True,null=True, help_text=_('beats per minute'))

    def save(self, force_insert=False, force_update=False):

        ''' Overriden to update UserProfile with new data '''
        super(UserProfileDetail, self).save(force_insert, force_update)
        if self.weight:
            # TODO: maybe round this off?
            self.userprofile.weight = int(self.weight)
        if self.resting_hr:
            self.userprofile.esting_hr = self.resting_hr
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
