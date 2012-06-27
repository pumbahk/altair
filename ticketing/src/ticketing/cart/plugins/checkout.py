# -*- coding:utf-8 -*-

from datetime import datetime

from zope.interface import implementer
from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound

from ticketing.orders.models import Order
from ticketing.cart.interfaces import IPaymentPlugin, IOrderPayment
from ticketing.cart import helpers as h
from ticketing.cart import api as a
from ticketing.cart.models import Cart, CartedProduct
from ticketing.core.models import Product, PaymentDeliveryMethodPair
from ticketing.checkout import api
from ticketing.checkout import helpers

PAYMENT_PLUGIN_ID = 2

def includeme(config):
    # 決済系(楽天あんしん決済)
    config.add_payment_plugin(CheckoutPlugin(), PAYMENT_PLUGIN_ID)
    config.add_route("payment.checkout_login", 'payment/checkout/login')
    config.add_route("payment.checkout_order_complete", 'payment/checkout/order_complete')
    config.scan(__name__)


@implementer(IPaymentPlugin)
class CheckoutPlugin(object):
    def prepare(self, request, cart):
        """ 楽天あんしん決済へリダイレクト """
        return HTTPFound(location=request.route_url("payment.checkout_login"))

    def finish(self, request, cart):
        """ 売り上げ確定 """
        order = Order.create_from_cart(cart)
        order.paid_at = datetime.now()
        cart.finish()

        return order


@view_config(context=IOrderPayment, name="payment-%d" % PAYMENT_PLUGIN_ID)
def completion_viewlet(context, request):
    """ 完了画面表示
    :param context: IOrderPayment
    """
    return Response(text=u"楽天あんしん決済")


class CheckoutView(object):
    """ 楽天あんしん決済 """

    def __init__(self, request):
        self.request = request

    @view_config(route_name='payment.checkout_login', request_method="GET", renderer="ticketing.cart.plugins:templates/checkout_login.html")
    def login(self):
        cart = a.get_cart(self.request)

        form = {}
        form['h'] = helpers.begin_checkout_form(self.request)
        form['b'] = helpers.render_checkout(self.request, cart)
        form['f'] = helpers.end_checkout_form(self.request)

        return dict(form=form)

    @view_config(route_name='payment.checkout_order_complete', renderer="ticketing.cart.plugins:templates/checkout_response.html")
    def order_complete(self):
        '''
        注文完了通知を保存する
        '''
        service = api.get_checkout_service(self.request)
        result = service.save_order_complete(self.request)

        return {
            'xml':service.create_order_complete_response_xml(result, datetime.now())
        }
