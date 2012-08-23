from pyramid.response import Response
from pyramid.renderers import render

def includeme(config):
    config.add_route("dummy.cart.payment", "/dummy/payment")
    config.add_view(payment_view, route_name="dummy.cart.payment")
    config.add_route("dummy.payment.finish", "/dummy/completed")
    config.add_view(complete_view, route_name="dummy.payment.finish")

def _dummy_order():
    import mock
    from datetime import datetime
    order = mock.Mock()
    class performance:
        name = "Hey"
        start_on = datetime.now()
        class event:
            title = "event"
            id = 4
        class venue:
            name = "venue"
    order.ordered_products = []
    order.transaction_fee = 100
    order.system_fee = 200
    order.delivery_fee = 300
    order.total_amount = 500
    order.payment_delivery_pair.payment_method.payment_plugin_id = 1
    order.payment_delivery_pair.delivery_method.delivery_plugin_id = 1
    order.performance = performance
    return order

def complete_view(request):
    import mock
    with mock.patch("ticketing.cart.rakuten_auth.api.authenticated_user"):
        order = _dummy_order()
        result = render("carts/completion.html", dict(order=order), request=request)
        return Response(result)

def payment_view(request):
    import mock
    from .schemas import ClientForm
    with mock.patch("ticketing.cart.rakuten_auth.api.authenticated_user"):
        params=dict(form=ClientForm(), 
                    payment_delivery_methods=[], 
                    user=mock.Mock(), 
                    user_profile=mock.Mock())
        result = render("carts/payment.html", params, request=request)
        return Response(result)
    
