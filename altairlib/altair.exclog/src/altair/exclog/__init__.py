import __builtin__

import logging

from pyramid.tweens import INGRESS
from pyramid.settings import aslist
from pyramid.settings import asbool
from pyramid.util import DottedNameResolver

from .interfaces import IExceptionMessageBuilder, IExceptionMessageRenderer, IExceptionLogger
from .logger import ExceptionMessageBuilder, ExceptionLogger
from .renderer import BasicExceptionMessageRenderer

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

def create_exception_message_builder(registry):
    settings = registry.settings
    return ExceptionMessageBuilder(
        extra_info=asbool(settings.get('altair.exclog.extra_info', True)),
        includes=aslist(settings.get('altair.exclog.includes', DEFAULT_INCLUDES)))

def create_exception_message_renderer(config):
    renderer_factory = config.maybe_dotted(config.registry.settings.get('altair.exclog.renderer_factory', '.renderer.BasicExceptionMessageRenderer'))
    return renderer_factory(show_traceback=asbool(config.registry.settings.get('altair.exclog.show_traceback', 'false')))

def create_exception_logger(registry):
    return ExceptionLogger(logger)

def as_globals_list(value):
    L = []
    value = aslist(value)
    for dottedname in value:
        if dottedname in __builtin__.__dict__:
            dottedname = '__builtin__.%s' % dottedname
        obj = resolver.resolve(dottedname)
        L.append(obj)
    return L

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
    config.registry.registerUtility(create_exception_message_builder(config.registry), IExceptionMessageBuilder)
    config.registry.registerUtility(create_exception_message_renderer(config), IExceptionMessageRenderer)
    config.registry.registerUtility(create_exception_logger(config.registry), IExceptionLogger)
    config.add_tween('.tweens.ExcLogTween', under=INGRESS)
from pyramid.httpexceptions import HTTPInternalServerError, WSGIHTTPException
