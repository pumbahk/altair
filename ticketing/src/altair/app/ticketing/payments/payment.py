# -*- coding:utf-8 -*-
import logging
import transaction
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.core.models import Order
from .api import (
    get_payment_delivery_plugin, 
    get_preparer, 
    get_payment_plugin, 
    get_delivery_plugin,
)
from .events import DeliveryErrorEvent
from .exceptions import PaymentDeliveryMethodPairNotFound

logger = logging.getLogger(__name__)


class Payment(object):
    """ 決済
    """
    get_preparer = get_preparer

    def __init__(self, cart, request):
        self.request = request
        self.cart = cart
        self.sales_segment = cart.sales_segment

    def call_prepare(self):
        """ 決済方法前呼び出し
        """
        preparer = get_preparer(self.request, self.cart.payment_delivery_pair)
        if preparer is None:
            raise Exception
        res = preparer.prepare(self.request, self.cart)
        return res

    def call_delegator(self):
        """ 確認後決済フロー
        """
        preparer = get_preparer(self.request, self.cart.payment_delivery_pair)
        if preparer is None:
            raise Exception
        if hasattr(preparer, 'delegator'):
            return preparer.delegator(self.request, self.cart)
        return None

    def _bind_order(self, order):
        order.organization_id = order.performance.event.organization_id
        order.browserid = self.request.browserid
        self.cart.order = order

    def call_payment_delivery(self, payment_delivery_plugin):
        # 決済配送を両方一度に処理する
        order = payment_delivery_plugin.finish(self.request, self.cart)
        DBSession.add(order)
        return order

    def call_payment_plugin(self, payment_plugin):
        order = payment_plugin.finish(self.request, self.cart)
        DBSession.add(order)
        return order

    def get_plugins(self, payment_delivery_pair):
        assert payment_delivery_pair is not None
        payment_delivery_plugin = get_payment_delivery_plugin(self.request,
            payment_delivery_pair.payment_method.payment_plugin_id,
            payment_delivery_pair.delivery_method.delivery_plugin_id,)
        payment_plugin = get_payment_plugin(self.request, payment_delivery_pair.payment_method.payment_plugin_id)
        delivery_plugin = get_delivery_plugin(self.request, payment_delivery_pair.delivery_method.delivery_plugin_id)
        if payment_delivery_plugin is None and \
           (payment_plugin is None or delivery_plugin is None):
            raise PaymentDeliveryMethodPairNotFound(u"対応する決済プラグインか配送プラグインが見つかりませんでした")
        return payment_delivery_plugin, payment_plugin, delivery_plugin

    def call_validate(self):
        """ 決済処理前の状態チェック
        """
        preparer = get_preparer(self.request, self.cart.payment_delivery_pair)
        if preparer is None:
            raise Exception
        if hasattr(preparer, 'validate'):
            return preparer.validate(self.request, self.cart)
        return None

    def call_payment(self):
        """ 決済処理
        """
        self.call_validate()

        payment_delivery_plugin, payment_plugin, delivery_plugin = self.get_plugins(self.cart.payment_delivery_pair)
        event_id = self.cart.performance.event_id
        
        if payment_delivery_plugin is not None:
            order = self.call_payment_delivery(payment_delivery_plugin)
            self._bind_order(order)
            # 注文確定として、他の処理でロールバックされないようにコミット
            transaction.commit()
        else:
            # 決済と配送を別々に処理する            
            order = self.call_payment_plugin(payment_plugin)
            self._bind_order(order)
            # 注文確定として、他の処理でロールバックされないようにコミット
            transaction.commit()
            try:
                delivery_plugin.finish(self.request, self.cart)
            except Exception as e:
                self.request.registry.notify(DeliveryErrorEvent(e, self.request, order))
                raise
        # transaction.commit() で order がデタッチされるので再度アタッチ
        DBSession.add(order)
        return order

    def call_delivery(self, order):
        payment_delivery_plugin, payment_plugin, delivery_plugin = self.get_plugins(self.cart.payment_delivery_pair)
        self.cart.order = order
        delivery_plugin.finish(self.request, self.cart)
