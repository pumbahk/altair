import logging

logger = logging.getLogger(__name__)

def includeme(config):
    config.include('altair.app.ticketing.sej.communicator')
    config.include('altair.point')
    config.include('altair.pgw')
    config.add_directive("add_payment_plugin", ".directives.add_payment_plugin")
    config.add_directive("add_delivery_plugin", ".directives.add_delivery_plugin")
    config.add_directive("add_payment_delivery_plugin", ".directives.add_payment_delivery_plugin")

    config.add_directive("set_cart_interface", ".directives.set_cart_interface")
    config.add_directive("add_payment_view_renderer_lookup", ".directives.add_payment_view_renderer_lookup")
