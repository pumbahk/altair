# encoding: utf-8

import logging
import transaction

from pyramid.threadlocal import get_current_request
from zope.interface import directlyProvides
from .interfaces import IGetCart
from .exceptions import PaymentDeliveryMethodPairNotFound
from .interfaces import IPaymentPreparerFactory, IPaymentPreparer, IPaymentDeliveryPlugin, IPaymentPlugin, IDeliveryPlugin

logger = logging.getLogger(__name__)


def is_finished_payment(request, pdmp, order):
    if order is None:
        return False
    request.altair_checkout3d_override_shop_name = order.organization.setting.multicheckout_shop_name
    plugin = get_payment_plugin(request, pdmp.payment_method.payment_plugin_id)
    return plugin.finished(request, order)

def is_finished_delivery(request, pdmp, order):
    if order is None:
        return False
    request.altair_checkout3d_override_shop_name = order.organization.setting.multicheckout_shop_name
    plugin = get_delivery_plugin(request, pdmp.delivery_method.delivery_plugin_id)
    return plugin.finished(request, order)

def get_cart(request):
    getter = request.registry.getUtility(IGetCart)
    return getter(request)

def get_delivery_plugin(request, plugin_id):
    registry = request.registry
    return registry.utilities.lookup([], IDeliveryPlugin, name="delivery-%s" % plugin_id)

def get_payment_plugin(request, plugin_id):
    logger.debug("get_payment_plugin: %s" % plugin_id)
    registry = request.registry
    return registry.utilities.lookup([], IPaymentPlugin, name="payment-%s" % plugin_id)

def get_payment_delivery_plugin(request, payment_plugin_id, delivery_plugin_id):
    registry = request.registry
    return registry.utilities.lookup([], IPaymentDeliveryPlugin, 
        "payment-%s:delivery-%s" % (payment_plugin_id, delivery_plugin_id))

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

def lookup_plugin(request, payment_delivery_pair):
    assert payment_delivery_pair is not None
    payment_delivery_plugin = get_payment_delivery_plugin(request,
        payment_delivery_pair.payment_method.payment_plugin_id,
        payment_delivery_pair.delivery_method.delivery_plugin_id,)
    payment_plugin = get_payment_plugin(request, payment_delivery_pair.payment_method.payment_plugin_id)
    delivery_plugin = get_delivery_plugin(request, payment_delivery_pair.delivery_method.delivery_plugin_id)
    if payment_delivery_plugin is None and \
       (payment_plugin is None or delivery_plugin is None):
        raise PaymentDeliveryMethodPairNotFound(u"対応する決済プラグインか配送プラグインが見つかりませんでした")
    return payment_delivery_plugin, payment_plugin, delivery_plugin

def refresh_order(session, order):
    request = get_current_request()
    session.add(order)
    logger.info('Trying to refresh order %s (id=%d, payment_delivery_pair={ payment_method=%s, delivery_method=%s })...'
                        % (order.order_no, order.id, order.payment_delivery_pair.payment_method.name, order.payment_delivery_pair.delivery_method.name))
    os = order.organization.setting
    request.altair_checkout3d_override_shop_name = os.multicheckout_shop_name
    payment_delivery_plugin, payment_plugin, delivery_plugin = lookup_plugin(request, order.payment_delivery_pair)
    if payment_delivery_plugin is not None:
        logger.info('payment_delivery_plugin.refresh')
        payment_delivery_plugin.refresh(request, order)
        transaction.commit()
    else:
        logger.info('payment_plugin.refresh')
        payment_plugin.refresh(request, order)
        transaction.commit()
        session.add(order)
        logger.info('delivery_plugin.refresh')
        delivery_plugin.refresh(request, order)
        transaction.commit()
    session.add(order)
    logger.info('Finished refreshing order %s (id=%d)' % (order.order_no, order.id))
