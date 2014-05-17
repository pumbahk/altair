# -*- coding:utf-8 -*-
import logging
import transaction
from zope.interface import implementer 
from sqlalchemy.orm.util import _is_mapped_class
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.orders.models import Order
from .events import DeliveryErrorEvent
from .exceptions import PaymentDeliveryMethodPairNotFound
from .interfaces import IPayment, IPaymentCart

logger = logging.getLogger(__name__)

@implementer(IPayment)
class Payment(object):
    """ 決済
    """
    def __init__(self, cart, request, session=None):
        self.request = request
        self.cart = cart
        self.sales_segment = cart.sales_segment
        self.session = session or DBSession
        from .api import get_preparer, lookup_plugin
        self.get_preparer = get_preparer
        self.lookup_plugin = lookup_plugin

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
                self.session.add(order)
                self._bind_order(order)
                # 注文確定として、他の処理でロールバックされないようにコミット
                transaction.commit()
                if _is_mapped_class(self.cart.__class__):
                    self.session.add(self.cart)
                self.session.add(order)
            else:
                payment_delivery_plugin.finish2(self.request, self.cart)
                order = self.cart
        else:
            # 決済と配送を別々に処理する            
            if IPaymentCart.providedBy(self.cart):
                order = payment_plugin.finish(self.request, self.cart)
                self.session.add(order)
                self._bind_order(order)
                # 注文確定として、他の処理でロールバックされないようにコミット
                transaction.commit()
                if _is_mapped_class(self.cart.__class__):
                    self.session.add(self.cart)
                try:
                    delivery_plugin.finish(self.request, self.cart)
                except Exception as e:
                    self.session.add(order)
                    self.request.registry.notify(DeliveryErrorEvent(e, self.request, order))
                    raise
                transaction.commit()
                # transaction.commit() で order がデタッチされるので再度アタッチ
                self.session.add(self.cart)
                self.session.add(order)
            else:
                logger.info('cart is not a IPaymentCart')
                payment_plugin.finish2(self.request, self.cart)
                order = self.cart
                try:
                    delivery_plugin.finish2(self.request, self.cart)
                except Exception as e:
                    self.request.registry.notify(DeliveryErrorEvent(e, self.request, order))
                    raise
        return order

    def call_payment2(self, order):
        payment_delivery_plugin, payment_plugin, delivery_plugin = self._get_plugins(self.cart.payment_delivery_pair)
        if payment_delivery_plugin is not None:
            payment_delivery_plugin.finish2(self.request, order)
        else:
            payment_plugin.finish2(self.request, order)
            try:
                delivery_plugin.finish2(self.request, self.cart)
            except Exception as e:
                self.request.registry.notify(DeliveryErrorEvent(e, self.request, order))
                raise
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
