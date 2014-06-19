# -*- coding:utf-8 -*-

import sys
import logging
import transaction
from decimal import Decimal
from datetime import datetime

from zope.interface import implementer
from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPOk, HTTPFound, HTTPBadRequest
from webhelpers.html.builder import literal

from altair.app.ticketing.utils import clear_exc
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.mails.interfaces import ICompleteMailPayment
from altair.app.ticketing.mails.interfaces import IOrderCancelMailPayment
from altair.app.ticketing.mails.interfaces import ILotsAcceptedMailPayment
from altair.app.ticketing.mails.interfaces import ILotsElectedMailPayment
from altair.app.ticketing.mails.interfaces import ILotsRejectedMailPayment

from altair.app.ticketing.cart import api as cart_api
from altair.app.ticketing.cart.models import Cart, CartedProduct
from altair.app.ticketing.core.api import get_channel
from altair.app.ticketing.cart.exceptions import NoCartError
from altair.app.ticketing.core.models import Product, PaymentDeliveryMethodPair
from altair.app.ticketing.core.models import MailTypeEnum, ChannelEnum
from altair.app.ticketing.orders.models import Order
from altair.app.ticketing.cart.events import notify_order_completed
from altair.app.ticketing.cart.interfaces import ICartPayment
from altair.app.ticketing.cart.selectable_renderer import selectable_renderer
from altair.app.ticketing.cart.views import back, back_to_top, back_to_product_list_for_mobile
from altair.app.ticketing.checkout import api
from altair.app.ticketing.checkout import helpers
from altair.app.ticketing.checkout.exceptions import AnshinCheckoutAPIError
from altair.app.ticketing.mailmags.api import multi_subscribe

from ..exceptions import PaymentPluginException, OrderLikeValidationFailure
from ..interfaces import IPaymentPlugin, IOrderPayment
from ..payment import Payment

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
    try:
        return request.route_url('payment.confirm')
    except:
        return None

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

ANSHIN_CHECKOUT_MINIMUM_AMOUNT = Decimal('100')

@implementer(IPaymentPlugin)
class CheckoutPlugin(object):
    def validate_order(self, request, order_like):
        for item in order_like.items:
            if item.price < ANSHIN_CHECKOUT_MINIMUM_AMOUNT:
                raise OrderLikeValidationFailure(u'product price too low', 'ordered_product.price')
        if order_like.delivery_fee != 0 and order_like.delivery_fee < ANSHIN_CHECKOUT_MINIMUM_AMOUNT:
            raise OrderLikeValidationFailure(u'delivery_fee too low', 'order.delivery_fee')
        if order_like.system_fee != 0 and order_like.system_fee < ANSHIN_CHECKOUT_MINIMUM_AMOUNT:
            raise OrderLikeValidationFailure(u'delivery_fee too low', 'order.system_fee')
        if order_like.special_fee and \
           order_like.special_fee < ANSHIN_CHECKOUT_MINIMUM_AMOUNT:
            raise OrderLikeValidationFailure(u'special_fee too low', 'order.special_fee')

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

    def finish2(self, request, order_like):
        # XXX ここで判定するのよくない。なぜなら、決済プラグインは Order の詳細を知っているべきではないから
        # (is_inner_channel は IOrderLike インターフェイスにない、IOrderLike インターフェイスは Cart も実装するものなので)
        if getattr(order_like, 'is_inner_channel', False):
            logger.info('order %s is inner order' % order_like.order_no)
            return
        raise NotImplementedError()

    @clear_exc
    def sales(self, request, order):
        """ 売り上げ確定 """
        service = api.get_checkout_service(request, order.organization_id, get_channel(order.channel))
        try:
            result = service.request_fixation_order([order])
        except AnshinCheckoutAPIError as e:
            logger.info(u'CheckoutPlugin finish: 決済エラー order_no = %s, result = %s' % (order.order_no, e.error_code))
            request.session.flash(u'決済に失敗しました。再度お試しください。')
            raise CheckoutSettlementFailure(
                message='finish: generic failure',
                order_no=order.order_no,
                back_url=back_url(request),
                error_code=e.error_code
                )

    def finished(self, request, order):
        """ 売上確定済か判定 """
        service = api.get_checkout_service(request, order.organization_id, get_channel(order.channel))
        return bool(service.get_order_settled_at(order))

    def refresh(self, request, order_like):
        # XXX ここで判定するのよくない。なぜなら、決済プラグインは Order の詳細を知っているべきではないから
        # (is_inner_channel は IOrderLike インターフェイスにない、IOrderLike インターフェイスは Cart も実装するものなので)
        if getattr(order_like, 'is_inner_channel', False):
            logger.info('order %s is inner order' % order_like.order_no)
            return

        service = api.get_checkout_service(request, order_like.organization_id, get_channel(order_like.channel))
        service.request_change_order([(order_like, order_like)])

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
        cart = cart_api.get_cart_safe(self.request, for_update=False)
        try:
            self.request.session['altair.app.ticketing.cart.magazine_ids'] = [long(v) for v in self.request.params.getall('mailmagazine')]
        except TypeError, ValueError:
            raise HTTPBadRequest()
        logger.debug(u'mailmagazine = %s' % self.request.session['altair.app.ticketing.cart.magazine_ids'])
        channel = get_channel(cart.channel)
        service = api.get_checkout_service(self.request, cart.performance.event.organization, channel)
        _, form = service.build_checkout_request_form(
            cart,
            success_url=self.request.route_url('payment.checkout.callback.success'),
            fail_url=self.request.route_url('payment.checkout.callback.error')
            )
        return dict(
            form=literal(form)
            )


class CheckoutCompleteView(object):
    """ 楽天あんしん支払いサービス(API)からの完了通知受取 """

    def __init__(self, request):
        self.request = request
        self.context = request.context

    @view_config(route_name='payment.checkout.order_complete')
    def order_complete(self):
        '''
        注文完了通知を保存し、予約確定する
          - 楽天あんしん支払いサービスより注文完了通知が来たタイミングで、予約を確定させる
          - ここでOKを返すとオーソリが完了する、なのでCheckoutの売上処理はこのタイミングではやらない
          - NGの場合はオーソリもされないので、Cartも座席解放してfinished_atをセットする
          - Checkoutの売上処理は、バッチで行う
        '''
        service = api.get_checkout_service(self.request)
        checkout = service.save_order_complete(self.request.params)

        cart = Cart.query.filter(Cart.id==checkout.orderCartId_old).first()
        if self._validate(cart):
            logger.debug(u'checkout order_complete success (cart_id=%s)' % cart.id)
            result = api.RESULT_FLG_SUCCESS
            self._success(cart)
        else:
            logger.debug(u'checkout order_complete failed (cart_id=%s)' % cart.id)
            result = api.RESULT_FLG_FAILED
            self._failed(cart)

        return HTTPOk(  
            content_type='text/html', charset='utf-8',
            body=service.create_order_complete_response_xml(result, datetime.now()))

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
        cart = cart_api.get_cart(self.request)
        if not cart:
            raise NoCartError()

        service = api.get_checkout_service(self.request, cart.performance.event.organization, get_channel(cart.channel))
        service.mark_authorized(cart.order_no)

        # メール購読
        try:
            user = cart_api.get_or_create_user(self.context.authenticated_user())
            emails = cart.shipping_address.emails
            magazine_ids = self.request.session.get('altair.app.ticketing.cart.magazine_ids')
            multi_subscribe(user, emails, magazine_ids)
            logger.debug(u'subscribe mags (magazine_ids=%s)' % magazine_ids)
        except Exception as e: # all exception ignored
            logger.error('Exception ignored', exc_info=sys.exc_info()) 
        finally:
            del self.request.session['altair.app.ticketing.cart.magazine_ids']
            self.request.session.persist()
        cart_api.remove_cart(self.request)
        cart_api.logout(self.request)

        return dict(order=cart.order)

    @clear_exc
    @view_config(route_name='payment.checkout.callback.error', request_method='GET')
    def error(self):
        cart = cart_api.get_cart(self.request)
        logger.info(u'CheckoutPlugin finish: 決済エラー order_no = %s' % (cart.order_no))
        self.request.session.flash(u'決済に失敗しました。しばらくしてから再度お試しください。')
        raise CheckoutSettlementFailure(
            message='finish: generic failure',
            order_no=cart.order_no,
            back_url=back_url(self.request),
            error_code=None
        )

