import sys

from textwrap import dedent
from pprint import pformat

from zope.interface import implementer
from pyramid.settings import asbool, aslist

from .interfaces import IExceptionMessageBuilder, IExceptionLogger

@implementer(IExceptionMessageBuilder)
class ExceptionMessageBuilder(object):
    def __init__(self, include_env_dump, includes):
        self.include_env_dump = include_env_dump
        self.includes = includes

    def filter_environ(self, environ):
        return dict([(e, v) for e, v in environ.items() if e in self.includes])

    def __call__(self, request):
        filtered_env = self.filter_environ(request.environ)
        if self.include_env_dump:
            message = dedent("""\n
            %(url)s
            
            ENVIRONMENT
            
            %(env)s
            
            
            
            """ % dict(url=request.url,
                       env=pformat(filtered_env)))
        else:
            message = request.url
        return (
            getattr(request, 'exc_info', None) or sys.exc_info(),
            message,
            {
                'environ': filtered_env,
                'params': list(request.params.items()) if hasattr(request, 'params') else None,
                'session': dict(request.session) if hasattr(request, 'session') else None,
                }
            )

@implementer(IExceptionLogger)
class ExceptionLogger(object):
    def __init__(self, logger):
        self.logger = logger

    def __call__(self, exc_info, message, extra_info):
        self.logger.error(message, exc_info=exc_info, extra=extra_info)
