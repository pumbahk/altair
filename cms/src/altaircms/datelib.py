from altair.now import get_now as original_get_now
from altair.now import get_today as original_get_today
from pyramid.threadlocal import get_current_request
import traceback 
import logging
logger = logging.getLogger(__name__)

def get_now(request=None):
    if request is None:
        logger.warn("get current request used. %s" % traceback.format_stack(limit=3))
        request = get_current_request()
    return original_get_now(request)

def get_today(request=None):
    if request is None:
        logger.warn("get current request used. %s" % traceback.format_stack(limit=3))
        request = get_current_request()
    return original_get_today(request)
