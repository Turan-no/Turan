from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from models import *



#class CycleTripInline(admin.StackedInline):
#    model = CycleTripDetail

class RouteAdmin(admin.ModelAdmin):
    list_display = ('name', 'distance', 'description', 'route_url', 'gpx_file', 'ascent', 'descent')
    search_fields = ('name', 'description', 'route_url',)
    list_filter = ('gpx_file',)
#
#    inlines = [
#        CycleTripInline,
#    ]


class HikeAdmin(admin.ModelAdmin):
    exclude = ('user',)
    def queryset(self, request):
        qs = super(HikeAdmin,self).queryset(request)
        return qs.filter(user=request.user)
    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

class CycleTripAdmin(admin.ModelAdmin):
    list_display = ('route', 'date', 'time', 'avg_speed', 'avg_cadence', 'avg_hr', 'max_speed', 'max_cadence', 'max_hr', 'kcal')
    list_editable = ('avg_speed', 'avg_cadence', 'avg_hr', 'max_speed', 'max_cadence', 'max_hr', 'kcal')
    date_hierarchy = 'date'
    exclude = ('user',)
    fieldsets = (
        (None, {
            'fields': ('route', 'date', 'time', 'comment', 'sensor_file', 'kcal', 'url'),
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('avg_speed', 'avg_cadence', 'avg_hr', 'max_speed', 'max_cadence', 'max_hr')
        }),
    )


    def queryset(self, request):
        qs = super(CycleTripAdmin,self).queryset(request)
        return qs.filter(user=request.user)

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()


#    def formfield_for_foreignkey(self, db_field, request, **kwargs):
#        if db_field.name == "user_id":
#            kwargs["queryset"] = User.objects.filter(user=request.user)
#            return db_field.formfield(**kwargs)
#        return super(CycleTripAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class OtherExcerciseAdmin(admin.ModelAdmin):
    exclude = ('user',)
    def queryset(self, request):
        qs = super(OtherExcerciseAdmin,self).queryset(request)
        return qs.filter(user=request.user)
    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

admin.site.register(Route, RouteAdmin)
admin.site.register(CycleTrip, CycleTripAdmin)
admin.site.register(Hike, HikeAdmin)
admin.site.register(OtherExercise, OtherExcerciseAdmin)
admin.site.register(Location)
admin.site.register(Team)
admin.site.register(TeamMembership)
admin.site.register(ExerciseType)
#admin.site.register(Teamsport)

