import sys

from textwrap import dedent
from pprint import pformat

from zope.interface import implementer
from pyramid.settings import asbool, aslist

from .interfaces import IExceptionMessageBuilder, IExceptionLogger

@implementer(IExceptionMessageBuilder)
class ExceptionMessageBuilder(object):
    def __init__(self, extra_info, includes):
        self.extra_info = extra_info
        self.includes = includes

    def filter_environ(self, environ):
        return dict([(e, v) for e, v in environ.items() if e in self.includes])

    def __call__(self, request):
        if self.extra_info:
            message = dedent("""\n
            %(url)s
            
            ENVIRONMENT
            
            %(env)s
            
            
            
            """ % dict(url=request.url,
                       env=pformat(self.filter_environ(request.environ))))

        else:
            message = request.url
        return getattr(request, 'exc_info', None) or sys.exc_info(), message
        # return sys.exc_info(), message

@implementer(IExceptionLogger)
class ExceptionLogger(object):
    def __init__(self, logger):
        self.logger = logger

    def __call__(self, exc_info, message):
        self.logger.error(message, exc_info=exc_info)
