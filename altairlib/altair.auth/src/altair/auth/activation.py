# This package may contain traces of nuts
import os
import sys
import logging
from webob.response import Response as WebObResponse
from pyramid.tweens import INGRESS
from pyramid.response import Response

from .api import decide, who_api

logger = logging.getLogger(__name__)

def deactivate(request):
    from . import REQUEST_KEY
    try:
        del request.environ[REQUEST_KEY]
    except KeyError:
        pass
    try:
        del request.environ['altair.auth.who_api_cache']
    except KeyError:
        pass
    
def activate_who_api_tween(handler, registry):
    from . import REQUEST_KEY
    def wrap(request):
        try:
            request.environ[REQUEST_KEY] = request
            return handler(request)
        finally:
            deactivate(request)
    return wrap

def stringize_resp(request, wsgi_resp):
    if isinstance(wsgi_resp, WebObResponse):
        return WebObResponse.__repr__(wsgi_resp)
    else:
        return repr(wsgi_resp)

class ChallengeView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        wsgi_resp = None
        api, api_name = who_api(self.request)
        if api is not None:
            logger.debug('challenge: api=%r, api_name=%s, context=%s' % (api, api_name, self.context))
            try:
                wsgi_resp = api.challenge()
            except:
                logger.exception('challenge: exception occurred')
                raise
            logger.debug('challenge: response=%s' % stringize_resp(self.request, wsgi_resp))
        if wsgi_resp is None:
            msg = u'authentication failed where no challenge mechanism is provided'
            logger.error(msg)
            return Response(status=403, body=u'We are experiencing a system error that you cannot get around at the moment. Sorry for the inconvenience... (guru meditation: {0})'.format(msg), content_type='text/plain')
        else:
            return self.request.get_response(wsgi_resp)

def includeme(config):
    config.add_tween("altair.auth.activation.activate_who_api_tween", under=INGRESS)
    config.add_forbidden_view(ChallengeView)

