import logging

logger = logging.getLogger(__name__)

def includeme(config):
    config.add_directive("add_payment_plugin", ".directives.add_payment_plugin")
    config.add_directive("add_delivery_plugin", ".directives.add_delivery_plugin")
    config.add_directive("add_payment_delivery_plugin", ".directives.add_payment_delivery_plugin")

    config.add_directive("set_cart_getter", ".directives.set_cart_getter")
