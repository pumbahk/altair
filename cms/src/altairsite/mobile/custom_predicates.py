import logging
logger = logging.getLogger(__file__)
import uamobile

def mobile_access_predicate(info, request):
    ua = uamobile.detect(request.environ)
    logger.debug(request.environ.get("HTTP_USER_AGENT"))
    return not ua.is_nonmobile()
