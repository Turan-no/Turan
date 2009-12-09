import MySQLdb
import MySQLdb.cursors



conn_o = MySQLdb.connect(host = "localhost", user = "lortal", passwd = "l0rt4l", db = "lortal_pinax", cursorclass=MySQLdb.cursors.DictCursor)
conn_n = MySQLdb.connect(host = "localhost", user = "lortal", passwd = "l0rt4l", db = "turan", cursorclass=MySQLdb.cursors.DictCursor)
cursor_o = conn_o.cursor()
cursor_n = conn_n.cursor()

sql = "SELECT * from turan_cycletrip order by id"

cursor_o.execute(sql)
result = cursor_o.fetchall()
oldid = 0
for index, row in enumerate(result):
    id = index+1
    fields = []
    values = ''
    for field in row:
        value = row[field]
        if not value:
            continue
        if field == 'id':
            # autogenerate id
            oldid = value
            continue
        fields.append(field)
        if type(value) == type(''):
            value = value.replace('"', '\\"')
        values += """"%s", """ %value

    fields = ', '.join(fields)
    values = values.rstrip(', ')
    insertsql = '''INSERT INTO turan_exercise (exercise_type_id, id, %s) VALUES (13, %s, %s)''' %(fields, oldid, values)
    cursor_n.execute(insertsql)

    cursor_o.execute('select * from turan_cycletripdetail where trip_id = %s' %oldid)
    for row in cursor_o.fetchall():
        fields = []
        values = ''
        for field in row:
            value = row[field]
            if not value and not type(value) == type(0.0) and not type(value) == type(0L):
                continue
            if field == 'id' or field == 'trip_id':
                # autogenerate id
                continue
            fields.append(field)
            values += """"%s", """ %value

        fields = ', '.join(fields)
        values = values.rstrip(', ')
        insertsql = '''INSERT INTO turan_exercisedetail (exercise_id, %s) VALUES (%s, %s)''' %(fields, oldid, values)
        cursor_n.execute(insertsql)
    print oldid


## HIIIIIIIIIIIIKE
sql = "SELECT * from turan_hike"

cursor_o.execute(sql)
result = cursor_o.fetchall()
for row in result:
    oldid += 1
    fields = []
    values = ''
    for field in row:
        value = row[field]
        if not value:
            continue
        if field == 'id':
            # autogenerate id
            real_oldid = value
            continue
        fields.append(field)
        if type(value) == type(''):
            value = value.replace('"', '\\"')
        values += """"%s", """ %value

    fields = ', '.join(fields)
    values = values.rstrip(', ')
    insertsql = '''INSERT INTO turan_exercise (exercise_type_id, id, %s) VALUES (14, %s, %s)''' %(fields, oldid, values)
    cursor_n.execute(insertsql)
    print oldid

    cursor_o.execute('select * from turan_hikedetail where trip_id = %s' %real_oldid)
    for row in cursor_o.fetchall():
        fields = []
        values = ''
        for field in row:
            value = row[field]
            if not value and not type(value) == type(0.0) and not type(value) == type(0L):
                continue
            if field == 'id' or field == 'trip_id':
                # autogenerate id
                continue
            fields.append(field)
            values += """"%s", """ %value

        fields = ', '.join(fields)
        values = values.rstrip(', ')
        insertsql = '''INSERT INTO turan_exercisedetail (exercise_id, %s) VALUES (%s, %s)''' %(fields, oldid, values)
        cursor_n.execute(insertsql)




## OtherExercise
sql = "SELECT * from turan_otherexercise"

cursor_o.execute(sql)
result = cursor_o.fetchall()
for row in result:
    oldid += 1
    fields = []
    values = ''
    for field in row:
        value = row[field]
        if not value:
            continue
        if field == 'id':
            # autogenerate id
            real_oldid = value
            continue
        fields.append(field)
        if type(value) == type(''):
            value = value.replace('"', '\\"')
        values += """"%s", """ %value

    fields = ', '.join(fields)
    values = values.rstrip(', ')
    insertsql = '''INSERT INTO turan_exercise (id, %s) VALUES (%s, %s)''' %(fields, oldid, values)
    cursor_n.execute(insertsql)

    cursor_o.execute('select * from turan_otherexercisedetail where trip_id = %s' %real_oldid)
    for row in cursor_o.fetchall():
        fields = []
        values = ''
        for field in row:
            value = row[field]
            if not value and not type(value) == type(0.0) and not type(value) == type(0L):
                continue
            if field == 'id' or field == 'trip_id':
                # autogenerate id
                continue
            fields.append(field)
            values += """"%s", """ %value

        fields = ', '.join(fields)
        values = values.rstrip(', ')
        insertsql = '''INSERT INTO turan_exercisedetail (exercise_id, %s) VALUES (%s, %s)''' %(fields, oldid, values)
        cursor_n.execute(insertsql)
