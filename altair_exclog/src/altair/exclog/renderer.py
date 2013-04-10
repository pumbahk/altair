import traceback
import StringIO

from zope.interface import implementer

from pyramid.response import Response

from .interfaces import IExceptionMessageRendererFactory

@implementer(IExceptionMessageRendererFactory)
class BasicExceptionMessageRenderer(object):
    def __init__(self):
        pass

    def __call__(self, request, exc_info, message):
        out = StringIO.StringIO()
        out.write(message + "\n")
        traceback.print_exception(*exc_info, file=out)
        return Response(out.getvalue(), status=500, content_type='text/plain')

