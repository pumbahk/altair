# -*- coding:utf-8 -*-
import re
import logging
from zope.interface import directlyProvides
from .interfaces import IMobileRequest, ISmartphoneRequest
from pyramid.response import Response
from .api import detect, get_middleware

logger = logging.getLogger(__name__)

def mobile_encoding_convert_factory(handler, registry):
    middleware = get_middleware(registry)
    def tween(request):
        return middleware(handler, request)
    return tween
