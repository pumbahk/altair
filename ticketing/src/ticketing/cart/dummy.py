# -*- coding:utf-8 -*-
from ticketing.cart.selectable_renderer import selectable_renderer
from ticketing.core.api import get_organization
from ticketing.users import models as u_models

def includeme(config):
    config.add_route("dummy.cart.payment", "/dummy/payment")
    config.add_view(payment_view, route_name='dummy.cart.payment', request_method="GET", renderer=selectable_renderer("carts/%(membership)s/payment.html"))
    config.add_view(payment_view, route_name='dummy.cart.payment', request_type='.interfaces.IMobileRequest', request_method="GET", renderer=selectable_renderer("carts_mobile/%(membership)s/payment.html"))

    config.add_route("dummy.payment.confirm", "/dummy/confirm")
    config.add_view(confirm_view, route_name='dummy.payment.confirm', request_method="GET", renderer=selectable_renderer("carts/%(membership)s/confirm.html"))
    config.add_view(confirm_view, route_name='dummy.payment.confirm', request_type='.interfaces.IMobileRequest', request_method="GET", renderer=selectable_renderer("carts_mobile/%(membership)s/confirm.html"))

    config.add_route("dummy.payment.complete", "/dummy/complete")
    config.add_view(complete_view, route_name='dummy.payment.complete', request_method="GET", renderer=selectable_renderer("carts/%(membership)s/complete.html"))
    config.add_view(complete_view, route_name='dummy.payment.complete', request_type='.interfaces.IMobileRequest', request_method="GET", renderer=selectable_renderer("carts_mobile/%(membership)s/complete.html"))

    config.add_route("dummy.timeout", "/dummy/timeout")
    config.add_view(timeout_view, route_name="dummy.timeout", renderer="carts/timeout.html")


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


def _get_mailmagazines_from_organization(organization):
    return u_models.MailMagazine.query.outerjoin(u_models.MailSubscription) \
            .filter(u_models.MailMagazine.organization==organization)
           

def confirm_view(request):
    import mock
    from collections import defaultdict
    with mock.patch("ticketing.cart.rakuten_auth.api.authenticated_user"):
        form = mock.Mock()
        cart = _dummy_cart()
        request.session["order"] = defaultdict(str)
        magazines = _get_mailmagazines_from_organization(get_organization(request))
        user = mock.Mock()
        return dict(cart=cart, mailmagazines=magazines, user=user, form=form)


def complete_view(request):
    import mock
    with mock.patch("ticketing.cart.rakuten_auth.api.authenticated_user"):
        order = _dummy_order()
        return dict(order=order)

def payment_view(request):
    import mock
    from .schemas import ClientForm
    request.session.flash(u"お支払い方法／受け取り方法をどれかひとつお選びください")
    with mock.patch("ticketing.cart.rakuten_auth.api.authenticated_user"):
        params=dict(form=ClientForm(), 
                    payment_delivery_methods=[], 
                    user=mock.Mock(), 
                    user_profile=mock.Mock())
        return params
    
def timeout_view(request):
    return {}
