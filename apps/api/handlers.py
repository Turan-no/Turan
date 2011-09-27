from piston.handler import BaseHandler
from turan.models import Exercise, Route

class ExerciseHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Exercise

    def read(self, request, object_id=None):
        """
        Returns a single post if `blogpost_id` is given,
        otherwise a subset.

        """
        base = Exercise.objects

        if object_id:
            return base.get(pk=object_id)
        else:
            return base.all()[:20]

class RouteHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Route
    fields = ('id', 'name', 'description', ('exercise_set', ('id','duration', 'date',('user', ('username',))),),)

    def read(self, request, object_id=None):
        """
        Returns a single post if `blogpost_id` is given,
        otherwise a subset.

        """
        base = Route.objects

        if object_id:
            return base.get(pk=object_id)
        else:
            return base.all()[:20]

