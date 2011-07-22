# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Exercise.max_speed_lat'
        db.add_column('turan_exercise', 'max_speed_lat', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True), keep_default=False)

        # Adding field 'Exercise.max_speed_lon'
        db.add_column('turan_exercise', 'max_speed_lon', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True), keep_default=False)

        # Adding field 'Exercise.max_power_lat'
        db.add_column('turan_exercise', 'max_power_lat', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True), keep_default=False)

        # Adding field 'Exercise.max_power_lon'
        db.add_column('turan_exercise', 'max_power_lon', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True), keep_default=False)

        # Adding field 'Exercise.max_cadence_lat'
        db.add_column('turan_exercise', 'max_cadence_lat', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True), keep_default=False)

        # Adding field 'Exercise.max_cadence_lon'
        db.add_column('turan_exercise', 'max_cadence_lon', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True), keep_default=False)

        # Adding field 'Exercise.max_hr_lat'
        db.add_column('turan_exercise', 'max_hr_lat', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True), keep_default=False)

        # Adding field 'Exercise.max_hr_lon'
        db.add_column('turan_exercise', 'max_hr_lon', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True), keep_default=False)

        # Adding field 'Exercise.max_altitude_lat'
        db.add_column('turan_exercise', 'max_altitude_lat', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True), keep_default=False)

        # Adding field 'Exercise.max_altitude_lon'
        db.add_column('turan_exercise', 'max_altitude_lon', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Exercise.max_speed_lat'
        db.delete_column('turan_exercise', 'max_speed_lat')

        # Deleting field 'Exercise.max_speed_lon'
        db.delete_column('turan_exercise', 'max_speed_lon')

        # Deleting field 'Exercise.max_power_lat'
        db.delete_column('turan_exercise', 'max_power_lat')

        # Deleting field 'Exercise.max_power_lon'
        db.delete_column('turan_exercise', 'max_power_lon')

        # Deleting field 'Exercise.max_cadence_lat'
        db.delete_column('turan_exercise', 'max_cadence_lat')

        # Deleting field 'Exercise.max_cadence_lon'
        db.delete_column('turan_exercise', 'max_cadence_lon')

        # Deleting field 'Exercise.max_hr_lat'
        db.delete_column('turan_exercise', 'max_hr_lat')

        # Deleting field 'Exercise.max_hr_lon'
        db.delete_column('turan_exercise', 'max_hr_lon')

        # Deleting field 'Exercise.max_altitude_lat'
        db.delete_column('turan_exercise', 'max_altitude_lat')

        # Deleting field 'Exercise.max_altitude_lon'
        db.delete_column('turan_exercise', 'max_altitude_lon')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
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
        'turan.commonaltitudegradient': {
            'Meta': {'ordering': "('xaxis',)", 'object_name': 'CommonAltitudeGradient'},
            'altitude': ('django.db.models.fields.FloatField', [], {}),
            'gradient': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'xaxis': ('django.db.models.fields.FloatField', [], {})
        },
        'turan.component': {
            'Meta': {'object_name': 'Component'},
            'added': ('django.db.models.fields.DateField', [], {}),
            'brand': ('django.db.models.fields.CharField', [], {'max_length': '140'}),
            'componenttype': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['turan.ComponentType']"}),
            'equipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['turan.Equipment']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '140'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'removed': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'weight': ('django.db.models.fields.FloatField', [], {'default': '0', 'blank': 'True'})
        },
        'turan.componenttype': {
            'Meta': {'object_name': 'ComponentType'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '140'})
        },
        'turan.equipment': {
            'Meta': {'ordering': "('-aquired',)", 'object_name': 'Equipment'},
            'aquired': ('django.db.models.fields.DateField', [], {}),
            'brand': ('django.db.models.fields.CharField', [], {'max_length': '140'}),
            'equipmenttype': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['turan.EquipmentType']"}),
            'exercise_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['turan.ExerciseType']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '140'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'riding_weight': ('django.db.models.fields.FloatField', [], {'default': '0', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'weight': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'turan.equipmenttype': {
            'Meta': {'object_name': 'EquipmentType'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '140'})
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
            'equipment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['turan.Equipment']", 'null': 'True', 'blank': 'True'}),
            'exercise_permission': ('django.db.models.fields.CharField', [], {'default': "'A'", 'max_length': '1'}),
            'exercise_type': ('django.db.models.fields.related.ForeignKey', [], {'default': '13', 'to': "orm['turan.ExerciseType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kcal': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'live_state': ('django.db.models.fields.CharField', [], {'default': "'F'", 'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'max_altitude_lat': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'max_altitude_lon': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'max_cadence': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'max_cadence_lat': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'max_cadence_lon': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'max_hr': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'max_hr_lat': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'max_hr_lon': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'max_power': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'max_power_lat': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'max_power_lon': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'max_speed': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'max_speed_lat': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'max_speed_lon': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'max_temperature': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'min_temperature': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'normalized_hr': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
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
        'turan.exercisealtitudegradient': {
            'Meta': {'ordering': "('xaxis',)", 'object_name': 'ExerciseAltitudeGradient', '_ormbases': ['turan.CommonAltitudeGradient']},
            'commonaltitudegradient_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['turan.CommonAltitudeGradient']", 'unique': 'True', 'primary_key': 'True'}),
            'exercise': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['turan.Exercise']"})
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
        'turan.freq': {
            'Meta': {'object_name': 'Freq'},
            'exercise': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['turan.Exercise']"}),
            'freq_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'json': ('django.db.models.fields.TextField', [], {})
        },
        'turan.hrzonesummary': {
            'Meta': {'ordering': "('zone',)", 'object_name': 'HRZoneSummary'},
            'duration': ('django.db.models.fields.IntegerField', [], {}),
            'exercise': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['turan.Exercise']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'zone': ('django.db.models.fields.IntegerField', [], {})
        },
        'turan.interval': {
            'Meta': {'ordering': "('start_time',)", 'object_name': 'Interval'},
            'ascent': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'avg_cadence': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'avg_hr': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'avg_pedaling_cadence': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '160', 'null': 'True', 'blank': 'True'}),
            'route_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'single_serving': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start_lat': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'start_lon': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'tags': ('tagging.fields.TagField', [], {})
        },
        'turan.segment': {
            'Meta': {'object_name': 'Segment'},
            'ascent': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'descent': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'distance': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'end_lat': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'end_lon': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'gpx_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'grade': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_altitude': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'min_altitude': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'segment_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'start_lat': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'start_lon': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'tags': ('tagging.fields.TagField', [], {})
        },
        'turan.segmentdetail': {
            'Meta': {'ordering': "('duration',)", 'object_name': 'SegmentDetail'},
            'act_power': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'ascent': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'avg_hr': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
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
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'segment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['turan.Segment']", 'null': 'True', 'blank': 'True'}),
            'speed': ('django.db.models.fields.FloatField', [], {}),
            'start': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'start_lat': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'start_lon': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'vam': ('django.db.models.fields.IntegerField', [], {'default': '0'})
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
        },
        'turan.wzonesummary': {
            'Meta': {'ordering': "('zone',)", 'object_name': 'WZoneSummary'},
            'duration': ('django.db.models.fields.IntegerField', [], {}),
            'exercise': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['turan.Exercise']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'zone': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['turan']
