from ticketing.payments.plugins.qr import DELIVERY_PLUGIN_ID as QR_PLUGIN_ID
from ticketing.payments.plugins.shipping import PLUGIN_ID as SHIPPING_PLUGIN_ID
from ticketing.payments.interfaces import IOrderDelivery, IMobileRequest

def includeme(config):
    config.include(include_qr)
    config.include(include_shipping)

def include_qr(config):
    config.add_view("ticketing.payments.plugins.qr.deliver_completion_viewlet", 
                    context=IOrderDelivery, 
                    name="delivery-%d" % QR_PLUGIN_ID, 
                    renderer="ticketing.orderreview:templates/plugins/qr_complete.html")
    config.add_view("ticketing.payments.plugins.qr.deliver_completion_viewlet", 
                    request_type=IMobileRequest, 
                    context=IOrderDelivery, 
                    name="delivery-%d" % QR_PLUGIN_ID, 
                    renderer="ticketing.orderreview:templates/plugins/qr_complete_mobile.html")

def include_shipping(config):
    config.add_view("ticketing.payments.plugins.shipping.deliver_completion_viewlet", 
                    context=IOrderDelivery, 
                    name="delivery-%d" % SHIPPING_PLUGIN_ID, 
                    renderer="ticketing.orderreview:templates/plugins/shipping_complete.html")
    config.add_view("ticketing.payments.plugins.shipping.deliver_completion_viewlet", 
                    request_type=IMobileRequest, 
                    context=IOrderDelivery, 
                    name="delivery-%d" % SHIPPING_PLUGIN_ID, 
                    renderer="ticketing.orderreview:templates/plugins/shipping_complete.html")

