# encoding: utf-8

import logging
import transaction

from zope.interface import directlyProvides
from .interfaces import ICartInterface
from .exceptions import PaymentDeliveryMethodPairNotFound
from .interfaces import IPaymentPreparerFactory, IPaymentPreparer, IPaymentDeliveryPlugin, IPaymentPlugin, IDeliveryPlugin
from zope.deprecation import deprecation

logger = logging.getLogger(__name__)

OBSOLETED_SUCCESS_URL_KEY = 'payment_confirm_url'

@deprecation.deprecate("this method should be removed after the code gets released")
def set_confirm_url(request, url):
    request.session[OBSOLETED_SUCCESS_URL_KEY] = url

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
    cart_if = request.registry.getUtility(ICartInterface)
    return cart_if.get_cart(request)

def get_confirm_url(request):
    cart_if = request.registry.getUtility(ICartInterface)
    return cart_if.get_success_url(request)

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
