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
from altair.app.ticketing.payments.interfaces import IPaymentPlugin, IOrderPayment
from altair.app.ticketing.payments.plugins import PGW_CREDIT_CARD_PAYMENT_PLUGIN_ID as PAYMENT_PLUGIN_ID
from altair.app.ticketing.utils import clear_exc
from altair.formhelpers.form import OurForm, SecureFormMixin
from altair.pyramid_dynamic_renderer import lbr_view_config
from pyramid.httpexceptions import HTTPFound
from wtforms.ext.csrf.fields import CSRFTokenField
from zope.interface import implementer

logger = logging.getLogger(__name__)


def _selectable_renderer(path_fmt):
    # TODO multicheckout.pyからコピー。必要に応じて独自に実装する。
    from . import _template
    return _template(path_fmt, type='select_by_organization', for_='payments', plugin_type='payment',
                     plugin_id=PAYMENT_PLUGIN_ID)


def _overridable(path, fallback_ua_type=None):
    # TODO multicheckout.pyからコピー。必要に応じて独自に実装する。
    from . import _template
    return _template(path, type='overridable', for_='payments', plugin_type='payment', plugin_id=PAYMENT_PLUGIN_ID,
                     fallback_ua_type=fallback_ua_type)


@lbr_view_config(context=ICartPayment, name='payment-{}'.format(PAYMENT_PLUGIN_ID),
                 renderer=_overridable('card_confirm.html'))
def confirm_viewlet(context, request):
    # TODO multicheckout.pyからコピー。必要に応じて独自に実装する。
    return {}


@lbr_view_config(context=IOrderPayment, name='payment-{}'.format(PAYMENT_PLUGIN_ID),
                 renderer=_overridable('card_complete.html'))
def completion_viewlet(context, request):
    # TODO multicheckout.pyからコピー。必要に応じて独自に実装する。
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
        """ バリデーション """
        pass

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
        pass

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
        pass


def includeme(config):
    config.add_payment_plugin(PaymentGatewayCreditCardPaymentPlugin(), PAYMENT_PLUGIN_ID)
    config.add_route('payment.card', 'payment/card')
    config.scan(__name__)
