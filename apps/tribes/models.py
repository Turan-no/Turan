from django.core.urlresolvers import reverse
from django.contrib.auth.models import  User
from django.utils.translation import ugettext_lazy as _
from django.db import models

from groups.base import Group

class Tribe(Group):
    
    members = models.ManyToManyField(User, related_name='tribes', verbose_name=_('members'))
    slogan = models.TextField(blank=True, help_text=_('No pain - no gain'))
    logo = models.ImageField(upload_to='team_logos', blank=True)
    url = models.URLField(blank=True)
    
    def get_absolute_url(self):
        return reverse('tribe_detail', kwargs={'group_slug': self.slug})
    
    def get_url_kwargs(self):
        return {'group_slug': self.slug}

    class Meta:
        verbose_name = _("Team")
        verbose_name_plural = _("Teams")
