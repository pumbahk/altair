# -*- coding:utf-8 -*-
from .interfaces import ISVGBuilder
from . import VISIBLE_TICKETFORMAT_SESSION_KEY
from datetime import datetime

def get_svg_builder(request):
    return request.registry.getUtility(ISVGBuilder)

def set_visible_ticketformat(request):
    request.session[VISIBLE_TICKETFORMAT_SESSION_KEY] = str(datetime.now())

def set_invisible_ticketformat(request):
    if VISIBLE_TICKETFORMAT_SESSION_KEY in request.session:
        del request.session[VISIBLE_TICKETFORMAT_SESSION_KEY]
