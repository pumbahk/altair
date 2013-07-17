# -*- coding:utf-8 -*-
import logging
from pyramid.httpexceptions import HTTPFound
import transaction
logger = logging.getLogger(__name__)
from altair.app.ticketing.cart import api as cart_api

def exception_view(context, request):
    logger.error("The error was: %s" % context, exc_info=request.exc_info)
    return dict()

def notfound_view(context, request):
    #logger.error("The error was: %s" % context, exc_info=request.exc_info)
    return dict()
def forbidden_view(context, request):
    #logger.error("The error was: %s" % context, exc_info=request.exc_info)
    return dict()

def cart_creation_exception(context, request):
    if context.back_url is not None:
        # カートの救済可能な場合
        cart_api.recover_cart(request) 
        transaction.commit()
        return HTTPFound(location=context.back_url)

    # #以下のコードはまったく動かない
    # else:
    #     # カートの救済不可能
    #     if cart is not None:
    #         location = request.route_url('cart.index', event_id=cart.performance.event_id)
    #     else:
    #         location = request.context.host_base_url
    # return dict(message=Markup(u'決済中にエラーが発生しました。しばらく時間を置いてから<a href="%s">再度お試しください。</a>' % location))

class OutTermSalesView(object):
    def __init__(self, context, request):
        self.request = request
        self.context = context

    def pc(self):
        if self.context.next is None:
            datum = self.context.last
            which = 'last'
        else:
            datum = self.context.next
            which = 'next'
        return dict(which=which, **datum)

    def mobile(self):
        if self.context.next is None:
            datum = self.context.last
            which = 'last'
        else:
            datum = self.context.next
            which = 'next'
        return dict(which=which, **datum)

