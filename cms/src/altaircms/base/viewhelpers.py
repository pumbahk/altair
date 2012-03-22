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

class FlashMessage(object):
    """ flashmessageのqueueをmethodで呼び分ける
    ここで追加されたメッセージは、altaircms:templates/parts/flashmessage.makoなどで使われる
    """
    @classmethod
    def _flash(cls, request, message, queue):
        if request:
            request.session.flash(message, queue)
        logger.info("flashmessage type:%s message:%s" % (queue, message))

    @classmethod
    def success(cls, message, request=None):
        cls._flash(request, message, "successmessage")

    @classmethod
    def error(cls, message, request=None):
        cls._flash(request, message, "errormessage")

    @classmethod
    def info(cls, message, request=None):
        cls._flash(request, message, "infomessage")
