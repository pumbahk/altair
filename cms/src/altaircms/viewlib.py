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
    
def get_endpoint(request): #maybe
    if "endpoint" in request.GET:
        return request.GET["endpoint"]
    logger.warn("invalid endpoint: url={r.url} referrer={r.referrer}".format(r=request))
    return "/"

def download_response(path, request=None, filename=None, **kwargs):
    filename = filename or path
    response = FileResponse(path=path, request=request, **kwargs)
    response.content_disposition = 'attachment; filename="{0}"'.format(filename)
    return response
