
from south.db import db
from django.db import models
from turan.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding field 'Exercise.exercise_permission'
        db.add_column('turan_exercise', 'exercise_permission', orm['turan.exercise:exercise_permission'])
        
        # Changing field 'Exercise.exercise_type'
        # (to signature: django.db.models.fields.related.ForeignKey(default=13, to=orm['turan.ExerciseType']))
        db.alter_column('turan_exercise', 'exercise_type_id', orm['turan.exercise:exercise_type'])
        
        # Changing field 'ExercisePermission.power'
        # (to signature: django.db.models.fields.CharField(default='A', max_length=1))
        db.alter_column('turan_exercisepermission', 'power', orm['turan.exercisepermission:power'])
        
        # Changing field 'ExercisePermission.hr'
        # (to signature: django.db.models.fields.CharField(default='A', max_length=1))
        db.alter_column('turan_exercisepermission', 'hr', orm['turan.exercisepermission:hr'])
        
        # Changing field 'ExercisePermission.speed'
        # (to signature: django.db.models.fields.CharField(default='A', max_length=1))
        db.alter_column('turan_exercisepermission', 'speed', orm['turan.exercisepermission:speed'])
        
        # Changing field 'ExercisePermission.cadence'
        # (to signature: django.db.models.fields.CharField(default='A', max_length=1))
        db.alter_column('turan_exercisepermission', 'cadence', orm['turan.exercisepermission:cadence'])
        
    
    
    def backwards(self, orm):
        
        # Deleting field 'Exercise.exercise_permission'
        db.delete_column('turan_exercise', 'exercise_permission')
        
        # Changing field 'Exercise.exercise_type'
        # (to signature: django.db.models.fields.related.ForeignKey(to=orm['turan.ExerciseType']))
        db.alter_column('turan_exercise', 'exercise_type_id', orm['turan.exercise:exercise_type'])
        
        # Changing field 'ExercisePermission.power'
        # (to signature: django.db.models.fields.CharField(max_length=1))
        db.alter_column('turan_exercisepermission', 'power', orm['turan.exercisepermission:power'])
        
        # Changing field 'ExercisePermission.hr'
        # (to signature: django.db.models.fields.CharField(max_length=1))
        db.alter_column('turan_exercisepermission', 'hr', orm['turan.exercisepermission:hr'])
        
        # Changing field 'ExercisePermission.speed'
        # (to signature: django.db.models.fields.CharField(max_length=1))
        db.alter_column('turan_exercisepermission', 'speed', orm['turan.exercisepermission:speed'])
        
        # Changing field 'ExercisePermission.cadence'
        # (to signature: django.db.models.fields.CharField(max_length=1))
        db.alter_column('turan_exercisepermission', 'cadence', orm['turan.exercisepermission:cadence'])
        
    
    
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
            'exercise_permission': ('django.db.models.fields.CharField', [], {'default': "'A'", 'max_length': '1'}),
            'exercise_type': ('django.db.models.fields.related.ForeignKey', [], {'default': '13', 'to': "orm['turan.ExerciseType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kcal': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'max_cadence': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'max_hr': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'max_power': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'max_speed': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'route': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['turan.Route']", 'null': 'True', 'blank': 'True'}),
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
        'turan.exercisepermission': {
            'cadence': ('django.db.models.fields.CharField', [], {'default': "'A'", 'max_length': '1'}),
            'exercise': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['turan.Exercise']", 'unique': 'True', 'primary_key': 'True'}),
            'hr': ('django.db.models.fields.CharField', [], {'default': "'A'", 'max_length': '1'}),
            'power': ('django.db.models.fields.CharField', [], {'default': "'A'", 'max_length': '1'}),
            'speed': ('django.db.models.fields.CharField', [], {'default': "'A'", 'max_length': '1'})
        },
        'turan.exercisetype': {
            'altitude': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'slopes': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'})
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
