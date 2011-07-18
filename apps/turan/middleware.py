from django.template import RequestContext
from django.conf import settings
from django.core.exceptions import PermissionDenied  
from django.http import HttpResponseForbidden
from django.template import RequestContext, Context, loader
from sentry.client.models import get_client
import logging

class Http403(Exception):
    pass  

def render_to_403(*args, **kwargs):
    """
        Returns a HttpResponseForbidden whose content is filled with the result of calling
        django.template.loader.render_to_string() with the passed arguments.
    """
    if not isinstance(args,list):
        args = []
        args.append('403.html')

    httpresponse_kwargs = {'mimetype': kwargs.pop('mimetype', None)}
    response = HttpResponseForbidden(loader.render_to_string(*args, **kwargs), **httpresponse_kwargs)

    return response

class Http403Middleware(object):
    def process_exception(self,request,exception):
        if isinstance(exception,Http403):
            #if settings.DEBUG:
            #    raise PermissionDenied
            return render_to_403(context_instance=RequestContext(request))

class TuranSentry404CatchMiddleware(object):
    def process_response(self, request, response):
        if response.status_code == 404 and request.META.get('HTTP_REFERER', ''):
            message_id = get_client().create_from_text('Http 404 %s' %request.path, request=request, level=logging.INFO, logger='http404')
            request.sentry = {
                'id': message_id,
                }
        return response

class TuranSentryMarkup(object):
    '''Add more information to the sentry log'''

    def process_exception(self, request, exception):
        # Make sure the exception signal is fired for Sentry
        if request.user:
            request.META['TURANUSER'] = request.user
        return None
