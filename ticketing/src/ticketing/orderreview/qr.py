from ticketing.cart.plugins.qr import DELIVERY_PLUGIN_ID
from ticketing.cart.interfaces import IOrderDelivery, IMobileRequest

def includeme(config):
    config.add_view("ticketing.cart.plugins.qr.deliver_completion_viewlet", 
                    context=IOrderDelivery, 
                    name="delivery-%d" % DELIVERY_PLUGIN_ID, 
                    renderer="ticketing.cart.plugins:templates/qr_orderreview_complete.html")
    config.add_view("ticketing.cart.plugins.qr.deliver_completion_viewlet", 
                    request_type=IMobileRequest, 
                    context=IOrderDelivery, 
                    name="delivery-%d" % DELIVERY_PLUGIN_ID, 
                    renderer="ticketing.cart.plugins:templates/qr_orderreview_complete_mobile.html")
