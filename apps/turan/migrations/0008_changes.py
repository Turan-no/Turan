
from south.db import db
from django.db import models
from turan.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'OtherExerciseDetail'
        db.create_table('turan_otherexercisedetail', (
            ('id', orm['turan.otherexercisedetail:id']),
            ('time', orm['turan.otherexercisedetail:time']),
            ('speed', orm['turan.otherexercisedetail:speed']),
            ('hr', orm['turan.otherexercisedetail:hr']),
            ('altitude', orm['turan.otherexercisedetail:altitude']),
            ('lat', orm['turan.otherexercisedetail:lat']),
            ('lon', orm['turan.otherexercisedetail:lon']),
            ('trip', orm['turan.otherexercisedetail:trip']),
        ))
        db.send_create_signal('turan', ['OtherExerciseDetail'])
        
        # Adding model 'ExerciseType'
        db.create_table('turan_exercisetype', (
            ('id', orm['turan.exercisetype:id']),
            ('name', orm['turan.exercisetype:name']),
        ))
        db.send_create_signal('turan', ['ExerciseType'])
        
        # Adding model 'OtherExercise'
        db.create_table('turan_otherexercise', (
            ('id', orm['turan.otherexercise:id']),
            ('user', orm['turan.otherexercise:user']),
            ('route', orm['turan.otherexercise:route']),
            ('duration', orm['turan.otherexercise:duration']),
            ('date', orm['turan.otherexercise:date']),
            ('time', orm['turan.otherexercise:time']),
            ('comment', orm['turan.otherexercise:comment']),
            ('url', orm['turan.otherexercise:url']),
            ('avg_hr', orm['turan.otherexercise:avg_hr']),
            ('max_hr', orm['turan.otherexercise:max_hr']),
            ('kcal', orm['turan.otherexercise:kcal']),
            ('sensor_file', orm['turan.otherexercise:sensor_file']),
            ('object_id', orm['turan.otherexercise:object_id']),
            ('content_type', orm['turan.otherexercise:content_type']),
            ('exercise_type', orm['turan.otherexercise:exercise_type']),
        ))
        db.send_create_signal('turan', ['OtherExercise'])
        
        # Adding field 'CycleTrip.content_type'
        db.add_column('turan_cycletrip', 'content_type', orm['turan.cycletrip:content_type'])
        
        # Adding field 'Teamsport.sensor_file'
        db.add_column('turan_teamsport', 'sensor_file', orm['turan.teamsport:sensor_file'])
        
        # Adding field 'CycleTrip.object_id'
        db.add_column('turan_cycletrip', 'object_id', orm['turan.cycletrip:object_id'])
        
        # Adding field 'CycleTrip.sensor_file'
        db.add_column('turan_cycletrip', 'sensor_file', orm['turan.cycletrip:sensor_file'])
        
        # Adding field 'Hike.content_type'
        db.add_column('turan_hike', 'content_type', orm['turan.hike:content_type'])
        
        # Adding field 'Teamsport.object_id'
        db.add_column('turan_teamsport', 'object_id', orm['turan.teamsport:object_id'])
        
        # Adding field 'Hike.object_id'
        db.add_column('turan_hike', 'object_id', orm['turan.hike:object_id'])
        
        # Adding field 'Hike.sensor_file'
        db.add_column('turan_hike', 'sensor_file', orm['turan.hike:sensor_file'])
        
        # Adding field 'Teamsport.content_type'
        db.add_column('turan_teamsport', 'content_type', orm['turan.teamsport:content_type'])
        
        # Deleting model 'userprofiledetail'
        db.delete_table('turan_userprofiledetail')
        
        # Deleting model 'userprofile'
        db.delete_table('turan_userprofile')
        
        # Deleting model 'team'
        db.delete_table('turan_team')
        
        # Deleting model 'teammembership'
        db.delete_table('turan_teammembership')
        
        # Changing field 'Teamsport.duration'
        # (to signature: DurationField(default=0, blank=True))
        db.alter_column('turan_teamsport', 'duration', orm['turan.teamsport:duration'])
        
        # Changing field 'CycleTrip.duration'
        # (to signature: DurationField(default=0, blank=True))
        db.alter_column('turan_cycletrip', 'duration', orm['turan.cycletrip:duration'])
        
        # Changing field 'Hike.duration'
        # (to signature: DurationField(default=0, blank=True))
        db.alter_column('turan_hike', 'duration', orm['turan.hike:duration'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'OtherExerciseDetail'
        db.delete_table('turan_otherexercisedetail')
        
        # Deleting model 'ExerciseType'
        db.delete_table('turan_exercisetype')
        
        # Deleting model 'OtherExercise'
        db.delete_table('turan_otherexercise')
        
        # Deleting field 'CycleTrip.content_type'
        db.delete_column('turan_cycletrip', 'content_type_id')
        
        # Deleting field 'Teamsport.sensor_file'
        db.delete_column('turan_teamsport', 'sensor_file')
        
        # Deleting field 'CycleTrip.object_id'
        db.delete_column('turan_cycletrip', 'object_id')
        
        # Deleting field 'CycleTrip.sensor_file'
        db.delete_column('turan_cycletrip', 'sensor_file')
        
        # Deleting field 'Hike.content_type'
        db.delete_column('turan_hike', 'content_type_id')
        
        # Deleting field 'Teamsport.object_id'
        db.delete_column('turan_teamsport', 'object_id')
        
        # Deleting field 'Hike.object_id'
        db.delete_column('turan_hike', 'object_id')
        
        # Deleting field 'Hike.sensor_file'
        db.delete_column('turan_hike', 'sensor_file')
        
        # Deleting field 'Teamsport.content_type'
        db.delete_column('turan_teamsport', 'content_type_id')
        
        # Adding model 'userprofiledetail'
        db.create_table('turan_userprofiledetail', (
            ('weight', orm['turan.teamsport:weight']),
            ('resting_hr', orm['turan.teamsport:resting_hr']),
            ('time', orm['turan.teamsport:time']),
            ('id', orm['turan.teamsport:id']),
            ('userprofile', orm['turan.teamsport:userprofile']),
        ))
        db.send_create_signal('turan', ['userprofiledetail'])
        
        # Adding model 'userprofile'
        db.create_table('turan_userprofile', (
            ('weight', orm['turan.teamsport:weight']),
            ('image', orm['turan.teamsport:image']),
            ('height', orm['turan.teamsport:height']),
            ('cycle_image', orm['turan.teamsport:cycle_image']),
            ('user', orm['turan.teamsport:user']),
            ('motto', orm['turan.teamsport:motto']),
            ('id', orm['turan.teamsport:id']),
            ('cycle', orm['turan.teamsport:cycle']),
            ('info', orm['turan.teamsport:info']),
            ('max_hr', orm['turan.teamsport:max_hr']),
            ('resting_hr', orm['turan.teamsport:resting_hr']),
        ))
        db.send_create_signal('turan', ['userprofile'])
        
        # Adding model 'team'
        db.create_table('turan_team', (
            ('slogan', orm['turan.teamsport:slogan']),
            ('name', orm['turan.teamsport:name']),
            ('url', orm['turan.teamsport:url']),
            ('members', orm['turan.teamsport:members']),
            ('logo', orm['turan.teamsport:logo']),
            ('id', orm['turan.teamsport:id']),
            ('description', orm['turan.teamsport:description']),
        ))
        db.send_create_signal('turan', ['team'])
        
        # Adding model 'teammembership'
        db.create_table('turan_teammembership', (
            ('role', orm['turan.teamsport:role']),
            ('user', orm['turan.teamsport:user']),
            ('team', orm['turan.teamsport:team']),
            ('id', orm['turan.teamsport:id']),
            ('date_joined', orm['turan.teamsport:date_joined']),
        ))
        db.send_create_signal('turan', ['teammembership'])
        
        # Changing field 'Teamsport.duration'
        # (to signature: DurationField())
        db.alter_column('turan_teamsport', 'duration', orm['turan.teamsport:duration'])
        
        # Changing field 'CycleTrip.duration'
        # (to signature: DurationField())
        db.alter_column('turan_cycletrip', 'duration', orm['turan.cycletrip:duration'])
        
        # Changing field 'Hike.duration'
        # (to signature: DurationField())
        db.alter_column('turan_hike', 'duration', orm['turan.hike:duration'])
        
    
    
    models = {
        'auth.group': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'unique': 'True'}),
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
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2009, 7, 24, 13, 15, 55, 882990)'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2009, 7, 24, 13, 15, 55, 882891)'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30', 'unique': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'turan.cycletrip': {
            'avg_cadence': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'avg_hr': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'avg_speed': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'duration': ('DurationField', [], {'default': '0', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kcal': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'max_cadence': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'max_hr': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'max_speed': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'route': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['turan.Route']"}),
            'sensor_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
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
        'turan.exercisetype': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'turan.hike': {
            'avg_hr': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'avg_speed': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'duration': ('DurationField', [], {'default': '0', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kcal': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'max_hr': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'max_speed': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'route': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['turan.Route']"}),
            'sensor_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'turan.hikedetail': {
            'altitude': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'hr': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'lon': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'speed': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {}),
            'trip': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['turan.Hike']"})
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
        'turan.otherexercise': {
            'avg_hr': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'duration': ('DurationField', [], {'default': '0', 'blank': 'True'}),
            'exercise_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['turan.ExerciseType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kcal': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'max_hr': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'route': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['turan.Route']"}),
            'sensor_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'turan.otherexercisedetail': {
            'altitude': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'hr': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'lon': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'speed': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {}),
            'trip': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['turan.OtherExercise']"})
        },
        'turan.route': {
            'ascent': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'descent': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'distance': ('django.db.models.fields.FloatField', [], {}),
            'end_lat': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'end_lon': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'gpx_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '160', 'blank': 'True'}),
            'route_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'start_lat': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'start_lon': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'})
        },
        'turan.team': {
            'description': 'django.db.models.fields.TextField()',
            'id': 'django.db.models.fields.AutoField(primary_key=True)',
            'logo': 'django.db.models.fields.files.ImageField(max_length=100, blank=True)',
            'members': "django.db.models.fields.related.ManyToManyField(to=orm['auth.User'])",
            'name': 'django.db.models.fields.CharField(max_length=160)',
            'slogan': 'django.db.models.fields.TextField(blank=True)',
            'url': 'django.db.models.fields.URLField(max_length=200, blank=True)'
        },
        'turan.teamsport': {
            'avg_hr': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'duration': ('DurationField', [], {'default': '0', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kcal': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'max_hr': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'route': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['turan.Route']"}),
            'sensor_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'turan.userprofile': {
            'cycle': 'django.db.models.fields.CharField(max_length=99, blank=True)',
            'cycle_image': 'django.db.models.fields.files.ImageField(max_length=100, blank=True)',
            'height': 'django.db.models.fields.IntegerField(blank=True)',
            'id': 'django.db.models.fields.AutoField(primary_key=True)',
            'image': 'django.db.models.fields.files.ImageField(max_length=100, blank=True)',
            'info': 'django.db.models.fields.TextField(blank=True)',
            'max_hr': 'django.db.models.fields.IntegerField(default=0, blank=True)',
            'motto': 'django.db.models.fields.CharField(max_length=160)',
            'resting_hr': 'django.db.models.fields.IntegerField(default=0, blank=True)',
            'user': "django.db.models.fields.related.ForeignKey(to=orm['auth.User'], unique=True)",
            'weight': 'django.db.models.fields.FloatField(blank=True)'
        }
    }
    
    complete_apps = ['turan']
