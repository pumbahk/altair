import __builtin__
import sys
import logging
import traceback
import StringIO

from textwrap import dedent
from pprint import pformat

from pyramid.tweens import INGRESS
from pyramid.settings import aslist
from pyramid.settings import asbool
from pyramid.util import DottedNameResolver
from pyramid.httpexceptions import HTTPInternalServerError, WSGIHTTPException
from pyramid.response import Response

DEFAULT_INCLUDES = [
    'CONTENT_TYPE',
    'HTTP_COOKIE',
    'HTTP_HOST',
    'HTTP_REFERER',
    'HTTP_USER_AGENT',
    'HTTP_X_FORWARDED_SSL',
    'PATH_INFO',
    'QUERY_STRING',
    'REMOTE_ADDR',
    'REQUEST_METHOD',
    'SCRIPT_NAME',
    'SERVER_NAME',
    'SERVER_PORT',
    'SERVER_PROTOCOL',
    'altair.browserid.env_key',
    'repoze.browserid',
    'session.rakuten_openid',
]

resolver = DottedNameResolver(None)
logger = logging.getLogger(__name__)

def as_globals_list(value):
    L = []
    value = aslist(value)
    for dottedname in value:
        if dottedname in __builtin__.__dict__:
            dottedname = '__builtin__.%s' % dottedname
        obj = resolver.resolve(dottedname)
        L.append(obj)
    return L


class ExcLogTween(object):
    def __init__(self, handler, registry):
        self.handler = handler
        self.registry = registry

        settings = self.registry.settings

        self.extra_info = settings.get('altair.exclog.extra_info', True)
        self.ignored = settings.get('altair.exclog.ignored', 
                                    (WSGIHTTPException,))
        self.show_traceback = settings.get('altair.exclog.show_traceback', False)
        self.includes = aslist(settings.get('altair.exclog.includes', DEFAULT_INCLUDES))

    def __call__(self, request):

        # getLogger injected for testing purposes
        try:
            return self.handler(request)
        except self.ignored:
            raise
        except:

            if self.extra_info:
                message = dedent("""\n
                %(url)s
                
                ENVIRONMENT
                
                %(env)s
                
                
                
                """ % dict(url=request.url,
                           env=pformat(self.filter_environ(request.environ))))

            else:
                message = request.url
            logger.exception(message)

            if self.show_traceback:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                out = StringIO.StringIO()
                out.write(message + "\n")
                traceback.print_exception(exc_type, exc_value, exc_traceback, file=out)
                return Response(out.getvalue(), status=500, content_type='text/plain')
            return HTTPInternalServerError()

    def filter_environ(self, environ):
        return dict([(e, v) for e, v in environ.items() if e in self.includes])


def _convert_settings(settings):
    extra_info = asbool(settings.get('altair.exclog.extra_info', True))
    ignored = as_globals_list(settings.get('altair.exclog.ignored',
                                           'pyramid.httpexceptions.WSGIHTTPException'))
    show_traceback = asbool(settings.get('altair.exclog.show_traceback', False))

    settings['altair.exclog.extra_info'] = extra_info
    settings['altair.exclog.ignored'] = tuple(ignored)
    settings['altair.exclog.show_traceback'] = show_traceback

def includeme(config):
    _convert_settings(config.registry.settings)
    config.add_tween('.ExcLogTween', under=INGRESS)
