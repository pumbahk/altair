import logging
logger = logging.getLogger(__file__)
import uamobile

def mobile_access_predicate(info, request):
    if not hasattr(request, "_ua"):
        request._ua = uamobile.detect(request.environ)
        logger.debug(request.environ.get("HTTP_USER_AGENT"))
    return not request._ua.is_nonmobile()
