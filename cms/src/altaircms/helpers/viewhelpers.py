# -*- coding:utf-8 -*-

import logging
logger = logging.getLogger(__name__)

class RegisterViewPredicate(object):
    """ input -> confirm -> execute形式のviewのためのcustom predicate
    """
    @classmethod
    def confirm(cls, context, request):
        return request.POST.get("stage") == "confirm"

    @classmethod
    def execute(cls, context, request):
        return request.POST.get("stage") == "execute"

## endpoint
import logging
logger = logging.getLogger("altaircms.viewhelpers")

CMS_ENDPOINT = "cms:endpoint"
_CMS_ENDPOINT_SENTINEL =  "cms:endpoint:sentinel" #sentinel?
def set_endpoint(request, endpoint=None):
    session = request.session
    if session.get(_CMS_ENDPOINT_SENTINEL) != request.matched_route.name:
        session[_CMS_ENDPOINT_SENTINEL] = request.matched_route.name
        session[CMS_ENDPOINT] = endpoint or request.referrer
    logger.debug("matched route name")
    logger.debug(request.matched_route.name)
    logger.debug("session")
    logger.debug("sentinel: %s, endpoint: %s" % (session.get(_CMS_ENDPOINT_SENTINEL), session.get(CMS_ENDPOINT)))

def get_endpoint(request): #maybe
    session = request.session
    endpoint = session.get(CMS_ENDPOINT)
    if endpoint:
        del session[CMS_ENDPOINT]
    logger.debug("returned endpoint: %s" % endpoint)
    return endpoint


class FlashMessage(object):
    """ flashmessageのqueueをmethodで呼び分ける
    ここで追加されたメッセージは、altaircms:templates/parts/flashmessage.makoなどで使われる
    """
    @classmethod
    def _flash(cls, request, message, queue):
        if request:
            request.session.flash(message, queue)
        logger.info("flashmessage -- type:%s message:%s --" % (queue, message))

    @classmethod
    def success(cls, message, request=None):
        cls._flash(request, message, "successmessage")

    @classmethod
    def error(cls, message, request=None):
        cls._flash(request, message, "errormessage")

    @classmethod
    def info(cls, message, request=None):
        cls._flash(request, message, "infomessage")
