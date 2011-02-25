from turan.models import *
eds = Exercise.objects.get(pk=3723).exercisedetail_set.all()
a = {}
previous = eds[0].time
for e in eds:
    time_d = (e.time - previous).seconds
    if not time_d in a:
        a[time_d] = 0
    a[time_d] += 1
    previous = e.time
