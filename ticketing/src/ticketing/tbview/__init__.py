import sys
import traceback
import StringIO
from pyramid.view import render_view_to_response
from pyramid.tweens import INGRESS

def includeme(config):
    config.add_view(tb_view,
        context=ExceptionWrapper,
        renderer="string")
    config.add_tween(__name__ + '.tbview_tween_factory',
        under=INGRESS)

class ExceptionWrapper(object):
    def __init__(self, exc_type, exc_value, exc_traceback):
        self.exc_type = exc_type
        self.exc_value = exc_value
        self.exc_traceback = exc_traceback

def tb_view(context, request):
    out = StringIO.StringIO()
    traceback.print_exception(context.exc_type, context.exc_value, context.exc_traceback, file=out)
    return out.getvalue()

def tbview_tween_factory(handler, registry):
    def tween(request):
        try:
            return handler(request)
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            wrapper = ExceptionWrapper(exc_type, exc_value, exc_traceback)
            return render_view_to_response(wrapper, request)
    return tween
