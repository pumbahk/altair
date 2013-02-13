# -*- coding:utf-8 -*-
import logging
import transaction
from zope.interface import directlyProvides
from ticketing.models import DBSession
from ticketing.cart.exceptions import DeliveryFailedException
from ticketing.core.models import Order
from .interfaces import IPaymentPreparerFactory, IPaymentPreparer, IPaymentDeliveryPlugin, IPaymentPlugin, IDeliveryPlugin
from .exceptions import PaymentDeliveryMethodPairNotFound

logger = logging.getLogger(__name__)

# TODO: apiに移動
def get_delivery_plugin(request, plugin_id):
    registry = request.registry
    return registry.utilities.lookup([], IDeliveryPlugin, name="delivery-%s" % plugin_id)

# TODO: apiに移動
def get_payment_plugin(request, plugin_id):
    logger.debug("get_payment_plugin: %s" % plugin_id)
    registry = request.registry
    return registry.utilities.lookup([], IPaymentPlugin, name="payment-%s" % plugin_id)

# TODO: apiに移動
def get_payment_delivery_plugin(request, payment_plugin_id, delivery_plugin_id):
    registry = request.registry
    return registry.utilities.lookup([], IPaymentDeliveryPlugin, 
        "payment-%s:delivery-%s" % (payment_plugin_id, delivery_plugin_id))

# TODO: apiに移動
def get_preparer(request, payment_delivery_pair):
    if payment_delivery_pair is None:
        raise PaymentDeliveryMethodPairNotFound
    payment_delivery_plugin = get_payment_delivery_plugin(request, 
        payment_delivery_pair.payment_method.payment_plugin_id,
        payment_delivery_pair.delivery_method.delivery_plugin_id,)

    if payment_delivery_plugin is not None:
        directlyProvides(payment_delivery_plugin, IPaymentPreparer)
        return payment_delivery_plugin
    else:
        payment_plugin = get_payment_plugin(request, payment_delivery_pair.payment_method.payment_plugin_id)
        if payment_plugin is not None:
            directlyProvides(payment_plugin, IPaymentPreparer)
            return payment_plugin

directlyProvides(get_preparer, IPaymentPreparerFactory)

class Payment(object):
    """ 決済
    """
    get_preparer = get_preparer

    def __init__(self, cart, request):
        self.request = request
        self.cart = cart
        self.sales_segment = cart.sales_segment

    def get_payment_delivery_methods(self):
        """ via PaymentView
        """

    def select_payment(self, payment_delivery_pair, shipping_address):
        """ 決済・引取方法選択 via PaymentView
        """
        cart.payment_delivery_pair = payment_delivery_pair
        cart.system_fee = payment_delivery_pair.system_fee
        cart.shipping_address = shipping_address
        order = dict(
            client_name=client_name,
            payment_delivery_method_pair_id=payment_delivery_method_pair_id,
            mail_address=shipping_address.email,
        )
        self.request.session['order'] = order

    def call_prepare(self):
        """ 決済方法前呼び出し
        """
        preparer = get_preparer(self.request, self.cart.payment_delivery_pair)
        if preparer is None:
            raise Exception
        res = preparer.prepare(self.request, self.cart)
        return res

    def call_delegator(self):
        preparer = get_preparer(self.request, self.cart.payment_delivery_pair)
        if preparer is None:
            raise Exception
        if hasattr(preparer, 'delegator'):
            return preparer.delegator(self.request, self.cart)
        return None

    def _bind_order(self, order, user):
        order.user = user
        order.organization_id = order.performance.event.organization_id
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
        payment_delivery_plugin = get_payment_delivery_plugin(self.request, 
            payment_delivery_pair.payment_method.payment_plugin_id,
            payment_delivery_pair.delivery_method.delivery_plugin_id,)
        payment_plugin = get_payment_plugin(self.request, payment_delivery_pair.payment_method.payment_plugin_id)
        delivery_plugin = get_delivery_plugin(self.request, payment_delivery_pair.delivery_method.delivery_plugin_id)
        return payment_delivery_plugin, payment_plugin, delivery_plugin

    def get_or_create_user(self):
        pass

    def call_payment(self):
        """ 決済処理
        """

        payment_delivery_plugin, payment_plugin, delivery_plugin = self.get_plugins(self.cart.payment_delivery_pair)
        event_id = self.cart.performance.event_id
        user = self.get_or_create_user()

        if payment_delivery_plugin is not None:
            order = self.call_payment_delivery(payment_delivery_plugin)
        elif payment_plugin and delivery_plugin:
            # 決済と配送を別々に処理する
            order = self.call_payment_plugin(payment_plugin)
            self.cart.order = order
            order_no = order.order_no
            try:
                delivery_plugin.finish(self.request, self.cart)
            except Exception as e:
                on_delivery_error(e, self.request, order)
                transaction.commit()
                raise DeliveryFailedException(order_no, event_id)
        else:
            raise Exception(u"対応する決済プラグインか配送プラグインが見つかりませんでした") # TODO 例外クラス作成

        self._bind_order(order, user)
        order_no = order.order_no
        # 注文確定として、他の処理でロールバックされないようにコミット
        transaction.commit()
        # デタッチされてしまうので再度取得
        order = DBSession.query(Order).filter(Order.order_no==order_no).one()
        return order


def on_delivery_error(e, request, order):
    import sys
    import traceback
    import StringIO
    exc_info = sys.exc_info()
    out = StringIO.StringIO()
    traceback.print_exception(*exc_info, file=out)
    logger.error(out.getvalue())

    order.cancel(request)
    order.note = str(e)
    #order_no = order.order_no
    #event_id = cart.sales_segment.event_id
