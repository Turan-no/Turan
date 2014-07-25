from django.contrib import admin
from apps.profiles.models import Profile, UserProfileDetail

class ProfileAdmin(admin.ModelAdmin):
    exclude = ('user',)
    def queryset(self, request):
        qs = super(ProfileAdmin,self).queryset(request)
        return qs.filter(user=request.user)

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

class UserProfileDetailAdmin(admin.ModelAdmin):
    list_display = ('userprofile', 'time', 'weight', 'resting_hr')
    search_fields = ('userprofile',)
    list_filter = ('userprofile',)

    def queryset(self, request):
        qs = super(UserProfileDetailAdmin,self).queryset(request)
        return qs.filter(userprofile__user=request.user)

    def get_form(self, request, obj=None):
        self.request = request
        f = super(UserProfileDetailAdmin,self).get_form(request, obj)
        return f

    def formfield_for_dbfield(self, dbfield, **kwargs):
        if dbfield.name == 'userprofile':
          kwargs['queryset'] = Profile.objects.filter(user=self.request.user)
        return super(UserProfileDetailAdmin, self).formfield_for_dbfield(dbfield, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()
admin.site.register(Profile)#, ProfileAdmin)
admin.site.register(UserProfileDetail, UserProfileDetailAdmin)
