import sys
from pyramid import renderers
import logging
logger = logging.getLogger(__name__)
import traceback

def render(template, value, request=None, limit=100):
    try:
        return renderers.render(template, value, request=request)
    except Exception as e:
        etype, value, tb = sys.exc_info()
        # logger.exception(str(e))
        return u''.join(s.decode("utf-8", errors="replace") for s in traceback.format_exception(etype, value, tb, limit))

