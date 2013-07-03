# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from pyramid.response import FileResponse

class BaseView(object):
    """simplest class view object"""
    def __init__(self, context, request):
        self.request = request
        self.context = context


class FlashMessage(object):
    """ flashmessageのqueueをmethodで呼び分ける
    ここで追加されたメッセージは、altaircms:templates/parts/flashmessage.htmlなどで使われる
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

## todo: remove endpoint session.!!!
CMS_ENDPOINT = "cms:endpoint"
_CMS_ENDPOINT_SENTINEL =  "cms:endpoint:sentinel" #sentinel?
def set_endpoint(request, endpoint=None):
    session = request.session
    logger.debug(session.get(_CMS_ENDPOINT_SENTINEL) != request.matched_route.name)
    if session.get(_CMS_ENDPOINT_SENTINEL) != request.matched_route.name:
        session[_CMS_ENDPOINT_SENTINEL] = request.matched_route.name
        session[CMS_ENDPOINT] = endpoint or request.referrer
    logger.debug("matched route name")
    logger.debug(request.matched_route.name)
    logger.debug("session")
    logger.debug("sentinel: %s, endpoint: %s, referer: %s" % (session.get(_CMS_ENDPOINT_SENTINEL), session.get(CMS_ENDPOINT), endpoint or request.referrer))
    
def get_endpoint(request): #maybe
    if "endpoint" in request.GET:
        return request.GET["endpoint"]
    session = request.session
    endpoint = request.get("endpoint") or session.get(CMS_ENDPOINT)
    if endpoint and CMS_ENDPOINT in session:
        del session[CMS_ENDPOINT]
    session[_CMS_ENDPOINT_SENTINEL] = None #sentinel?
    logger.debug("sentinel: %s, endpoint: %s, referer: %s" % (session.get(_CMS_ENDPOINT_SENTINEL), session.get(CMS_ENDPOINT), request.referrer))
    return endpoint

def download_response(path, request=None, filename=None, **kwargs):
    filename = filename or path
    response = FileResponse(path=path, request=request, **kwargs)
    response.content_disposition = 'attachment; filename="{0}"'.format(filename)
    return response
