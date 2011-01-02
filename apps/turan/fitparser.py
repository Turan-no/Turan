from datetime import datetime, timedelta
import struct

fit_file_id = {
    'type': 0,
    'serial': 3,
    'manufacturer': 1,
    'time_created': 3,
    'product': 2,
    'number': 5}

fit_record = {
    'timestamp': 253,
    'lat': 0,
    'lon': 1,
    'dist': 5,
    'time_from_course': 11,
    'speed_distance': 8,
    'hr': 3,
    'alt': 2,
    'speed': 6,
    'power': 7,
    'grade': 9,
    'cadence': 4,
    'resistance': 10,
    'cycle_length': 12,
    'temperature': 13}

fit_file_type = {
    1:  'device',
    2:  'settings',
    3:  'sport',
    4:  'activity',
    5:  'workout',
    9:  'weight',
    10: 'totals',
    11: 'goals',
    12: 'blood pressure'}

fit_msg_type = {
    0:  'file id',
    1:  'capabilites',
    2:  'device settings',
    3:  'user profile',
    4:  'HRM profile',
    5:  'SDM profile',
    6:  'bike profile',
    7:  'zones target',
    8:  'HR zone',
    9:  'power zone',
    10: 'met zone',
    12: 'sport',
    15: 'training goals',
    18: 'session',
    19: 'lap',
    20: 'record',
    21: 'event',
    22: 'unknown',
    23: 'device info',
    26: 'workout',
    27: 'workout step',
    30: 'weight scale',
    33: 'totals',
    34: 'activity',
    35: 'software',
    37: 'file capabilities',
    38: 'mesg capabilities',
    39: 'field capabilities',
    49: 'file creator',
    51: 'blood pressure',
    int('0xFF00', 16): 'mfg range min',
    int('0xFFFE', 16): 'mfg range max'}

fit_base_types = {
    0:  {'number':  0, 'endian': 0, 'field': int('0x00' ,16), 'type': 'enum',    'invalid': int('0xFF' ,16),               'size': 1},
    1:  {'number':  1, 'endian': 0, 'field': int('0x01' ,16), 'type': 'sint8',   'invalid': int('0x7F' ,16),               'size': 1},
    2:  {'number':  2, 'endian': 0, 'field': int('0x02' ,16), 'type': 'uint8',   'invalid': int('0xFF' ,16),               'size': 1},
    3:  {'number':  3, 'endian': 1, 'field': int('0x83' ,16), 'type': 'sint16',  'invalid': int('0x7FFF' ,16),             'size': 2},
    4:  {'number':  4, 'endian': 1, 'field': int('0x84' ,16), 'type': 'uint16',  'invalid': int('0xFFFF' ,16),             'size': 2},
    5:  {'number':  5, 'endian': 1, 'field': int('0x85' ,16), 'type': 'sint32',  'invalid': int('0x7FFFFFFF' ,16),         'size': 4},
    6:  {'number':  6, 'endian': 1, 'field': int('0x86' ,16), 'type': 'uint32',  'invalid': int('0xFFFFFFFF' ,16),         'size': 4},
    7:  {'number':  7, 'endian': 0, 'field': int('0x07' ,16), 'type': 'string',  'invalid': int('0x00' ,16),               'size': 1},
    8:  {'number':  8, 'endian': 1, 'field': int('0x88' ,16), 'type': 'float32', 'invalid': int('0xFFFFFFFF' ,16),         'size': 2},
    9:  {'number':  9, 'endian': 1, 'field': int('0x89' ,16), 'type': 'float64', 'invalid': int('0xFFFFFFFFFFFFFFFF' ,16), 'size': 4},
    10: {'number': 10, 'endian': 0, 'field': int('0x0A' ,16), 'type': 'uint8z',  'invalid': int('0x00' ,16),               'size': 1},
    11: {'number': 11, 'endian': 1, 'field': int('0x8B' ,16), 'type': 'uint16z', 'invalid': int('0x0000' ,16),             'size': 2},
    12: {'number': 12, 'endian': 1, 'field': int('0x8C' ,16), 'type': 'uint32z', 'invalid': int('0x00000000' ,16),         'size': 4},
    13: {'number': 13, 'endian': 0, 'field': int('0x0D' ,16), 'type': 'byte',    'invalid': int('0xFF' ,16),               'size': 1}}

fit_type_unpack = {
    'enum':    'B',
    'sint8':   'b',
    'uint8':   'B',
    'sint16':  'h',
    'uint16':  'H',
    'sint32':  'i',
    'uint32':  'I',
    'string':  'c',
    'float32': 'f',
    'float64': 'd',
    'uint8z':  'B',
    'uint16z': 'H',
    'uint32z': 'I',
    'byte':    'c'}

timestamp_offset = datetime(1989,12,31,00,00)-datetime.utcfromtimestamp(0)

def get_field_value(fields, field_def, field_name):
    try:
        field = fields[field_def[field_name]]
        value = field['value']
        if value == field['base_type']['invalid']:
            value = 0
    except KeyError:
        value = 0
    return value

class FITEntry(object):
    def __init__(self, time, hr, speed, cadence, power, temp, altitude, lat, lon):
        self.time = time
        self.hr = hr
        self.speed = speed
        self.cadence = cadence
        self.power = power
        self.temp = temp
        self.altitude = altitude
        self.lon = lon
        self.lat = lat

    def __str__(self):
        return '[%s] hr: %s spd: %s cad: %s pwr: %s temp: %s alt: %s lat: %s lon: %s' % (self.time, self.hr, self.speed, self.cadence, self.power, self.temp, self.altitude, self.lat, self.lon)

class FITParser(object):
    
    def __init__(self):
        self.start_lon = 0.0
        self.start_lat = 0.0
        self.end_lon = 0.0
        self.end_lat = 0.0
        self.entries = []
        self.distance_sum = 0.0
        self.ascent = 0.0
        self.descent = 0.0
        self.max_speed = 0
        self.avg_speed = 0
        self.max_hr = 0
        self.avg_hr = 0
        self.avg_cadence = 0
        self.max_cadence = 0
        self.avg_power = 0
        self.max_power = 0
        self.avg_torque = 0.0
        self.max_torque = 0.0
        self.avg_pedaling_cad = 0
        self.avg_pedaling_power = 0
        self.avg_temp = 0.0
        self.max_temp = 0.0
        self.kcal_sum = 0

    def parse_uploaded_file(self, f):
        local_msg_types = {}
        hdr = f.read(12)
        (hdr_size,proto_ver,prof_ver,data_size) = struct.unpack('BBHI',hdr[0:8])
        data_type = hdr[8:]

        if data_type != '.FIT':
            return

        while f.tell() < data_size + hdr_size:
            (hdr,) = struct.unpack('B',f.read(1))
            hdr_type = (hdr >> 7) & 1
            if hdr_type == 0:
                msg_type = (hdr >> 6) & 1
                local_msg_type = (hdr) & 15
                time_offset = -1
            elif hdr_type == 1:
                local_msg_type = (hdr >> 5) & 3
                time_offset = (hdr) & 31
            else:
                # Invalid header type
                return

            if msg_type == 0:
                fields = {}
                global_msg_type = local_msg_types[local_msg_type]['global_msg_number']
                for field in local_msg_types[local_msg_type]['fields']:
                    base_type = fit_base_types[field['base_type']]
                    endian = local_msg_types[local_msg_type]['endian']
                    unpack_string = fit_type_unpack[base_type['type']]
                    field_data = f.read(base_type['size'])
                    if field['endian']:
                        unpack_string = endian + unpack_string
                    (field_value,) = struct.unpack(unpack_string, field_data)
                    fields[field['def_num']] = {'value': field_value, 'base_type': base_type}
                if global_msg_type == 0:
                    if get_field_value(fields, fit_file_id, 'type') != 4:
                        return
                if global_msg_type == 20:
                    hr = get_field_value(fields, fit_record, 'hr')
                    pwr = get_field_value(fields, fit_record, 'power')
                    alt = (get_field_value(fields, fit_record, 'alt') - 500) / 5.
                    lat = get_field_value(fields, fit_record, 'lat')
                    lon = get_field_value(fields, fit_record, 'lon')
                    spd = get_field_value(fields, fit_record, 'speed')/1000.*3.6
                    time = datetime.fromtimestamp(get_field_value(fields, fit_record, 'timestamp'))+timestamp_offset
                    grade = get_field_value(fields, fit_record, 'grade')
                    temp = get_field_value(fields, fit_record, 'temperature')
                    cad = get_field_value(fields, fit_record, 'cadence')

                    self.entries.append(FITEntry(time,hr,spd,cad,pwr,temp,alt, lat, lon))
                    
            elif msg_type == 1:                
                def_hdr = f.read(5)
                (arch,) = struct.unpack('B',def_hdr[1:2])
                if arch == 0:
                    endian = '<'
                elif arch == 1:
                    endian = '>'

                (global_msg_number,n_fields) = struct.unpack(endian + 'HB',def_hdr[2:5])

                fields = []
                for i in range(n_fields):
                    (field_def_num,field_size,base_type) = struct.unpack('BBB',f.read(3))
                    field_endian = (base_type >> 7) & 1
                    field_base_type = (base_type) & 31
                    fields.append({'def_num': field_def_num, 'size': field_size, 'endian': field_endian, 'base_type': field_base_type})
                local_msg_types[local_msg_type] = {'arch': arch, 'endian': endian, 'global_msg_number': global_msg_number, 'fields': fields}

if __name__ == '__main__':
    import pprint
    import sys
    t = FITParser()
    t.parse_uploaded_file(file(sys.argv[1]))

    for fit_e in t.entries:
        print fit_e
    """
    print 'start: %s %s - duration: %s - distance: %s' % (t.date, t.start_time, t.duration, t.distance_sum)
    print 'start - lat: %s - lon: %s' % (t.start_lat, t.start_lon)
    print 'end - lat: %s - lon: %s' % (t.end_lat, t.end_lon)
    print 'HR - avg: %s - max: %s' % (t.avg_hr, t.max_hr)
    print 'SPEED - avg: %s - max: %s' % (t.avg_speed, t.max_speed)
    print 'CADENCE - avg: %s - max: %s - pedal: %s' % (t.avg_cadence, t.max_cadence, t.avg_pedaling_cad)
    print 'POWER - avg: %s - max: %s - pedal: %s' % (t.avg_power, t.max_power, t.avg_pedaling_power)
    print 'TORQUE - avg: %s - max: %s' % (t.avg_torque, t.max_torque)
    print 'TEMP - avg: %s - max: %s' % (t.avg_temp, t.max_temp)
    """
