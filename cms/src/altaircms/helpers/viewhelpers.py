# -*- coding:utf-8 -*-

import logging
from functools import wraps
logger = logging.getLogger(__name__)

from altaircms.viewlib import FlashMessage
from altaircms.viewlib import get_endpoint

__all__ = ["FlashMessage", 
           "get_endpoint", 
           "RegisterViewPredicate", 
           ""]
class RegisterViewPredicate(object):
    """ input -> confirm -> execute形式のviewのためのcustom predicate
    """
    @classmethod
    def confirm(cls, context, request):
        return request.POST.get("stage") == "confirm"

    @classmethod
    def execute(cls, context, request):
        return request.POST.get("stage") == "execute"


def with_exception_logging(fn):
    @wraps(fn)
    def wrapped(context, request):
        try:
            return fn(context, request)
        except Exception as e:
            logger.exception(e)
            raise
    return wrapped
