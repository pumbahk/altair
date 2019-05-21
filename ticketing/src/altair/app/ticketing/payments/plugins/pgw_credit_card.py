# -*- coding:utf-8 -*-
import logging
from altair.app.ticketing.cart.interfaces import ICartPayment
from altair.app.ticketing.mails.interfaces import (
    ICompleteMailResource,
    IOrderCancelMailResource,
    ILotsAcceptedMailResource,
    ILotsElectedMailResource,
    ILotsRejectedMailResource,
)
from altair.app.ticketing.orders import models as order_models
from altair.app.ticketing.orders.api import bind_attributes
from altair.app.ticketing.payments.api import get_confirm_url
from altair.app.ticketing.payments.interfaces import IPaymentPlugin, IOrderPayment
from altair.app.ticketing.payments.plugins import PGW_CREDIT_CARD_PAYMENT_PLUGIN_ID as PAYMENT_PLUGIN_ID
from altair.app.ticketing.utils import clear_exc
from altair.formhelpers.form import OurForm, SecureFormMixin
from altair.pyramid_dynamic_renderer import lbr_view_config
from datetime import datetime
from pyramid.httpexceptions import HTTPFound
from wtforms.ext.csrf.fields import CSRFTokenField
from zope.interface import implementer
from ..exceptions import OrderLikeValidationFailure

logger = logging.getLogger(__name__)


def _overridable(path, fallback_ua_type=None):
    from . import _template
    return _template(path, type='overridable', for_='payments', plugin_type='payment', plugin_id=PAYMENT_PLUGIN_ID,
                     fallback_ua_type=fallback_ua_type)


@lbr_view_config(context=ICartPayment, name='payment-{}'.format(PAYMENT_PLUGIN_ID),
                 renderer=_overridable('pgw_card_confirm.html'))
def confirm_viewlet(context, request):
    """
    決済前確認子画面表示(購入確認で利用)
    :param context: コンテキスト
    :param request: リクエスト
    :return: 画面表示用データ
    """
    # TODO 仮実装 3DS認証が実装されたら入力に応じて表示するよう修正する
    return {
        'last4digits': '1234',
        'expirationMonth': '04',
        'expirationYear': '2025'
    }


@lbr_view_config(context=IOrderPayment, name='payment-{}'.format(PAYMENT_PLUGIN_ID),
                 renderer=_overridable('pgw_card_complete.html'))
def completion_viewlet(context, request):
    """
    決済完了子画面表示(購入完了で利用)
    :param context: コンテキスト
    :param request: リクエスト
    :return: 画面表示データ
    """
    return {}


@lbr_view_config(context=ICompleteMailResource, name='payment-{}'.format(PAYMENT_PLUGIN_ID),
                 renderer=_overridable('card_mail_complete.html', fallback_ua_type='mail'))
@lbr_view_config(context=ILotsElectedMailResource, name="payment-%d" % PAYMENT_PLUGIN_ID,
                 renderer=_overridable('checkout_mail_complete.html', fallback_ua_type='mail'))
def completion_payment_mail_viewlet(context, request):
    # TODO multicheckout.pyからコピー。必要に応じて独自に実装する。
    return {}


@lbr_view_config(context=IOrderCancelMailResource, name='payment-{}'.format(PAYMENT_PLUGIN_ID))
@lbr_view_config(context=ILotsRejectedMailResource, name='payment-{}'.format(PAYMENT_PLUGIN_ID))
@lbr_view_config(context=ILotsAcceptedMailResource, name='payment-{}'.format(PAYMENT_PLUGIN_ID))
def cancel_payment_mail_viewlet(context, request):
    # TODO multicheckout.pyからコピー。必要に応じて独自に実装する。
    return {}


@implementer(IPaymentPlugin)
class PaymentGatewayCreditCardPaymentPlugin(object):
    def validate_order(self, request, order_like, update=False):
        """
        予約のバリデーション

        対象の予約が決済可能な状態であることをチェックする。
        :param request: リクエスト
        :param order_like: Cart/LotEntry/Order/ProtoOrder
        :param update: 予約更新の場合はTrue, 新規予約の場合はFalseを指定する
        """
        if order_like.total_amount <= 0:
            raise OrderLikeValidationFailure(u'total_amount is zero', 'order.total_amount')

        if order_like.payment_amount < 0:
            raise OrderLikeValidationFailure(u'payment_amount is minus', 'order.payment_amount')

    def validate_order_cancellation(self, request, order, now):
        """ キャンセルバリデーション """
        pass

    def prepare(self, request, cart):
        """
        決済前準備としてカード情報入力画面を表示する
        :param request: リクエスト
        :param cart: カート
        :return: カード情報入力画面へ遷移
        """
        # マルチ決済にある、販売区分の設定文言を画面に表示する機能をPaymentGWへ展開する
        notice = cart.sales_segment.auth3d_notice
        request.session['altair.app.ticketing.payments.auth3d_notice'] = notice
        return HTTPFound(location=request.route_url('payment.card'))

    def finish(self, request, cart):
        """ 確定処理 """
        order_models.Order.query.session.add(cart)
        order = order_models.Order.create_from_cart(cart)
        order = bind_attributes(request, order)
        order.paid_at = datetime.now()
        cart.finish()

        return order

    def finish2(self, request, order):
        """ 確定処理 (先にOrderを作る場合) """
        pass

    def sales(self, request, cart):
        """ 売上確定処理 """
        pass

    def finished(self, request, order):
        """ *売上*確定済みか判定する (メソッド名がミスリードなのは歴史的経緯) """
        pass

    def cancel(self, request, order, now):
        """ キャンセル """
        pass

    def refresh(self, request, order):
        """ 注文金額変更 """
        pass

    def refund(self, request, order, refund_record):
        """ 払戻 """
        pass

    def get_order_info(self, request, order):
        pass


class PaymentGatewayCardForm(OurForm, SecureFormMixin):
    csrf_token = CSRFTokenField()


class PaymentGatewayCreditCardView(object):
    def __init__(self, request):
        """
        コンストラクタ
        :param request: リクエスト
        """
        self.request = request

    @clear_exc
    @lbr_view_config(route_name='payment.card', request_method='GET',
                     renderer=_overridable('pgw_card_form.html'))
    def show_card_form(self):
        """ カード情報入力画面表示 """
        form = PaymentGatewayCardForm(csrf_context=self.request.session)
        latest_card_info = None  # TODO 直近で使用のカード情報取得ロジックを後ほど実装する
        return dict(
            form=form,
            latest_card_info=latest_card_info,
        )

    @clear_exc
    @lbr_view_config(route_name='payment.card', request_method='POST',
                     renderer=_overridable('pgw_card_form.html'))
    def process_card_token(self):
        """ 入力されたカード情報を処理する """
        # TODO 3DSのコールバックもここで受ける？
        return HTTPFound(location=get_confirm_url(self.request))


def includeme(config):
    config.add_payment_plugin(PaymentGatewayCreditCardPaymentPlugin(), PAYMENT_PLUGIN_ID)
    config.add_route('payment.card', 'payment/card')
    config.scan(__name__)
