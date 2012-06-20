# -*- coding:utf-8 -*-
import hashlib

from pyramid.view import view_config
from pyramid.response import Response
import sqlahelper
import sqlalchemy as sa
import logging
from zope.interface import Interface, implementer

class IOrderDelivery(Interface):
    pass

@implementer(IOrderDelivery)
class OrderDelivery(object):
    def __init__(self, order):
        self.order = order

logger = logging.getLogger(__name__)
Base = sqlahelper.get_base()
DBSession = sqlahelper.get_session()

class ReservedNumber(Base):
    __tablename__ = "reserved_number"
    query = DBSession.query_property()
    id = sa.Column(sa.Integer, primary_key=True)
    order_no = sa.Column(sa.Unicode(255), unique=True)
    number = sa.Column(sa.Unicode(32))

def create_reserved_number(request, cart):
    """ 引き換え番号生成
    """

    number = hashlib.md5(str(cart.id)).hexdigest()
    reserved_number = ReservedNumber(order_no=cart.id, number=number)
    DBSession.add(reserved_number)
    return number


@view_config(context=IOrderDelivery, name="delivery-2")
def reserved_number_viewlet(context, request):
    logger.debug(u"窓口")
    order = context.order
    reserved_number = ReservedNumber.query.filter_by(order_no=order.id).one()
    return Response(text =u"引き換え番号: %s" % reserved_number.number)

@view_config(context=IOrderDelivery, name="delivery-3")
def deliver_viewlet(context, request):
    logger.debug(u"郵送")
    order = context.order
    return Response(text = u"郵送: %s" % order.shipping_address.address_1)

def includeme(config):
    config.scan(".")
