
from south.db import db
from django.db import models
from lortal.turan.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'CycleTripDetail'
        db.create_table('turan_cycletripdetail', (
            ('hr', orm['turan.CycleTripDetail:hr']),
            ('altitude', orm['turan.CycleTripDetail:altitude']),
            ('lon', orm['turan.CycleTripDetail:lon']),
            ('trip', orm['turan.CycleTripDetail:trip']),
            ('time', orm['turan.CycleTripDetail:time']),
            ('lat', orm['turan.CycleTripDetail:lat']),
            ('speed', orm['turan.CycleTripDetail:speed']),
            ('id', orm['turan.CycleTripDetail:id']),
            ('cadence', orm['turan.CycleTripDetail:cadence']),
        ))
        db.send_create_signal('turan', ['CycleTripDetail'])
        
        # Adding model 'CycleTrip'
        db.create_table('turan_cycletrip', (
            ('comment', orm['turan.CycleTrip:comment']),
            ('max_cadence', orm['turan.CycleTrip:max_cadence']),
            ('url', orm['turan.CycleTrip:url']),
            ('route', orm['turan.CycleTrip:route']),
            ('avg_cadence', orm['turan.CycleTrip:avg_cadence']),
            ('date', orm['turan.CycleTrip:date']),
            ('avg_hr', orm['turan.CycleTrip:avg_hr']),
            ('user', orm['turan.CycleTrip:user']),
            ('max_speed', orm['turan.CycleTrip:max_speed']),
            ('time', orm['turan.CycleTrip:time']),
            ('duration', orm['turan.CycleTrip:duration']),
            ('avg_speed', orm['turan.CycleTrip:avg_speed']),
            ('id', orm['turan.CycleTrip:id']),
            ('max_hr', orm['turan.CycleTrip:max_hr']),
        ))
        db.send_create_signal('turan', ['CycleTrip'])
        
        # Adding model 'Teamsport'
        db.create_table('turan_teamsport', (
            ('comment', orm['turan.Teamsport:comment']),
            ('url', orm['turan.Teamsport:url']),
            ('route', orm['turan.Teamsport:route']),
            ('date', orm['turan.Teamsport:date']),
            ('user', orm['turan.Teamsport:user']),
            ('time', orm['turan.Teamsport:time']),
            ('duration', orm['turan.Teamsport:duration']),
            ('id', orm['turan.Teamsport:id']),
        ))
        db.send_create_signal('turan', ['Teamsport'])
        
        # Adding model 'Location'
        db.create_table('turan_location', (
            ('town', orm['turan.Location:town']),
            ('url', orm['turan.Location:url']),
            ('country', orm['turan.Location:country']),
            ('lon', orm['turan.Location:lon']),
            ('county', orm['turan.Location:county']),
            ('state', orm['turan.Location:state']),
            ('lat', orm['turan.Location:lat']),
            ('id', orm['turan.Location:id']),
        ))
        db.send_create_signal('turan', ['Location'])
        
        # Adding model 'Route'
        db.create_table('turan_route', (
            ('distance', orm['turan.Route:distance']),
            ('description', orm['turan.Route:description']),
            ('descent', orm['turan.Route:descent']),
            ('gpx_file', orm['turan.Route:gpx_file']),
            ('route_url', orm['turan.Route:route_url']),
            ('ascent', orm['turan.Route:ascent']),
            ('id', orm['turan.Route:id']),
            ('name', orm['turan.Route:name']),
        ))
        db.send_create_signal('turan', ['Route'])
        
        # Adding model 'UserProfile'
        db.create_table('turan_userprofile', (
            ('info', orm['turan.UserProfile:info']),
            ('weight', orm['turan.UserProfile:weight']),
            ('image', orm['turan.UserProfile:image']),
            ('height', orm['turan.UserProfile:height']),
            ('cycle_image', orm['turan.UserProfile:cycle_image']),
            ('resting_hr', orm['turan.UserProfile:resting_hr']),
            ('cycle', orm['turan.UserProfile:cycle']),
            ('id', orm['turan.UserProfile:id']),
            ('user', orm['turan.UserProfile:user']),
        ))
        db.send_create_signal('turan', ['UserProfile'])
        
        # Adding model 'UserProfileDetail'
        db.create_table('turan_userprofiledetail', (
            ('resting_hr', orm['turan.UserProfileDetail:resting_hr']),
            ('time', orm['turan.UserProfileDetail:time']),
            ('id', orm['turan.UserProfileDetail:id']),
            ('weight', orm['turan.UserProfileDetail:weight']),
            ('userprofile', orm['turan.UserProfileDetail:userprofile']),
        ))
        db.send_create_signal('turan', ['UserProfileDetail'])
        
        # Adding model 'Hike'
        db.create_table('turan_hike', (
            ('comment', orm['turan.Hike:comment']),
            ('url', orm['turan.Hike:url']),
            ('route', orm['turan.Hike:route']),
            ('date', orm['turan.Hike:date']),
            ('avg_hr', orm['turan.Hike:avg_hr']),
            ('user', orm['turan.Hike:user']),
            ('max_speed', orm['turan.Hike:max_speed']),
            ('time', orm['turan.Hike:time']),
            ('duration', orm['turan.Hike:duration']),
            ('avg_speed', orm['turan.Hike:avg_speed']),
            ('id', orm['turan.Hike:id']),
            ('max_hr', orm['turan.Hike:max_hr']),
        ))
        db.send_create_signal('turan', ['Hike'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'CycleTripDetail'
        db.delete_table('turan_cycletripdetail')
        
        # Deleting model 'CycleTrip'
        db.delete_table('turan_cycletrip')
        
        # Deleting model 'Teamsport'
        db.delete_table('turan_teamsport')
        
        # Deleting model 'Location'
        db.delete_table('turan_location')
        
        # Deleting model 'Route'
        db.delete_table('turan_route')
        
        # Deleting model 'UserProfile'
        db.delete_table('turan_userprofile')
        
        # Deleting model 'UserProfileDetail'
        db.delete_table('turan_userprofiledetail')
        
        # Deleting model 'Hike'
        db.delete_table('turan_hike')
        
    
    
    models = {
        'turan.cycletripdetail': {
            'altitude': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'cadence': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'hr': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'lon': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'speed': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {}),
            'trip': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['turan.CycleTrip']"})
        },
        'auth.user': {
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2009, 7, 18, 0, 18, 38, 520349)'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2009, 7, 18, 0, 18, 38, 520250)'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'turan.location': {
            'country': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'county': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'lon': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'town': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128', 'blank': 'True'})
        },
        'turan.teamsport': {
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'duration': ('DurationField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'route': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['turan.Route']"}),
            'time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'turan.cycletrip': {
            'avg_cadence': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'avg_hr': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'avg_speed': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'duration': ('DurationField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_cadence': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'max_hr': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'max_speed': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'route': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['turan.Route']"}),
            'time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'turan.userprofile': {
            'cycle': ('django.db.models.fields.CharField', [], {'max_length': '99', 'blank': 'True'}),
            'cycle_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'height': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'resting_hr': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True'}),
            'weight': ('django.db.models.fields.FloatField', [], {'blank': 'True'})
        },
        'turan.route': {
            'ascent': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'descent': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'distance': ('django.db.models.fields.FloatField', [], {}),
            'gpx_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '160', 'blank': 'True'}),
            'route_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'turan.userprofiledetail': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'resting_hr': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {}),
            'userprofile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['turan.UserProfile']"}),
            'weight': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'auth.group': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'turan.hike': {
            'avg_hr': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'avg_speed': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'duration': ('DurationField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_hr': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'max_speed': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'route': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['turan.Route']"}),
            'time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        }
    }
    
    complete_apps = ['turan']
