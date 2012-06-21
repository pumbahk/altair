# -*- coding:utf-8 -*-
import hashlib
from pyramid.view import view_config
from pyramid.response import Response
from zope.interface import implementer
from .interfaces import IDeliveryPlugin, IOrderDelivery, ICartDelivery
from . import models as m

PLUGIN_ID = 3
def includeme(config):
    config.add_delivery_plugin(ReservedNumberPlugin(), PLUGIN_ID)
    config.scan(__name__)

@view_config(context=IOrderDelivery, name="delivery-%d" % PLUGIN_ID)
def reserved_number_viewlet(context, request):
    logger.debug(u"窓口")
    order = context.order
    reserved_number = m.ReservedNumber.query.filter_by(order_no=order.id).one()
    return Response(text =u"引き換え番号: %s" % reserved_number.number)

@view_config(context=ICartDelivery, name="delivery-%d" % PLUGIN_ID)
def reserved_number_viewlet(context, request):
    logger.debug(u"窓口")
    return Response(text =u"窓口引き換え")

@implementer(IDeliveryPlugin)
class ReservedNumberPlugin(object):
    """ 窓口引き換え予約番号プラグイン"""
    def prepare(self, request, cart):
        """ 前処理 なし"""

    def finish(self, request, cart):
        """ 確定処理 """
        number = hashlib.md5(str(cart.id)).hexdigest()
        reserved_number = m.ReservedNumber(order_no=cart.id, number=number)
        m.DBSession.add(reserved_number)
