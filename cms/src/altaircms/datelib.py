from altair.now import get_now as _get_now
from altair.now import get_today as _get_today
from altair.now import has_session_key as _has_session_key
from altair.now import set_now as _set_now
from pyramid.threadlocal import get_current_request
import traceback 
import logging
logger = logging.getLogger(__name__)

has_session_key = _has_session_key
set_now = _set_now

def get_now(request=None):
    if request is None:
        logger.warn("get current request used. %s", traceback.format_stack(limit=3))
        request = get_current_request()
    if hasattr(request, "_now"):
        return request._now
    now = request._now = _get_now(request)
    return now

def get_today(request=None):
    if request is None:
        logger.warn("get current request used. %s", traceback.format_stack(limit=3))
        request = get_current_request()
    return _get_today(request)
