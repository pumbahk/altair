import traceback
import StringIO

from zope.interface import implementer

from pyramid.response import Response
from pyramid.httpexceptions import HTTPInternalServerError

from .interfaces import IExceptionMessageRendererFactory

@implementer(IExceptionMessageRendererFactory)
class BasicExceptionMessageRenderer(object):
    def __init__(self, show_traceback):
        self.show_traceback = show_traceback

    def __call__(self, request, exc_info, message):
        if self.show_traceback:
            out = StringIO.StringIO()
            out.write(message + "\n")
            traceback.print_exception(*exc_info, file=out)
            return Response(out.getvalue(), status=500, content_type='text/plain')
        else:
            return HTTPInternalServerError()

