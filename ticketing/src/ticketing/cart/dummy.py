# -*- coding:utf-8 -*-

from pyramid.response import Response
from pyramid.renderers import render

def includeme(config):
    config.add_route("dummy.cart.payment", "/dummy/payment")
    config.add_view(payment_view, route_name="dummy.cart.payment")
    config.add_route("dummy.payment.confirm", "/dummy/confirm")
    config.add_view(confirm_view, route_name="dummy.payment.confirm")
    config.add_route("dummy.payment.finish", "/dummy/completed")
    config.add_view(complete_view, route_name="dummy.payment.finish")

def _dummy_performance():
    from datetime import datetime
    class performance:
        name = "Hey"
        start_on = datetime.now()
        class event:
            title = "event"
            id = 4
        class venue:
            name = "venue"
    return performance

def _dummy_order():
    import mock
    order = mock.Mock()
    order.performance = _dummy_performance()
    order.ordered_products = []
    order.transaction_fee = 100
    order.system_fee = 200
    order.delivery_fee = 300
    order.total_amount = 500
    order.payment_delivery_pair.payment_method.payment_plugin_id = 1
    order.payment_delivery_pair.delivery_method.delivery_plugin_id = 1
    return order

def _dummy_cart():
    import mock
    cart = mock.Mock()
    cart.performance = _dummy_performance()
    cart.products = []
    cart.transaction_fee = 100
    cart.system_fee = 200
    cart.delivery_fee = 300
    cart.total_amount = 500
    cart.payment_delivery_pair.payment_method.payment_plugin_id = 1
    cart.payment_delivery_pair.delivery_method.delivery_plugin_id = 1
    return cart

def confirm_view(request):
    import mock
    from collections import defaultdict
    with mock.patch("ticketing.cart.rakuten_auth.api.authenticated_user"):
        form = mock.Mock()
        cart = _dummy_cart()
        request.session["order"] = defaultdict(str)
        magazines = []
        user = mock.Mock()
        params = dict(cart=cart, mailmagazines=magazines, user=user, form=form)
        result = render("carts/confirm.html", params, request=request)
        return Response(result)
    
def complete_view(request):
    import mock
    with mock.patch("ticketing.cart.rakuten_auth.api.authenticated_user"):
        order = _dummy_order()
        result = render("carts/completion.html", dict(order=order), request=request)
        return Response(result)

def payment_view(request):
    import mock
    from .schemas import ClientForm
    request.session.flash(u"お支払い方法／受け取り方法をどれかひとつお選びください")
    with mock.patch("ticketing.cart.rakuten_auth.api.authenticated_user"):
        params=dict(form=ClientForm(), 
                    payment_delivery_methods=[], 
                    user=mock.Mock(), 
                    user_profile=mock.Mock())
        result = render("carts/payment.html", params, request=request)
        return Response(result)
    
