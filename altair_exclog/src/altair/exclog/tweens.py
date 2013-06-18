from pyramid.settings import asbool
from pyramid.httpexceptions import HTTPInternalServerError, WSGIHTTPException

from .interfaces import IExceptionMessageBuilder, IExceptionMessageRenderer, IExceptionLogger

class ExcLogTween(object):
    def __init__(self, handler, registry):
        self.handler = handler
        self.registry = registry

        settings = self.registry.settings

        self.ignored = settings.get('altair.exclog.ignored', 
                                    (WSGIHTTPException,))
        self.message_builder = registry.queryUtility(IExceptionMessageBuilder)
        self.exc_logger = registry.queryUtility(IExceptionLogger)
        self.response_renderer = registry.queryUtility(IExceptionMessageRenderer)

    def __call__(self, request):
        # getLogger injected for testing purposes
        try:
            return self.handler(request)
        except self.ignored:
            raise
        except:
            exc_info, message = self.message_builder(request)
            self.exc_logger(exc_info, message)
            if self.response_renderer:
                return self.response_renderer(request, exc_info, message)
            return HTTPInternalServerError()

    def filter_environ(self, environ):
        return dict([(e, v) for e, v in environ.items() if e in self.includes])



