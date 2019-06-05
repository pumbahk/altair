# -*- coding:utf-8 -*-
import logging
from altair.app.ticketing.cart.interfaces import ICartPayment
from altair.app.ticketing.core import models as core_models
from altair.app.ticketing.mails.interfaces import (
    ICompleteMailResource,
    IOrderCancelMailResource,
    ILotsAcceptedMailResource,
    ILotsElectedMailResource,
    ILotsRejectedMailResource,
)
from altair.app.ticketing.orders import models as order_models
from altair.app.ticketing.orders.api import bind_attributes
from altair.app.ticketing.payments.api import get_confirm_url, get_cart
from altair.app.ticketing.payments.interfaces import IPaymentPlugin, IOrderPayment
from altair.app.ticketing.payments.plugins import PGW_CREDIT_CARD_PAYMENT_PLUGIN_ID as PAYMENT_PLUGIN_ID
from altair.app.ticketing.pgw import api as pgw_api
from altair.app.ticketing.pgw.models import PaymentStatusEnum
from altair.app.ticketing.utils import clear_exc
from altair.formhelpers.form import OurForm, SecureFormMixin
from altair.pyramid_dynamic_renderer import lbr_view_config
from datetime import datetime
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from wtforms import fields
from wtforms.ext.csrf.fields import CSRFTokenField
from zope.interface import implementer
from ..exceptions import OrderLikeValidationFailure, PaymentPluginException

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
    cart = get_cart(request)
    # safe_card_info stored at PaymentGatewayCreditCardView.process_card_token
    safe_card_info = _restore_safe_card_info(request, cart.order_no)
    return {
        'last4digits': safe_card_info.get(u'last4digits'),
        'expirationMonth': safe_card_info.get(u'expirationMonth'),
        'expirationYear': safe_card_info.get(u'expirationYear')
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
    """
    購入完了メールの決済方法の内容を生成する
    :param context: コンテキスト
    :param request: リクエスト
    :return: レンダリング用のデータ
    """
    notice = context.mail_data('P', 'notice')
    order = context.order
    return dict(notice=notice, order=order)


@lbr_view_config(context=IOrderCancelMailResource, name='payment-{}'.format(PAYMENT_PLUGIN_ID))
@lbr_view_config(context=ILotsRejectedMailResource, name='payment-{}'.format(PAYMENT_PLUGIN_ID))
@lbr_view_config(context=ILotsAcceptedMailResource, name='payment-{}'.format(PAYMENT_PLUGIN_ID))
def cancel_payment_mail_viewlet(context, request):
    """
    キャンセルメールメールの決済方法の内容を生成する
    :param context: コンテキスト
    :param request: リクエスト
    :return: レンダリング用のデータ
    """
    return Response(text=u'＜クレジットカードでお支払いの方＞\n{0}'.format(context.mail_data('P', 'notice')))


class PgwCardPaymentPluginFailure(PaymentPluginException):
    def __init__(self, message, order_no, back_url, ignorable=False, disp_nested_exc=False):
        import sys
        super(PgwCardPaymentPluginFailure, self).__init__(message, order_no, back_url, ignorable)
        self.nested_exc_info = sys.exc_info() if disp_nested_exc else None


class DummyPgwAPIError(Exception):  # TODO 仮の例外クラス、のちに本物に差し替える
    def __init__(self, error_code, error_message):
        self.error_code = error_code
        self.error_message = error_message


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
        """
        カード決済を実施し、Orderを作成する
        :param request: リクエスト
        :param cart: カート
        :return: Order(予約)
        """
        self._settle_card_accounts(request, cart)

        order_models.Order.query.session.add(cart)
        order = order_models.Order.create_from_cart(cart)
        order = bind_attributes(request, order)
        order.paid_at = datetime.now()
        cart.finish()

        return order

    def finish2(self, request, order_like):
        """
        Orderを生成せず、カード決済のみを実施する
        :param request: リクエスト
        :param order_like: OrderLikeオブジェクト(Order, ProtoOrder, Cart, LotEntryなど)
        """
        self._settle_card_accounts(request, order_like)

    def _settle_card_accounts(self, request, order_like):
        # TODO 例外メッセージは後ほど整理する
        if order_like.point_use_type == core_models.PointUseTypeEnum.AllUse:
            # 全額ポイント払いの場合、決済が発生しないためスキップする
            logger.info(u'skip card settlement[%s] due to full amount already paid by point', order_like.order_no)
            return

        def _get_cancel_amount():
            if pgw_order_status.gross_amount - order_like.payment_amount < 0:  # 増額は許容しない
                raise PgwCardPaymentPluginFailure(
                    message=u'unable to increase the [{}] settlement amount, {} -> {}'.format(
                        order_like.order_no, pgw_order_status.gross_amount, order_like.payment_amount),
                    order_no=order_like.order_no, back_url=None)
            return pgw_order_status.gross_amount - order_like.payment_amount

        try:
            pgw_order_status = pgw_api.get_pgw_order_status(order_like.order_no)

            if pgw_order_status.payment_status == PaymentStatusEnum.initialized.v:
                # 通常のケース
                pgw_api.authorize_and_capture(request, order_like.order_no, order_like.shipping_address.email_1)
            elif pgw_order_status.payment_status == PaymentStatusEnum.auth.v:
                # 当選処理のケース(先にオーソリ済)
                cancel_amount = _get_cancel_amount()
                if cancel_amount > 0:
                    # 当選商品額が抽選申込時のオーソリ金額と異なるケース(申込時は最大商品金額でオーソリする。希望商品が複数だとあり得る)
                    pgw_api.modify(request, order_like.order_no, order_like.payment_amount)
                pgw_api.capture(request, order_like.order_no)
            elif pgw_order_status.payment_status == PaymentStatusEnum.capture.v:
                cancel_amount = _get_cancel_amount()
                if cancel_amount > 0:
                    # Capture済みだが金額を変更して決済するケース(特殊なケース)
                    # 当選処理には、決済処理にて決済プラグインに成功し、配送プラグインに失敗すると、決済ステータスを成功のままとして
                    # 再度当選処理を実行させリカバリする仕様が存在する。この仕様のため、下記のオペレーションで発生し得る。
                    # 1. クレカ x コンビニの抽選申込を当選させ、配送プラグインの決済処理で失敗(この時クレカ側は決済完了している)
                    # 2. backendでは該当の抽選申込は当選予定のままとなっており、当選商品などを変更すれば金額が変更可能になる
                    # 3. 2で金額変更した状態で再度当選処理を実行する
                    #
                    # TODO 本来、決済完了しているのに当選商品を変更できたり落選にできたりする仕様がおかしいため後に修正を検討する
                    logger.warn('the [%s] settlement amount to be modified, %s -> %s', order_like.order_no,
                                pgw_order_status.gross_amount, order_like.payment_amount)
                    pgw_api.modify(request, order_like.order_no, order_like.payment_amount)
                else:
                    logger.info('the order[%s] is already settled', order_like.order_no)
            else:
                raise PgwCardPaymentPluginFailure(
                    message=u'the payment status "{}" of order({}) is invalid for settlement'.format(
                        pgw_order_status.payment_status, order_like.order_no),
                    order_no=order_like.order_no, back_url=None)
        except DummyPgwAPIError as api_error:
            recoverable_errors = [u'temporarily_unavailable', u'invalid_payment_method', u'aborted_payment',
                                  u'cvv_token_unavailable']
            # 回復可能なエラーの場合はback_urlを指定し、カード情報入力画面へ戻す
            back_url = request.route_url('payment.card.error') if api_error.error_code in recoverable_errors else None
            raise PgwCardPaymentPluginFailure(
                message=u'[{}]PaymentGW API error occurred(errorCode={}, errorMessage={})'.format(
                    order_like.order_no, api_error.error_code, api_error.error_message),
                order_no=order_like.order_no, back_url=back_url, ignorable=bool(back_url))
        except PgwCardPaymentPluginFailure:
            raise
        except Exception:  # PgwCardPaymentPluginFailure以外のエラーをハンドリング
            raise PgwCardPaymentPluginFailure(message=u'unexpected error occurred during settlement',
                                              order_no=order_like.order_no, back_url=None, disp_nested_exc=True)

    def sales(self, request, cart):
        """ 売上確定処理 """
        pass

    def finished(self, request, order):
        """ *売上*確定済みか判定する (メソッド名がミスリードなのは歴史的経緯) """
        pass

    def cancel(self, request, order, now):
        """
        決済キャンセルを実施する
        :param request: リクエスト
        :param order: 予約
        :param now: 現在日時
        """
        if order.point_use_type == core_models.PointUseTypeEnum.AllUse:
            # 全額ポイント払いの場合、決済が存在しないためスキップする
            logger.info(u'skip to cancel %s due to full amount already paid by point', order.order_no)
            return

        pgw_status = pgw_api.get_pgw_status(request, order.order_no)
        if pgw_status[u'details'][0][u'paymentStatusType'] not in [u'captured']:
            raise PgwCardPaymentPluginFailure(
                message=u'the "{}" paymentStatusType of order({}) is invalid to cancel'.format(
                    pgw_status[u'details'][0][u'paymentStatusType'], order.order_no), order_no=order.order_no,
                back_url=None)

        api_result = pgw_api.cancel_or_refund(request, order.order_no)
        if api_result[u'resultType'] != u'success':
            raise PgwCardPaymentPluginFailure(
                message=u'failed PaymentGW API to cancel {}(resultType={}, errorCode={}, errorMessage={})'.format(
                    order.order_no, api_result.get(u'resultType'), api_result.get(u'errorCode'),
                    api_result.get(u'errorMessage')), order_no=order.order_no, back_url=None)

    def refresh(self, request, order):
        """
        決済済金額の変更を実施する
        :param request: リクエスト
        :param order: 予約
        """
        if order.point_use_type == core_models.PointUseTypeEnum.AllUse:
            logger.info(u'skip to refresh %s due to full amount already paid by point', order.order_no)
            return  # 全額ポイント払いの場合、決済が存在しないためスキップする
        if order.delivered_at is not None:
            raise PgwCardPaymentPluginFailure(
                message=u'failed refreshing order[%s], which is already delivered'.format(order.order_no),
                order_no=order.order_no, back_url=None)

        pgw_status = pgw_api.get_pgw_status(request, order.order_no)
        if pgw_status[u'details'][0][u'paymentStatusType'] not in [u'captured']:
            raise PgwCardPaymentPluginFailure(
                message=u'the "{}" paymentStatusType of order({}) is invalid to refresh'.format(
                    pgw_status[u'details'][0][u'paymentStatusType'], order.order_no), order_no=order.order_no,
                back_url=None)

        if order.payment_amount == int(pgw_status[u'details'][0][u'grossAmount']):
            logger.info(u'skip to refresh %s due to no change', order.order_no)
            return
        elif order.payment_amount > pgw_status[u'details'][0][u'grossAmount']:
            raise PgwCardPaymentPluginFailure(
                message=u'failed refreshing order[{}] amount {}->{}, can\'t increase from the captured amount.'.format(
                    order.order_no, pgw_status[u'details'][0][u'grossAmount'], order.payment_amount),
                order_no=order.order_no, back_url=None)
        elif order.point_amount > 0 and pgw_status[u'details'][0][u'grossAmount'] > 0 >= order.payment_amount:
            # ポイント使用の予約の減額の場合、更新前の予約で支払が存在し、更新後で全額ポイント払いになる変更を許容しない
            # 一部ポイント払いから全額ポイント払いになり、支払方法が変わるような減額は許容しない。
            raise PgwCardPaymentPluginFailure(
                message=u'failed refreshing order[{}] amount {}->{}, can\'t change point use type'.format(
                    order.order_no, pgw_status[u'details'][0][u'grossAmount'], order.payment_amount),
                order_no=order.order_no, back_url=None)

        api_result = pgw_api.modify(request, order.order_no, int(order.payment_amount))
        if api_result[u'resultType'] != u'success':
            raise PgwCardPaymentPluginFailure(
                message=u'failed PaymentGW API to refresh {}(resultType={}, errorCode={}, errorMessage={})'.format(
                    order.order_no, api_result.get(u'resultType'), api_result.get(u'errorCode'),
                    api_result.get(u'errorMessage')), order_no=order.order_no, back_url=None)

    def refund(self, request, order, refund_record):
        """ 払戻 """
        pass

    def get_order_info(self, request, order):
        return {}


class PaymentGatewayCardForm(OurForm, SecureFormMixin):
    def _validate_required_for_new_card(self, field):
        if not self.is_use_latest_card() and not self['errorCode'].data and not field.data:
            # 新規カード利用で、PayVaultエラーがない時は必須パラメータ
            raise ValueError(u'{} is required for using new card.'.format(field.short_name))

    def _validate_required_for_latest_card(self, field):
        if self.is_use_latest_card() and not self['errorCode'].data and not field.data:
            # 前回カード利用で、PayVaultエラーがない時は必須パラメータ
            raise ValueError(u'{} is required for using latest card.'.format(field.short_name))

    def is_use_latest_card(self):
        return self['radioBtnUseCard'].data == u'latest_card'

    csrf_token = CSRFTokenField()
    radioBtnUseCard = fields.TextField()
    cardToken = fields.TextField(validators=[_validate_required_for_new_card])
    cvvToken = fields.TextField(validators=[_validate_required_for_new_card, _validate_required_for_latest_card])
    last4digits = fields.TextField(validators=[_validate_required_for_new_card])
    expirationYear = fields.TextField(validators=[_validate_required_for_new_card])
    expirationMonth = fields.TextField(validators=[_validate_required_for_new_card])
    errorCode = fields.TextField()
    errorMessage = fields.TextField()
    brandCode = fields.TextField()
    issuerCode = fields.TextField()
    signature = fields.TextField()
    iin = fields.TextField()
    timestamp = fields.TextField()
    keyVersion = fields.TextField()


def __get_session_key_of_safe_card_info(order_no):
    return u'pgw_safe_card_info_{}'.format(order_no)


def _store_safe_card_info(request, order_no, safe_card_info):
    session_key = __get_session_key_of_safe_card_info(order_no)
    request.session[session_key] = safe_card_info


def _restore_safe_card_info(request, order_no):
    session_key = __get_session_key_of_safe_card_info(order_no)
    return request.session[session_key]


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
    @lbr_view_config(route_name='payment.card.error', request_method='GET')
    def redirect_card_form_with_payment_error(self):
        """ 決済エラーが発生した場合に、エラー文言を設定してカード情報入力画面へリダイレクト """

        # 本処理はフロントからの購入完了で決済エラーの場合に呼び出される。
        # エラー文言の設定はビジネスロジック側の責務のため、ここで処理する
        # ブラウザバックなどでエラーメッセージが何度も表示されるのを軽減するためshow_card_formを直接callせず、リダイレクトとする
        self.request.session.flash(u'決済に失敗しました。カードや内容を確認の上再度お試しください。')
        return HTTPFound(location=self.request.route_url('payment.card'))

    @clear_exc
    @lbr_view_config(route_name='payment.card', request_method='POST', renderer=_overridable('pgw_card_form.html'))
    def process_card_token(self):
        """ 入力されたカード情報を処理する """
        form = PaymentGatewayCardForm(formdata=self.request.params, csrf_context=self.request.session)
        cart = get_cart(self.request)

        if not form.validate():
            # バリデーションNGは、CSRF攻撃かPayVault APIが生成したパラメータが渡されないことで発生するため、決済エラーとする
            logger.error('[PMT0002]PaymentGatewayCardForm validation error occurred(%s): %s', cart.order_no,
                         form.errors)
            raise PgwCardPaymentPluginFailure(
                message='[{}]Got invalid card form. It might be CSRF attack or system trouble.'.format(cart.order_no),
                order_no=cart.order_no, back_url=None)

        if form.errorCode.data == u'invalid_request_parameter':
            # invalid_request_parameterは未対応カードブランドやカード有効期限切れ、セキュリティコード誤り等で発生する
            logger.warn('[%s]PayVault responded an invalid_request_parameter, errorMessage=%s', cart.order_no,
                        form.errorMessage.data)
            self.request.session.flash(u'入力エラー: カードや入力内容を確認の上再度お試しください。')
            return HTTPFound(location=self.request.route_url('payment.card'))
        elif form.errorCode.data:
            # 回復不可能なPayVault APIエラーはアラートに出力し、決済エラーとする
            logger.error('[PMT0003]PayVault error occurred(%s), errorCode=%s, errorMessage=%s',
                         cart.order_no, form.errorCode.data, form.errorMessage.data)
            raise PgwCardPaymentPluginFailure(message='[{}]Failed to process card token due to PayVault error.'.format(
                cart.order_no), order_no=cart.order_no, back_url=None)

        if form.is_use_latest_card():
            card_token = None
            cvv_token = None
            safe_card_info = {}  # TODO 前回のカード情報取得処理を後ほど実装
        else:
            card_token = form['cardToken'].data
            cvv_token = form['cvvToken'].data
            safe_card_info = {
                u'last4digits': form['last4digits'].data,
                u'expirationYear': form['expirationYear'].data,
                u'expirationMonth': form['expirationMonth'].data,
            }

        pgw_api.initialize_pgw_order_status(cart.organization.setting.pgw_sub_service_id, cart.order_no, card_token,
                                            cvv_token, cart.payment_amount)
        # TODO 3DS認証を後ほど実装

        _store_safe_card_info(self.request, cart.order_no, safe_card_info)
        return HTTPFound(location=get_confirm_url(self.request))


def includeme(config):
    config.add_payment_plugin(PaymentGatewayCreditCardPaymentPlugin(), PAYMENT_PLUGIN_ID)
    config.add_route('payment.card', 'payment/card')
    config.add_route('payment.card.error', 'payment/card/error')
    config.scan(__name__)
