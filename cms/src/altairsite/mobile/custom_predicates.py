import logging
logger = logging.getLogger(__file__)
from altair.mobile.api import detect

def mobile_access_predicate(info, request):
    if not hasattr(request, "mobile_ua"):
        request.mobile_ua = detect(request)
        logger.debug(request.environ.get("HTTP_USER_AGENT"))
    return not request.mobile_ua.carrier.is_nonmobile

