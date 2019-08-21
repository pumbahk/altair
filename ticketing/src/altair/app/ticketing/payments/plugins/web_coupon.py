# -*- coding:utf-8 -*-
"""WEBクーポン引取
"""
import re
import string

from altair.app.ticketing.cart.interfaces import ICartDelivery
from altair.app.ticketing.mails.interfaces import (
    ICompleteMailResource,
    IOrderCancelMailResource,
    ILotsAcceptedMailResource,
    ILotsElectedMailResource,
    ILotsRejectedMailResource,
)
from altair.app.ticketing.payments.interfaces import IDeliveryPlugin, IOrderDelivery
from altair.app.ticketing.utils import rand_string
from altair.pyramid_dynamic_renderer import lbr_view_config
from markupsafe import Markup
from pyramid.response import Response
from pyramid.view import view_defaults
from sqlalchemy.orm.exc import NoResultFound
from zope.interface import implementer
from . import WEB_COUPON_PLUGIN_ID as DELIVERY_PLUGIN_ID
from . import logger
from . import models as m
from .helpers import get_delivery_method_info

tag_re = re.compile(r"<[^>]*?>")


def includeme(config):
    config.add_delivery_plugin(WebCouponTicketDeliveryPlugin(), DELIVERY_PLUGIN_ID)
    config.scan(__name__)


def _overridable_delivery(path, fallback_ua_type=None):
    from . import _template
    return _template(path, type='overridable', for_='payments', plugin_type='delivery', plugin_id=DELIVERY_PLUGIN_ID, fallback_ua_type=fallback_ua_type)


@lbr_view_config(context=IOrderDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer=_overridable_delivery("web_coupon_completion.html"))
def reserved_number_viewlet(context, request):
    logger.debug(u"WEBクーポン")
    order = context.order
    logger.debug(u"order_no = %s" % order.order_no)
    reserved_number = m.ReservedNumber.query.filter_by(order_no=order.order_no).one()
    delivery_method = order.payment_delivery_pair.delivery_method
    delivery_name = get_delivery_method_info(request, delivery_method, 'name')
    description = get_delivery_method_info(request, delivery_method, 'description')
    return dict(reserved_number=reserved_number, delivery_name=delivery_name, description=Markup(description))


@lbr_view_config(context=ICartDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer=_overridable_delivery("web_coupon_confirm.html"))
def reserved_number_confirm_viewlet(context, request):
    logger.debug(u"WEBクーポン")
    cart = context.cart
    delivery_method = cart.payment_delivery_pair.delivery_method
    delivery_name = get_delivery_method_info(request, delivery_method, 'name')
    description = get_delivery_method_info(request, delivery_method, 'description')
    return dict(delivery_name=delivery_name, description=Markup(description))


@implementer(IDeliveryPlugin)
class WebCouponTicketDeliveryPlugin(object):
    """ WEBクーポン引き換え予約番号プラグイン"""

    def validate_order(self, request, order_like, update=False):
        """ なにかしたほうが良い?"""

    def validate_order_cancellation(self, request, order, now):
        """ キャンセルバリデーション """
        pass

    def prepare(self, request, cart):
        """ 前処理 なし"""

    def finish(self, request, cart):
        """ 確定処理 """
        self.finish2(request, cart)

    def finish2(self, request, order_like):
        while True:
            number = rand_string(string.digits, 10)
            existing_number = m.ReservedNumber.query.filter_by(number=number).first()
            if existing_number is None:
                reserved_number = m.ReservedNumber(order_no=order_like.order_no, number=number)
                break
        m.DBSession.add(reserved_number)
        logger.debug(u"WEBクーポン引き換え番号: %s" % reserved_number.number)

    def finished(self, request, order):
        """ 引換番号が発行されていること """
        reserved_number = m.DBSession.query(m.ReservedNumber).filter(
            m.ReservedNumber.order_no==order.order_no).first()
        return bool(reserved_number)

    def refresh(self, request, order):
        if order.delivered_at is not None:
            raise Exception('order %s is already delivered' % order.order_no)
        # 引換番号を再発行するべきだと思うけど...

    def cancel(self, request, order, now=None):
        # キャンセルフラグを立てるべきだと思うけど...
        pass

    def refund(self, request, order, refund_record):
        pass

    def get_order_info(self, request, order):
        try:
            reserved_number = m.DBSession.query(m.ReservedNumber).filter(
                m.ReservedNumber.order_no==order.order_no).one().number
        except NoResultFound:
            reserved_number = u''
        return {
            u'reserved_number': reserved_number,
            }


@view_defaults(context=ICompleteMailResource)
class CompletionMailViewlet(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @lbr_view_config(name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer=_overridable_delivery("web_coupon_mail_complete.html", fallback_ua_type='mail'))
    def delivery(self):
        """ 完了メール表示
        :param context: ICompleteMailDelivery
        """
        order = self.context.order
        delivery_method = order.payment_delivery_pair.delivery_method
        notice = self.context.mail_data("D", "notice")
        reserved_number = m.ReservedNumber.query.filter_by(order_no=self.context.order.order_no).first()
        description = ""
        if delivery_method.description is not None:
            description = tag_re.sub("", delivery_method.description)
        return dict(notice=notice, reserved_number=reserved_number, description=description)


@view_defaults(context=IOrderCancelMailResource)
class OrderCancelMailViewlet(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @lbr_view_config(name="delivery-%d" % DELIVERY_PLUGIN_ID)
    def delivery(self):
        """ cancelメール表示
        """
        return Response(self.context.mail_data("D", "notice"))


@lbr_view_config(context=ILotsElectedMailResource, name="delivery-%d" % DELIVERY_PLUGIN_ID)
@lbr_view_config(context=ILotsRejectedMailResource, name="delivery-%d" % DELIVERY_PLUGIN_ID)
@lbr_view_config(context=ILotsAcceptedMailResource, name="delivery-%d" % DELIVERY_PLUGIN_ID)
def lot_delivery_notice_viewlet(context, request):
    return Response(context.mail_data("D", "notice"))

