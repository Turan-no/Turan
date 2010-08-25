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



class ExcerciseAdmin(admin.ModelAdmin):
    exclude = ('user',)
    def queryset(self, request):
        qs = super(ExcerciseAdmin,self).queryset(request)
        return qs.filter(user=request.user)
    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

admin.site.register(Route, RouteAdmin)
#admin.site.register(CycleTrip, CycleTripAdmin)
#admin.site.register(Hike, HikeAdmin)
admin.site.register(Exercise, ExcerciseAdmin)
admin.site.register(Location)
#admin.site.register(Team)
#admin.site.register(TeamMembership)
admin.site.register(ExerciseType)
admin.site.register(ExercisePermission)
admin.site.register(MergeSensorFile)
#admin.site.register(Teamsport)

