# encoding: utf-8

import logging
import transaction

from zope.interface import directlyProvides
from pyramid.interfaces import IRequest
from zope.deprecation import deprecation

from .interfaces import ICartInterface
from .exceptions import PaymentDeliveryMethodPairNotFound, PaymentCartNotAvailable
from .interfaces import IPaymentPreparerFactory, IPaymentPreparer, IPaymentDeliveryPlugin, IPaymentPlugin, IDeliveryPlugin
from .directives import Discriminator

logger = logging.getLogger(__name__)

OBSOLETED_SUCCESS_URL_KEY = 'payment_confirm_url'

@deprecation.deprecate("this method should be removed after the code gets released")
def set_confirm_url(request, url):
    request.session[OBSOLETED_SUCCESS_URL_KEY] = url

def is_finished_payment(request, pdmp, order):
    if order is None:
        return False
    plugin = get_payment_plugin(request, pdmp.payment_method.payment_plugin_id)
    return plugin.finished(request, order)

def is_finished_delivery(request, pdmp, order):
    if order is None:
        return False
    plugin = get_delivery_plugin(request, pdmp.delivery_method.delivery_plugin_id)
    return plugin.finished(request, order)

def get_cart(request, retrieve_invalidated=False):
    cart_if = request.registry.getUtility(ICartInterface)
    cart = cart_if.get_cart(request, retrieve_invalidated=retrieve_invalidated)
    if cart is None:
        raise PaymentCartNotAvailable(u'cart is not available')
    if cart.payment_delivery_pair is None:
        raise PaymentDeliveryMethodPairNotFound(u'payment/delivery method not specified')
    return cart

def get_cart_by_order_no(request, order_no, retrieve_invalidated=False):
    cart_if = request.registry.getUtility(ICartInterface)
    return cart_if.get_cart_by_order_no(request, order_no, retrieve_invalidated=retrieve_invalidated)

def make_order_from_cart(request, cart):
    cart_if = request.registry.getUtility(ICartInterface)
    return cart_if.make_order_from_cart(request, cart)

def cont_complete_view(context, request, order_no, magazine_ids):
    cart_if = request.registry.getUtility(ICartInterface)
    return cart_if.cont_complete_view(context, request, order_no, magazine_ids)

def get_confirm_url(request):
    cart_if = request.registry.getUtility(ICartInterface)
    return cart_if.get_success_url(request)

def get_delivery_plugin(request_or_registry, plugin_id):
    if IRequest.providedBy(request_or_registry):
        registry = request_or_registry.registry
    else:
        registry = request_or_registry
    key = str(Discriminator(None, plugin_id))
    return registry.utilities.lookup([], IDeliveryPlugin, name=key)

def get_payment_plugin(request_or_registry, plugin_id):
    if IRequest.providedBy(request_or_registry):
        registry = request_or_registry.registry
    else:
        registry = request_or_registry
    key = str(Discriminator(plugin_id, None))
    return registry.utilities.lookup([], IPaymentPlugin, name=key)

def get_payment_delivery_plugin(request_or_registry, payment_plugin_id, delivery_plugin_id):
    if IRequest.providedBy(request_or_registry):
        registry = request_or_registry.registry
    else:
        registry = request_or_registry
    key = str(Discriminator(payment_plugin_id, delivery_plugin_id))
    return registry.utilities.lookup([], IPaymentDeliveryPlugin, key)

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
