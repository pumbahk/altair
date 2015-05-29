# -*- coding:utf-8 -*-
import sys
import logging
import transaction
from zope.interface import implementer
from datetime import datetime
from sqlalchemy.orm.util import _is_mapped_class
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.orders.models import Order
from .exceptions import PaymentDeliveryMethodPairNotFound
from .interfaces import IPayment, IPaymentCart

logger = logging.getLogger(__name__)

@implementer(IPayment)
class Payment(object):
    """ 決済
    """
    def __init__(self, cart, request, session=None, now=None, cancel_payment_on_failure=True):
        if now is None:
            now = datetime.now()
        self.request = request
        self.cart = cart
        self.sales_segment = cart.sales_segment
        self.session = session or DBSession
        self.now = now
        from .api import get_preparer, lookup_plugin
        self.get_preparer = get_preparer
        self.lookup_plugin = lookup_plugin
        self.cancel_payment_on_failure = cancel_payment_on_failure

    def _bind_order(self, order):
        order.organization_id = order.performance.event.organization_id
        order.browserid = self.request.browserid
        self.cart.order = order

    def _get_plugins(self, payment_delivery_pair):
        return self.lookup_plugin(self.request, payment_delivery_pair)

    def call_prepare(self):
        """ 決済方法前呼び出し
        """
        preparer = self.get_preparer(self.request, self.cart.payment_delivery_pair)
        if preparer is None:
            raise Exception
        res = preparer.prepare(self.request, self.cart)
        return res

    def call_delegator(self):
        """ 確認後決済フロー
        """
        preparer = self.get_preparer(self.request, self.cart.payment_delivery_pair)
        if preparer is None:
            raise Exception
        if hasattr(preparer, 'delegator'):
            return preparer.delegator(self.request, self.cart)
        return None

    def call_validate(self):
        """ 決済処理前の状態チェック
        """
        preparer = self.get_preparer(self.request, self.cart.payment_delivery_pair)
        if preparer is None:
            raise Exception
        if hasattr(preparer, 'validate'):
            return preparer.validate(self.request, self.cart)
        return None

    def call_payment(self):
        """ 決済処理
        """
        self.call_validate()

        payment_delivery_plugin, payment_plugin, delivery_plugin = self._get_plugins(self.cart.payment_delivery_pair)
        event_id = self.cart.performance.event_id

        if payment_delivery_plugin is not None:
            if IPaymentCart.providedBy(self.cart):
                order = payment_delivery_plugin.finish(self.request, self.cart)
                self._bind_order(order)
            else:
                payment_delivery_plugin.finish2(self.request, self.cart)
                order = self.cart
        else:
            # 決済と配送を別々に処理する
            if IPaymentCart.providedBy(self.cart):
                order = payment_plugin.finish(self.request, self.cart)
                self._bind_order(order)
                try:
                    delivery_plugin.finish(self.request, self.cart)
                except Exception as e:
                    exc_info = sys.exc_info()
                    order.deleted_at = self.now
                    if self.cancel_payment_on_failure:
                        payment_plugin.cancel(self.request, order)
                    raise exc_info[1], None, exc_info[2]
            else:
                logger.info('cart is not a IPaymentCart')
                payment_plugin.finish2(self.request, self.cart)
                order = self.cart
                delivery_plugin.finish2(self.request, self.cart)
        return order

    def call_payment2(self, order):
        payment_delivery_plugin, payment_plugin, delivery_plugin = self._get_plugins(self.cart.payment_delivery_pair)
        if payment_delivery_plugin is not None:
            payment_delivery_plugin.finish2(self.request, order)
        else:
            payment_plugin.finish2(self.request, order)
            try:
                delivery_plugin.finish2(self.request, self.cart)
            except Exception:
                exc_info = sys.exc_info()
                order.deleted_at = self.now
                if self.cancel_payment_on_failure:
                    payment_plugin.cancel(self.request, order)
                raise exc_info[1], None, exc_info[2]
        return order

    def call_delivery(self, order):
        payment_delivery_plugin, payment_plugin, delivery_plugin = self._get_plugins(self.cart.payment_delivery_pair)
        if delivery_plugin is not None:
            if IPaymentCart.providedBy(self.cart):
                self._bind_order(order)
                delivery_plugin.finish(self.request, self.cart)
            else:
                delivery_plugin.finish2(self.request, self.cart)
        else:
            logger.info(
                u'no delivery plugin for %s (plugin_id=%d)' % (
                    self.cart.payment_delivery_pair.delivery_method.name,
                    self.cart.payment_delivery_pair.delivery_method.delivery_plugin_id
                    )
                )
