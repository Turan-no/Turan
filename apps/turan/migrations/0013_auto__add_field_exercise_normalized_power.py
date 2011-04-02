# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Exercise.normalized_power'
        db.add_column('turan_exercise', 'normalized_power', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Exercise.normalized_power'
        db.delete_column('turan_exercise', 'normalized_power')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'turan.bestpowereffort': {
            'Meta': {'ordering': "('duration',)", 'object_name': 'BestPowerEffort'},
            'ascent': ('django.db.models.fields.IntegerField', [], {}),
            'descent': ('django.db.models.fields.IntegerField', [], {}),
            'duration': ('django.db.models.fields.IntegerField', [], {}),
            'exercise': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['turan.Exercise']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.FloatField', [], {}),
            'pos': ('django.db.models.fields.FloatField', [], {}),
            'power': ('django.db.models.fields.IntegerField', [], {})
        },
        'turan.bestspeedeffort': {
            'Meta': {'ordering': "('duration',)", 'object_name': 'BestSpeedEffort'},
            'ascent': ('django.db.models.fields.IntegerField', [], {}),
            'descent': ('django.db.models.fields.IntegerField', [], {}),
            'duration': ('django.db.models.fields.IntegerField', [], {}),
            'exercise': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['turan.Exercise']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.FloatField', [], {}),
            'pos': ('django.db.models.fields.FloatField', [], {}),
            'speed': ('django.db.models.fields.FloatField', [], {})
        },
        'turan.exercise': {
            'Meta': {'ordering': "('-date', '-time')", 'object_name': 'Exercise'},
            'avg_cadence': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'avg_hr': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'avg_pedaling_cad': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'avg_pedaling_power': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'avg_power': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'avg_speed': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'duration': ('django.db.models.fields.DecimalField', [], {'default': '0', 'blank': 'True'}),
            'exercise_permission': ('django.db.models.fields.CharField', [], {'default': "'A'", 'max_length': '1'}),
            'exercise_type': ('django.db.models.fields.related.ForeignKey', [], {'default': '13', 'to': "orm['turan.ExerciseType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kcal': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'max_cadence': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'max_hr': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'max_power': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'max_speed': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'max_temperature': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'min_temperature': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'normalized_power': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'route': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['turan.Route']", 'null': 'True', 'blank': 'True'}),
            'sensor_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'tags': ('tagging.fields.TagField', [], {}),
            'temperature': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'turan.exercisedetail': {
            'Meta': {'ordering': "('time',)", 'object_name': 'ExerciseDetail'},
            'altitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'cadence': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'distance': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'exercise': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['turan.Exercise']"}),
            'hr': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'lon': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'power': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'speed': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'temp': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {})
        },
        'turan.exercisepermission': {
            'Meta': {'object_name': 'ExercisePermission'},
            'cadence': ('django.db.models.fields.CharField', [], {'default': "'A'", 'max_length': '1'}),
            'exercise': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['turan.Exercise']", 'unique': 'True', 'primary_key': 'True'}),
            'hr': ('django.db.models.fields.CharField', [], {'default': "'A'", 'max_length': '1'}),
            'power': ('django.db.models.fields.CharField', [], {'default': "'A'", 'max_length': '1'}),
            'speed': ('django.db.models.fields.CharField', [], {'default': "'A'", 'max_length': '1'})
        },
        'turan.exercisetype': {
            'Meta': {'ordering': "('name',)", 'object_name': 'ExerciseType'},
            'altitude': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'slopes': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'turan.interval': {
            'Meta': {'ordering': "('start_time',)", 'object_name': 'Interval'},
            'ascent': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'avg_cadence': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'avg_hr': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'avg_power': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'avg_speed': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'avg_temp': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'descent': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'distance': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'duration': ('django.db.models.fields.IntegerField', [], {}),
            'end_lat': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'end_lon': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'exercise': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['turan.Exercise']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kcal': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'max_cadence': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'max_hr': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'max_power': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'max_speed': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'min_cadence': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'min_hr': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'min_power': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'min_speed': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'start': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'start_lat': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'start_lon': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {})
        },
        'turan.location': {
            'Meta': {'object_name': 'Location'},
            'country': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'county': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'lon': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'town': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128', 'blank': 'True'})
        },
        'turan.mergesensorfile': {
            'Meta': {'object_name': 'MergeSensorFile'},
            'altitude': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'cadence': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'exercise': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['turan.Exercise']"}),
            'hr': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'merge_strategy': ('django.db.models.fields.CharField', [], {'default': "'M'", 'max_length': '1'}),
            'position': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'power': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sensor_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'speed': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'turan.route': {
            'Meta': {'ordering': "('-created', 'name')", 'object_name': 'Route'},
            'ascent': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'descent': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'distance': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'end_lat': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'end_lon': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'gpx_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_altitude': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'min_altitude': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '160', 'blank': 'True'}),
            'route_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'single_serving': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start_lat': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'start_lon': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'tags': ('tagging.fields.TagField', [], {})
        },
        'turan.segment': {
            'Meta': {'object_name': 'Segment'},
            'ascent': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.IntegerField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'descent': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'distance': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'end_lat': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'end_lon': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'gpx_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'grade': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_altitude': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'min_altitude': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '160', 'blank': 'True'}),
            'start_lat': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'start_lon': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'tags': ('tagging.fields.TagField', [], {})
        },
        'turan.slope': {
            'Meta': {'ordering': "('-exercise__date',)", 'object_name': 'Slope'},
            'act_power': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'ascent': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'avg_hr': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'category': ('django.db.models.fields.IntegerField', [], {}),
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'duration': ('django.db.models.fields.IntegerField', [], {}),
            'end_lat': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'end_lon': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'est_power': ('django.db.models.fields.FloatField', [], {}),
            'exercise': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['turan.Exercise']"}),
            'grade': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'power_per_kg': ('django.db.models.fields.FloatField', [], {}),
            'segment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['turan.Segment']", 'null': 'True', 'blank': 'True'}),
            'speed': ('django.db.models.fields.FloatField', [], {}),
            'start': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'start_lat': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'start_lon': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'vam': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['turan']
