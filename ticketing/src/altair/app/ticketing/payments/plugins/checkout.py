# -*- coding:utf-8 -*-

import sys
import logging
import transaction
from datetime import datetime

from zope.interface import implementer
from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound, HTTPBadRequest
from webhelpers.html.builder import literal

from altair.app.ticketing.utils import clear_exc
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.mails.interfaces import ICompleteMailPayment
from altair.app.ticketing.mails.interfaces import IOrderCancelMailPayment
from altair.app.ticketing.mails.interfaces import ILotsAcceptedMailPayment
from altair.app.ticketing.mails.interfaces import ILotsElectedMailPayment
from altair.app.ticketing.mails.interfaces import ILotsRejectedMailPayment

from altair.app.ticketing.cart import helpers as h
from altair.app.ticketing.cart import api as a
from altair.app.ticketing.cart.models import Cart, CartedProduct
from altair.app.ticketing.core.api import get_channel
from altair.app.ticketing.cart.exceptions import NoCartError
from altair.app.ticketing.core.models import Product, PaymentDeliveryMethodPair, Order
from altair.app.ticketing.core.models import MailTypeEnum
from altair.app.ticketing.cart.events import notify_order_completed
from altair.app.ticketing.cart.interfaces import ICartPayment
from altair.app.ticketing.cart.selectable_renderer import selectable_renderer
from altair.app.ticketing.cart.views import back, back_to_top, back_to_product_list_for_mobile
from altair.app.ticketing.checkout import api
from altair.app.ticketing.checkout import helpers
from altair.app.ticketing.payments.exceptions import PaymentPluginException
from altair.app.ticketing.payments.interfaces import IPaymentPlugin, IOrderPayment
from altair.app.ticketing.payments.payment import Payment
from altair.app.ticketing.mailmags.api import multi_subscribe
from altair.app.ticketing.users.api import get_or_create_user

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
    def __init__(self, message, order_no, back_url, ignorable=False, error_code=None, return_code=None):
        super(CheckoutSettlementFailure, self).__init__(message, order_no, back_url, ignorable)
        self.error_code = error_code
        self.return_code = return_code

    @property
    def message(self):
        return '%s (error_code=%s, return_code=%s)' % (
            super(CheckoutSettlementFailure, self).message,
            self.error_code,
            self.return_code
            )


@implementer(IPaymentPlugin)
class CheckoutPlugin(object):
    def prepare(self, request, cart):
        """ ここでは何もしない """

    def delegator(self, request, cart):
        if request.is_mobile:
            submit = literal(
                u'<input type="submit" value="次へ" />'
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
        order = Order.create_from_cart(cart)
        order.paid_at = datetime.now()
        cart.finish()
        return order

    @clear_exc
    def sales(self, request, order):
        """ 売り上げ確定 """
        service = api.get_checkout_service(request, order.performance.event.organization, get_channel(order.channel))
        checkout = order.checkout
        result = service.request_fixation_order([checkout.orderControlId])
        if 'statusCode' in result and result['statusCode'] != '0':
            logger.info(u'CheckoutPlugin finish: 決済エラー order_no = %s, result = %s' % (order.order_no, result))
            request.session.flash(u'決済に失敗しました。再度お試しください。(%s)' % result['apiErrorCode'])
            transaction.commit()
            raise CheckoutSettlementFailure(
                message='finish: generic failure',
                order_no=order.order_no,
                back_url=back_url(request),
                error_code=result['apiErrorCode']
            )
        checkout.sales_at = datetime.now()
        checkout.save()
        return

    def finished(self, request, order):
        """ 売上確定済か判定 """
        if not order.checkout:
            return False
        checkout = order.checkout
        return bool(checkout.sales_at)

    def refresh(self, request, order):
        if order.is_inner_channel:
            logger.info('order %s is inner order' % order.order_no)
            return

        raise NotImplementedError()

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

@view_config(context=ICompleteMailPayment, name="payment-%d" % PAYMENT_PLUGIN_ID, renderer="altair.app.ticketing.payments.plugins:templates/checkout_mail_complete.html")
@view_config(context=ILotsElectedMailPayment, name="payment-%d" % PAYMENT_PLUGIN_ID, renderer="altair.app.ticketing.payments.plugins:templates/checkout_mail_complete.html")
def payment_mail_viewlet(context, request):
    notice=context.mail_data("notice")
    order=context.order
    return dict(notice=notice, order=order)

@view_config(context=IOrderCancelMailPayment, name="payment-%d" % PAYMENT_PLUGIN_ID)
@view_config(context=ILotsRejectedMailPayment, name="payment-%d" % PAYMENT_PLUGIN_ID)
@view_config(context=ILotsAcceptedMailPayment, name="payment-%d" % PAYMENT_PLUGIN_ID)
def notice_viewlet(context, request):
    return Response(text=u"＜クレジットカードでお支払いの方＞\n{0}".format(context.mail_data("notice")))


class CheckoutView(object):
    """ 楽天あんしん支払いサービスへ遷移する """

    def __init__(self, request):
        self.request = request
        self.context = request.context

    @clear_exc
    @back(back_to_top, back_to_product_list_for_mobile)
    @view_config(route_name='payment.checkout.login', renderer='altair.app.ticketing.payments.plugins:templates/checkout_login.html', request_method='POST')
    @view_config(route_name='payment.checkout.login', renderer=selectable_renderer("%(membership)s/mobile/checkout_login_mobile.html"), request_method='POST', request_type='altair.mobile.interfaces.IMobileRequest')
    def login(self):
        cart = a.get_cart_safe(self.request)
        try:
            self.request.session['altair.app.ticketing.cart.magazine_ids'] = [long(v) for v in self.request.params.getall('mailmagazine')]
        except TypeError, ValueError:
            raise HTTPBadRequest()
        logger.debug(u'mailmagazine = %s' % self.request.session['altair.app.ticketing.cart.magazine_ids'])
        return dict(
            form=helpers.checkout_form(self.request, cart)
        )


class CheckoutCompleteView(object):
    """ 楽天あんしん支払いサービス(API)からの完了通知受取 """

    def __init__(self, request):
        self.request = request
        self.context = request.context

    @view_config(route_name='payment.checkout.order_complete', renderer="altair.app.ticketing.payments.plugins:templates/checkout_response.html")
    def order_complete(self):
        '''
        注文完了通知を保存し、予約確定する
          - 楽天あんしん支払いサービスより注文完了通知が来たタイミングで、予約を確定させる
          - ここでOKを返すとオーソリが完了する、なのでCheckoutの売上処理はこのタイミングではやらない
          - NGの場合はオーソリもされないので、Cartも座席解放してfinished_atをセットする
          - Checkoutの売上処理は、バッチで行う
        '''
        service = api.get_checkout_service(self.request)
        checkout = service.save_order_complete(self.request)

        cart = Cart.query.filter(Cart.id==checkout.cart.id).first()
        if self._validate(cart):
            logger.debug(u'checkout order_complete success (cart_id=%s)' % cart.id)
            result = api.RESULT_FLG_SUCCESS
            self._success(cart)
        else:
            logger.debug(u'checkout order_complete failed (cart_id=%s)' % cart.id)
            result = api.RESULT_FLG_FAILED
            self._failed(cart)

        return {
            'xml':service.create_order_complete_response_xml(result, datetime.now())
        }

    def _validate(self, cart):
        now = datetime.now() # XXX
        if cart is None:
            return False
        if not cart.is_valid():
            return False
        if not cart.sales_segment.in_term(datetime.now()):
            return False
        if cart.is_expired(max(int(self.request.registry.settings['altair_cart.expire_time']) - 1, 0), now):
            return False
        if cart.finished_at is not None:
            return False
        return True

    def _success(self, cart):
        payment = Payment(cart, self.request)
        order = payment.call_payment()
        notify_order_completed(self.request, order)

    def _failed(self, cart):
        cart.release()
        cart.finished_at = datetime.now()


class CheckoutCallbackView(object):
    """ 楽天あんしん支払いサービスからの戻り先 """

    def __init__(self, request):
        self.request = request
        self.context = request.context

    @clear_exc
    @back(back_to_top, back_to_product_list_for_mobile)
    @view_config(route_name='payment.checkout.callback.success', renderer=selectable_renderer("%(membership)s/pc/completion.html"), request_method='GET')
    @view_config(route_name='payment.checkout.callback.success', request_type='altair.mobile.interfaces.IMobileRequest', renderer=selectable_renderer("%(membership)s/mobile/completion.html"), request_method='GET')
    def success(self):
        cart = a.get_cart(self.request)
        if not cart:
            raise NoCartError()

        # メール購読
        try:
            user = get_or_create_user(self.context.authenticated_user())
            emails = cart.shipping_address.emails
            magazine_ids = self.request.session.get('altair.app.ticketing.cart.magazine_ids')
            multi_subscribe(user, emails, magazine_ids)
            logger.debug(u'subscribe mags (magazine_ids=%s)' % magazine_ids)
        except e:
            logger.error('Exception ignored', exc_info=sys.exc_info()) 
        finally:
            del self.request.session['altair.app.ticketing.cart.magazine_ids']
            self.request.session.persist()
        a.remove_cart(self.request)
        a.logout(self.request)

        return dict(order=cart.order)

    @clear_exc
    @view_config(route_name='payment.checkout.callback.error', request_method='GET')
    def error(self):
        cart = a.get_cart(self.request)
        logger.info(u'CheckoutPlugin finish: 決済エラー order_no = %s' % (cart.order_no))
        self.request.session.flash(u'決済に失敗しました。しばらくしてから再度お試しください。')
        raise CheckoutSettlementFailure(
            message='finish: generic failure',
            order_no=cart.order_no,
            back_url=back_url(self.request),
            error_code=None
        )

