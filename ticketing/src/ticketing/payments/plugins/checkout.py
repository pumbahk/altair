# -*- coding:utf-8 -*-

import logging
import transaction
from datetime import datetime

from zope.interface import implementer
from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from webhelpers.html.builder import literal

from ticketing.models import DBSession
from ticketing.payments.interfaces import IPaymentPlugin, IOrderPayment
from ticketing.mails.interfaces import ICompleteMailDelivery, ICompleteMailPayment
from ticketing.mails.interfaces import IOrderCancelMailDelivery, IOrderCancelMailPayment
from ticketing.cart import helpers as h
from ticketing.cart import api as a
from ticketing.cart.models import Cart, CartedProduct
from ticketing.core.api import get_channel
from ticketing.core.models import Product, PaymentDeliveryMethodPair, Order
from ticketing.core.models import MailTypeEnum
from ticketing.cart.interfaces import ICartPayment
from ticketing.cart.selectable_renderer import selectable_renderer
from ticketing.cart.views import back, back_to_top, back_to_product_list_for_mobile
from ticketing.checkout import api
from ticketing.checkout import helpers
from ticketing.payments.exceptions import PaymentPluginException

from . import CHECKOUT_PAYMENT_PLUGIN_ID as PAYMENT_PLUGIN_ID

logger = logging.getLogger(__name__)

def includeme(config):
    # 決済系(楽天あんしん支払いサービス)
    config.add_payment_plugin(CheckoutPlugin(), PAYMENT_PLUGIN_ID)
    config.add_route('payment.checkout.login', 'payment/checkout/login')
    config.add_route('payment.checkout.order_complete', 'payment/checkout/order_complete')
    config.add_route('payment.checkout.callback.success', 'payment/checkout/callback/success')
    config.add_route('payment.checkout.callback.error', 'payment/checkout/callback/error')
    config.scan(__name__)

def back_url(request):
    return request.route_url('payment.confirm')

class CheckoutSettlementFailure(PaymentPluginException):
    def __init__(self, message, order_no, back_url, error_code=None, return_code=None):
        super(CheckoutSettlementFailure, self).__init__(message, order_no, back_url)
        self.error_code = error_code
        self.return_code = return_code


@implementer(IPaymentPlugin)
class CheckoutPlugin(object):
    def prepare(self, request, cart):
        """ ここでは何もしない """

    def delegator(self, request, cart):
        if request.is_mobile:
            submit = literal(
                u'<input type="submit" value="楽天 お支払い" />'
                u'<div style="font-size:x-small;">※楽天あんしん支払いサービスへ移動します。</div>'
            )
        else:
            submit = literal(
                u'<input type="image" src="https://checkout.rakuten.co.jp/p/common/img/btn_check_01.gif?c9cc8c1b9ae94c18920540a80b95c16a" border="0">'
                u'<br />'
                u'※楽天あんしん支払いサービスへ移動します。'
            )
        return {
            'url':request.route_url('payment.checkout.login'),
            'submit':submit
        }

    def finish(self, request, cart):
        """ 売り上げ確定 """
        order_no = cart.order_no

        checkout = api.get_checkout_service(request, cart.performance.event.organization, get_channel(cart.channel))
        result = checkout.request_fixation_order([cart.checkout.orderControlId])
        if 'statusCode' in result and result['statusCode'] != '0':
            logger.info(u'CheckoutPlugin finish: 決済エラー order_no = %s, result = %s' % (order_no, result))
            request.session.flash(u'決済に失敗しました。再度お試しください。(%s)' % result['apiErrorCode'])
            transaction.commit()
            raise CheckoutSettlementFailure(
                message='finish: generic failure',
                order_no=order_no,
                back_url=back_url(request),
                error_code=result['apiErrorCode']
            )

        order = Order.create_from_cart(cart)
        order.paid_at = datetime.now()
        cart.finish()

        return order


@view_config(context=ICartPayment, name="payment-%d" % PAYMENT_PLUGIN_ID)
def confirm_viewlet(context, request):
    """ 確認画面表示
    :param context: ICartPayment
    """
    return Response(text=u"楽天あんしん支払いサービス")

@view_config(context=IOrderPayment, name="payment-%d" % PAYMENT_PLUGIN_ID)
def completion_viewlet(context, request):
    """ 完了画面表示
    :param context: IOrderPayment
    """
    return Response(text=u"楽天あんしん支払いサービス")

@view_config(context=ICompleteMailPayment, name="payment-%d" % PAYMENT_PLUGIN_ID, renderer="ticketing.payments.plugins:templates/checkout_mail_complete.html")
def payment_mail_viewlet(context, request):
    notice=context.mail_data("notice")
    return dict(notice=notice)

@view_config(context=IOrderCancelMailPayment, name="payment-%d" % PAYMENT_PLUGIN_ID)
def cancel_mail_viewlet(context, request):
    return Response(context.mail_data("notice"))


class CheckoutView(object):
    """ 楽天あんしん支払いサービス """

    def __init__(self, request):
        self.request = request

    @back(back_to_top, back_to_product_list_for_mobile)
    @view_config(route_name='payment.checkout.login', renderer='ticketing.payments.plugins:templates/checkout_login.html', request_method='POST')
    @view_config(route_name='payment.checkout.login', renderer=selectable_renderer("carts_mobile/%(membership)s/checkout_login_mobile.html"), request_method='POST', request_type='ticketing.mobile.interfaces.IMobileRequest')
    def login(self):
        cart = a.get_cart_safe(self.request)
        self.request.session['ticketing.cart.csrf_token'] = self.request.params.get('csrf_token')
        self.request.session['ticketing.cart.mailmagazine'] = self.request.params.getall('mailmagazine')
        return dict(
            form=helpers.checkout_form(self.request, cart)
        )

    @view_config(route_name='payment.checkout.order_complete', renderer="ticketing.payments.plugins:templates/checkout_response.html")
    def order_complete(self):
        '''
        注文完了通知を保存する
        '''
        service = api.get_checkout_service(self.request)
        checkout = service.save_order_complete(self.request)

        cart = Cart.query.filter(Cart.id==checkout.cart.id).first()
        if cart is None:
            result = api.RESULT_FLG_FAILED
        else:
            minutes = max(int(self.request.registry.settings['altair_cart.expire_time']) - 1, 0)
            expired = cart.is_expired(minutes) or cart.finished_at
            if expired:
                result = api.RESULT_FLG_FAILED
            else:
                result = api.RESULT_FLG_SUCCESS

        return {
            'xml':service.create_order_complete_response_xml(result, datetime.now())
        }

    @view_config(route_name='payment.checkout.callback.success', renderer='ticketing.payments.plugins:templates/checkout_callback.html', request_method='GET')
    @view_config(route_name='payment.checkout.callback.success', renderer=selectable_renderer("carts_mobile/%(membership)s/checkout_callback_mobile.html"), request_method='GET', request_type='ticketing.mobile.interfaces.IMobileRequest')
    def callback_success(self):
        cart = a.get_cart_safe(self.request)
        return {
            'csrf_token':self.request.session.get('ticketing.cart.csrf_token'),
            'mailmagazine_ids':self.request.session.get('ticketing.cart.mailmagazine')
        }

    @view_config(route_name='payment.checkout.callback.error', request_method='GET')
    def callback_error(self):
        cart = a.get_cart_safe(self.request)
        logger.info(u'CheckoutPlugin finish: 決済エラー order_no = %s' % (cart.order_no))
        self.request.session.flash(u'決済に失敗しました。しばらくしてから再度お試しください。')
        raise CheckoutSettlementFailure(
            message='finish: generic failure',
            order_no=cart.order_no,
            back_url=back_url(self.request),
            error_code=None
        )
