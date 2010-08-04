
from south.db import db
from django.db import models
from turan.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Route'
        db.create_table('turan_route', (
            ('id', orm['turan.Route:id']),
            ('name', orm['turan.Route:name']),
            ('distance', orm['turan.Route:distance']),
            ('description', orm['turan.Route:description']),
            ('route_url', orm['turan.Route:route_url']),
            ('gpx_file', orm['turan.Route:gpx_file']),
            ('ascent', orm['turan.Route:ascent']),
            ('descent', orm['turan.Route:descent']),
            ('start_lat', orm['turan.Route:start_lat']),
            ('start_lon', orm['turan.Route:start_lon']),
            ('end_lat', orm['turan.Route:end_lat']),
            ('end_lon', orm['turan.Route:end_lon']),
            ('created', orm['turan.Route:created']),
            ('single_serving', orm['turan.Route:single_serving']),
            ('tags', orm['turan.Route:tags']),
        ))
        db.send_create_signal('turan', ['Route'])
        
        # Adding model 'Location'
        db.create_table('turan_location', (
            ('id', orm['turan.Location:id']),
            ('lat', orm['turan.Location:lat']),
            ('lon', orm['turan.Location:lon']),
            ('town', orm['turan.Location:town']),
            ('county', orm['turan.Location:county']),
            ('state', orm['turan.Location:state']),
            ('country', orm['turan.Location:country']),
            ('url', orm['turan.Location:url']),
        ))
        db.send_create_signal('turan', ['Location'])
        
        # Adding model 'ExerciseType'
        db.create_table('turan_exercisetype', (
            ('id', orm['turan.ExerciseType:id']),
            ('name', orm['turan.ExerciseType:name']),
        ))
        db.send_create_signal('turan', ['ExerciseType'])
        
        # Adding model 'Exercise'
        db.create_table('turan_exercise', (
            ('id', orm['turan.Exercise:id']),
            ('user', orm['turan.Exercise:user']),
            ('exercise_type', orm['turan.Exercise:exercise_type']),
            ('route', orm['turan.Exercise:route']),
            ('duration', orm['turan.Exercise:duration']),
            ('date', orm['turan.Exercise:date']),
            ('time', orm['turan.Exercise:time']),
            ('comment', orm['turan.Exercise:comment']),
            ('url', orm['turan.Exercise:url']),
            ('avg_speed', orm['turan.Exercise:avg_speed']),
            ('avg_cadence', orm['turan.Exercise:avg_cadence']),
            ('avg_power', orm['turan.Exercise:avg_power']),
            ('max_speed', orm['turan.Exercise:max_speed']),
            ('max_cadence', orm['turan.Exercise:max_cadence']),
            ('max_power', orm['turan.Exercise:max_power']),
            ('avg_hr', orm['turan.Exercise:avg_hr']),
            ('max_hr', orm['turan.Exercise:max_hr']),
            ('kcal', orm['turan.Exercise:kcal']),
            ('temperature', orm['turan.Exercise:temperature']),
            ('sensor_file', orm['turan.Exercise:sensor_file']),
            ('object_id', orm['turan.Exercise:object_id']),
            ('content_type', orm['turan.Exercise:content_type']),
            ('tags', orm['turan.Exercise:tags']),
        ))
        db.send_create_signal('turan', ['Exercise'])
        
        # Adding model 'ExerciseDetail'
        db.create_table('turan_exercisedetail', (
            ('id', orm['turan.ExerciseDetail:id']),
            ('exercise', orm['turan.ExerciseDetail:exercise']),
            ('time', orm['turan.ExerciseDetail:time']),
            ('speed', orm['turan.ExerciseDetail:speed']),
            ('hr', orm['turan.ExerciseDetail:hr']),
            ('altitude', orm['turan.ExerciseDetail:altitude']),
            ('lat', orm['turan.ExerciseDetail:lat']),
            ('lon', orm['turan.ExerciseDetail:lon']),
            ('cadence', orm['turan.ExerciseDetail:cadence']),
            ('power', orm['turan.ExerciseDetail:power']),
        ))
        db.send_create_signal('turan', ['ExerciseDetail'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Route'
        db.delete_table('turan_route')
        
        # Deleting model 'Location'
        db.delete_table('turan_location')
        
        # Deleting model 'ExerciseType'
        db.delete_table('turan_exercisetype')
        
        # Deleting model 'Exercise'
        db.delete_table('turan_exercise')
        
        # Deleting model 'ExerciseDetail'
        db.delete_table('turan_exercisedetail')
        
    
    
    models = {
        'auth.group': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
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
        'turan.exercise': {
            'avg_cadence': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'avg_hr': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'avg_power': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'avg_speed': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'duration': ('DurationField', [], {'default': '0', 'blank': 'True'}),
            'exercise_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['turan.ExerciseType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kcal': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'max_cadence': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'max_hr': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'max_power': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'max_speed': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'route': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['turan.Route']"}),
            'sensor_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'tags': ('TagField', [], {}),
            'temperature': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'turan.exercisedetail': {
            'altitude': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'cadence': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'exercise': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['turan.Exercise']"}),
            'hr': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'lon': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'power': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'speed': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {})
        },
        'turan.exercisetype': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'})
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
        'turan.route': {
            'ascent': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'descent': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'distance': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'end_lat': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'end_lon': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'gpx_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '160', 'blank': 'True'}),
            'route_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'single_serving': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'start_lat': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'start_lon': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'tags': ('TagField', [], {})
        }
    }
    
    complete_apps = ['turan']
