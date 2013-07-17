from .interfaces import IExceptionMessageBuilder, IExceptionMessageRenderer, IExceptionLogger
from pyramid.httpexceptions import HTTPInternalServerError

def build_exception_message(request):
    message_builder = request.registry.queryUtility(IExceptionMessageBuilder)
    if message_builder:
        return message_builder(request)
    else:
        return None

def render_exception_message(request, exc_info, message):
    message_renderer = request.registry.queryUtility(IExceptionMessageRenderer)
    if message_renderer:
        return message_renderer(request, exc_info, message)
    else:
        return HTTPInternalServerError()

def log_exception_message(request, exc_info, message):
    logger = request.registry.queryUtility(IExceptionLogger)
    if logger:
        logger(exc_info, message)
