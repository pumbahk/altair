# -*- coding:utf-8 -*-
import logging
from .interfaces import IOrderDelivery, IOrderPayment
from .interfaces import ICartInterface
from .interfaces import IPaymentDeliveryPlugin
from .interfaces import IPaymentPlugin, IDeliveryPlugin
from .interfaces import IPaymentViewRendererLookup

logger = logging.getLogger(__name__)

PAYMENT_CONFIG = -5

class Discriminator(object):
    __slot__ = (
        'payment_plugin_id',
        'delivery_plugin_id',
        )

    def __init__(self, payment_plugin_id, delivery_plugin_id):
        self.payment_plugin_id = payment_plugin_id
        self.delivery_plugin_id = delivery_plugin_id
       
    def __eq__(self, that):
        if not isinstance(that, self.__class__):
            return False
        self_is_pd = self.payment_plugin_id is not None and self.delivery_plugin_id is not None
        that_is_pd = that.payment_plugin_id is not None and that.delivery_plugin_id is not None
        if self_is_pd ^ that_is_pd:
            return False
        elif self_is_pd:
            return self.payment_plugin_id == that.payment_plugin_id and self.delivery_plugin_id == that.delivery_plugin_id
        else:
            return (self.payment_plugin_id is not None and that.payment_plugin_id is not None and self.payment_plugin_id == that.payment_plugin_id) or \
                   (self.delivery_plugin_id is not None and that.delivery_plugin_id is not None and self.delivery_plugin_id == that.delivery_plugin_id)

    def __str__(self):
        retval = []
        if self.payment_plugin_id is not None:
            retval.append("payment-%d" % self.payment_plugin_id)
        if self.delivery_plugin_id is not None:
            retval.append("delivery-%d" % self.delivery_plugin_id)
        return ":".join(retval)

    def __repr__(self):
        return "Discriminator(%s, %s)" % (self.payment_plugin_id, self.delivery_plugin_id)

    def __hash__(self):
        return 1


def add_payment_delivery_plugin(config, plugin, payment_plugin_id, delivery_plugin_id):
    key = Discriminator(payment_plugin_id, delivery_plugin_id)
    def register():
        logger.info("add_payment_delivery_plugin: %r registered as %d:%d" % (plugin, payment_plugin_id, delivery_plugin_id))
        config.registry.utilities.register([], IPaymentDeliveryPlugin, str(key), plugin)
    intr = config.introspectable(
        "payment / delivery plugins", str(key),
        config.object_description(plugin),
        "payment_plugin_id=%d, delivery_plugin_id=%d" % (payment_plugin_id, delivery_plugin_id)
        )
    config.action(key, register, introspectables=[intr], order=PAYMENT_CONFIG)


def add_payment_plugin(config, plugin, plugin_id):
    """ プラグイン登録 
    :param plugin: an instance of IPaymentPlugin 
    """
    key = Discriminator(plugin_id, None)
    def register():
        logger.info("add_payment_plugin: %r registered as plugin_id=%d" % (plugin, plugin_id))
        config.registry.utilities.register([], IPaymentPlugin, str(key), plugin)
    intr = config.introspectable(
        "payment plugins", str(key),
        config.object_description(plugin),
        "payment_plugin_id=%d" % plugin_id
        )
    config.action(key, register, introspectables=[intr], order=PAYMENT_CONFIG)


def add_delivery_plugin(config, plugin, plugin_id):
    """ プラグイン登録 
    :param plugin: an instance of IDeliveryPlugin 
    """
    key = Discriminator(None, plugin_id)
    def register():
        logger.info("add_delivery_plugins: %r registered as plugin_id=%d" % (plugin, plugin_id))
        config.registry.utilities.register([], IDeliveryPlugin, str(key), plugin)
    intr = config.introspectable(
        "delivery plugins", str(key),
        config.object_description(plugin),
        "delivery_plugin_id=%d" % plugin_id
        )
    config.action(key, register, introspectables=[intr], order=PAYMENT_CONFIG)


def set_cart_interface(config, cart_if):
    def register():
        _cart_if = config.maybe_dotted(cart_if)
        reg = config.registry
        reg.registerUtility(_cart_if, ICartInterface)
    config.action('set_cart_interface', register, order=PAYMENT_CONFIG)


def add_payment_view_renderer_lookup(config, impl, type):
    def register():
        config.registry.utilities.register([], IPaymentViewRendererLookup, type, impl)
    config.action('payment_view_renderer_lookup:%s' % type, register, order=PAYMENT_CONFIG)
