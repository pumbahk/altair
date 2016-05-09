# -*- coding:utf-8 -*-
from functools import wraps
import logging
logger = logging.getLogger(__name__)
from pyramid.response import FileResponse
from altaircms.auth.interfaces import IAPIKeyValidator #hmm

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

def download_response(path, request=None, filename=None, **kwargs):
    filename = filename or path
    response = FileResponse(path=path, request=request, **kwargs)
    response.content_disposition = 'attachment; filename="{0}"'.format(filename)
    return response

def failure_result(data={}, message=""):
    return {"status": "FAIL", "data": data, "message": message}

def success_result(data={}):
    return {"status": "OK",  "data": data}

def validate_apikey(request, apikey):
    reg = request.registry
    validator = reg.getAdapter(request, IAPIKeyValidator)
    return validator(apikey)

def apikey_required(tag="*api view condition*"):
    def wrapped(context, request):
        apikey = request.headers.get('X-Altair-Authorization', None)
        if apikey is None:
            logger.warn("{tag} apikey is not found: params={params}".format(tag=tag, params=request.POST))
            return False
        if not validate_apikey(request, apikey):
            logger.warn("{tag} invalid api key: {key}".format(tag=tag, key=apikey))
            return False
        return True
    return wrapped
