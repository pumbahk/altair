# -*- coding:utf-8 -*-
import logging
import transaction
from datetime import datetime, timedelta
from zope.interface import implementer
from pyramid.view import view_defaults
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound

from wtforms import fields
from altair.formhelpers.form import OurForm, SecureFormMixin
from wtforms.validators import Regexp, Length
from wtforms.ext.csrf.fields import CSRFTokenField

import markupsafe

from altair.multicheckout import helpers as m_h
from altair.multicheckout.api import get_multicheckout_3d_api
from altair.multicheckout.util import get_multicheckout_ahead_com_name
from altair.multicheckout.models import (
    MultiCheckoutStatusEnum,
)
from altair.pyramid_dynamic_renderer import lbr_view_config
from altair.app.ticketing.utils import clear_exc
from altair.app.ticketing.core import models as c_models
from altair.app.ticketing.orders import models as order_models
from altair.app.ticketing.payments.interfaces import IPaymentPlugin, IOrderPayment
from altair.app.ticketing.cart.interfaces import ICartPayment
from altair.app.ticketing.mails.interfaces import (
    ICompleteMailResource,
    IOrderCancelMailResource,
    ILotsAcceptedMailResource,
    ILotsElectedMailResource,
    ILotsRejectedMailResource,
    )
from altair.formhelpers import (
    Required,
    Translations,
    ignore_space_hyphen,
    capitalize,
    OurSelectField
)
from altair.timeparse import parse_time_spec

from .models import DBSession
from .. import logger
from altair.app.ticketing.cart import api
from altair.app.ticketing.cart.exceptions import NoCartError, InvalidCartStatusError
from ..exceptions import PaymentPluginException, OrderLikeValidationFailure
from altair.app.ticketing.views import mobile_request
from altair.app.ticketing.fanstatic import with_jquery
from altair.app.ticketing.payments.api import get_cart, get_confirm_url

logger = logging.getLogger(__name__)

from . import MULTICHECKOUT_PAYMENT_PLUGIN_ID as PLUGIN_ID

confirm_url = get_confirm_url # XXX: backwards compatibility: must be removed later! yet any code should not rely on this reference

class MultiCheckoutSettlementFailure(PaymentPluginException):
    def __init__(self, message, order_no, back_url, ignorable=False, error_code=None, card_error_code=None, return_code=None):
        super(MultiCheckoutSettlementFailure, self).__init__(message, order_no, back_url, ignorable)
        self.error_code = error_code
        self.card_error_code = card_error_code
        self.return_code = return_code

    @property
    def message(self):
        return '%s (error_code=%s, card_error_code=%s, return_code=%s)' % (
            super(MultiCheckoutSettlementFailure, self).message,
            self.error_code,
            self.card_error_code,
            self.return_code
            )


def back_url(request):
    return request.route_url("payment.secure3d")

def complete_url(request):
    return request.route_url('payment.secure3d_result')


def _selectable_renderer(path_fmt):
    from . import _template
    return _template(path_fmt, type='select_by_organization', for_='payments', plugin_type='payment', plugin_id=PLUGIN_ID)

def _overridable(path, fallback_ua_type=None):
    from . import _template
    return _template(path, type='overridable', for_='payments', plugin_type='payment', plugin_id=PLUGIN_ID, fallback_ua_type=fallback_ua_type)

error_messages = {
    '001002': u'注文が不正です最初からお試しください。',
    '001009': u'購入者氏名が不正です',
    '001012': u'カード番号が不正です',
    '001013': u'カード有効期限が不正です',
    '001014': u'カード名義人が不正です',
    '001018': u'セキュリティコードが不正です',
}


CARD_NUMBER_REGEXP = r'^\d{14,16}$'
CARD_HOLDER_NAME_REGEXP = r'^[A-Z\s]+$'
CARD_EXP_YEAR_REGEXP = r'^\d{2}$'
CARD_EXP_MONTH_REGEXP = r'^\d{2}$'
CARD_SECURE_CODE_REGEXP = r'^\d{3,4}$'

def card_exp_year(form):
    now = datetime.now() # safe to use datetime.now() here
    return [(u'%02d' % (y % 100), '%d' % y) for y in range(now.year, now.year + 20)]

class CardForm(OurForm, SecureFormMixin):
    SECRET_KEY = 'EPj00jpfj8Gx1SjnyLxwBBSQfnQ9DJYe0Ym'

    def _get_translations(self):
        return Translations({
            'This field is required.' : u'入力してください',
            'Not a valid choice' : u'選択してください',
            'Invalid email address.' : u'Emailの形式が正しくありません。',
            'Field must be at least %(min)d characters long.' : u'正しく入力してください。',
            'Field must be between %(min)d and %(max)d characters long.': u'正しく入力してください。',
            'Invalid input.': u'形式が正しくありません。',
        })

    csrf_token = CSRFTokenField()

    card_number = fields.TextField('card',
                                   filters=[ignore_space_hyphen],
                                   validators=[Length(14, 16), Regexp(CARD_NUMBER_REGEXP), Required()])
    exp_year = OurSelectField('exp_year', validators=[Length(2), Regexp(CARD_EXP_YEAR_REGEXP)], choices=card_exp_year)
    exp_month = OurSelectField('exp_month', validators=[Length(2), Regexp(CARD_EXP_MONTH_REGEXP)], choices=[(u'%02d' % i, u'%02d' % i) for i in range(1, 13)])
    card_holder_name = fields.TextField('card_holder_name', filters=[capitalize], validators=[Length(2), Regexp(CARD_HOLDER_NAME_REGEXP)])
    secure_code = fields.TextField('secure_code', validators=[Length(3, 4), Regexp(CARD_SECURE_CODE_REGEXP)])

def get_error_message(request, error_code):
    return u'決済エラー:' + error_messages.get(error_code, u'決済に失敗しました。カードや内容を確認の上再度お試しください。')

@implementer(IPaymentPlugin)
class MultiCheckoutPlugin(object):
    def __init__(self, sales_cancel_moratorium=None):
        if sales_cancel_moratorium is None:
            sales_cancel_moratorium = timedelta()
        self.sales_cancel_moratorium = sales_cancel_moratorium

    def validate_order(self, request, order_like, update=False):
        if order_like.total_amount <= 0:
            raise OrderLikeValidationFailure(u'total_amount is zero', 'order.total_amount')

    def prepare(self, request, cart):
        """ 3Dセキュア認証 """
        notice = cart.sales_segment.auth3d_notice
        request.session['altair.app.ticketing.payments.auth3d_notice'] = notice
        return HTTPFound(location=back_url(request))

    @clear_exc
    def validate(self, request, cart):
        """ 確定前の状態確認 """
        order_no = cart.order_no
        organization = c_models.Organization.query.filter_by(id=cart.organization_id).one()
        multicheckout_api = get_multicheckout_3d_api(request, organization.setting.multicheckout_shop_name)
        status = multicheckout_api.get_order_status_by_order_no(order_no)
        # オーソリ済みであること
        if status is None or status.Status is not None:
            if status.Status == str(MultiCheckoutStatusEnum.Authorized):
                pass
            elif status.Status in (str(MultiCheckoutStatusEnum.Settled), str(MultiCheckoutStatusEnum.PartCanceled)):
                authorized_amount = multicheckout_api.get_authorized_amount(order_no)
                if cart.total_amount > authorized_amount:
                    raise MultiCheckoutSettlementFailure(
                        message='multicheckout status is settled and new total_amount is greater than the previous (%s, %s > %s)' % (order_no, cart.total_amount, authorized_amount),
                        order_no=order_no,
                        back_url=back_url(request)
                        )
            else:
                raise MultiCheckoutSettlementFailure(
                    message='multicheckout status is not authorized (%s)' % order_no,
                    order_no=order_no,
                    back_url=back_url(request)
                    )

    @clear_exc
    def finish(self, request, cart):
        """ 売り上げ確定(3D認証) """
        order = request.session['order']
        order_no = order['order_no']
        card_number = order.get('card_number')
        organization = c_models.Organization.query.filter_by(id=cart.organization_id).one()
        checkout_sales_result = self._finish2_inner(request, cart, override_name=organization.setting.multicheckout_shop_name)

        order_models.Order.query.session.add(cart)
        order = order_models.Order.create_from_cart(cart)
        order.paid_at = datetime.now()
        cart.finish()

        return order

    @clear_exc
    def finish2(self, request, order_like):
        # finish2 では OrderLike から organization を取得する
        organization = c_models.Organization.query.filter_by(id=order_like.organization_id).one()
        self._finish2_inner(request, order_like, override_name=organization.setting.multicheckout_shop_name)

    def _finish2_inner(self, request, order_like, override_name=None):
        multicheckout_api = get_multicheckout_3d_api(request, override_name)
        mc_order_no = order_like.order_no
        authorized_amount = multicheckout_api.get_authorized_amount(mc_order_no)
        amount_to_cancel = 0
        assert authorized_amount is not None
        # order_like.total_amount は Decimal だ...
        amount_to_cancel = authorized_amount - int(order_like.total_amount)

        logger.info('finish2: amount_to_cancel=%d' % amount_to_cancel)

        assert amount_to_cancel >= 0

        try:
            status = multicheckout_api.get_order_status_by_order_no(mc_order_no)
            if status is not None:
                if status.Status is None:
                    status = multicheckout_api.checkout_inquiry(mc_order_no)
                already_settled = status.Status in (str(MultiCheckoutStatusEnum.Settled), str(MultiCheckoutStatusEnum.PartCanceled))
            else:
                already_settled = False # unlikely

            if already_settled:
                logger.info('finish2: order is already settled!')
                if amount_to_cancel == 0:
                    checkout_sales_result = None
                else:
                    checkout_sales_result = multicheckout_api.checkout_sales_part_cancel(mc_order_no, amount_to_cancel, 0)
            else:
                if amount_to_cancel == 0:
                    checkout_sales_result = multicheckout_api.checkout_sales(mc_order_no)
                else:
                    ## 金額変更での売上確定
                    checkout_sales_result = multicheckout_api.checkout_sales_different_amount(mc_order_no, amount_to_cancel)
            if checkout_sales_result is not None and checkout_sales_result.CmnErrorCd != '000000':
                raise MultiCheckoutSettlementFailure(
                    message='finish_secure: generic failure',
                    order_no=order_like.order_no,
                    back_url=back_url(request),
                    error_code=checkout_sales_result.CmnErrorCd,
                    card_error_code=checkout_sales_result.CardErrorCd
                    )
        except Exception as e:
            logger.exception(str(e))
            if isinstance(e, MultiCheckoutSettlementFailure):
                # XXX: これは本当は呼び出し元でやってほしい
                logger.info(u'finish_secure: 決済エラー order_no = %s, error_code = %s' % (e.order_no, e.error_code))
                request.session.flash(get_error_message(request, e.error_code))
            else:
                # MultiCheckoutSettlementFailure 以外の例外 (通信エラーなど)
                logger.exception('multicheckout plugin')
                e = MultiCheckoutSettlementFailure(
                    message='uncaught exception',
                    order_no=order_like.order_no,
                    back_url=back_url(request))
            # KeepAuthFor が MultiCheckoutOrderStatus に設定されていると、実際にはオーソリキャンセルは行われない
            multicheckout_api.checkout_auth_cancel(mc_order_no)
            raise e

        return checkout_sales_result

    def finished(self, request, order):
        """ 売上確定済か判定 """
        organization = c_models.Organization.query.filter_by(id=order.organization_id).one()
        multicheckout_api = get_multicheckout_3d_api(request, organization.setting.multicheckout_shop_name)
        status = multicheckout_api.get_order_status_by_order_no(order.order_no)
        if status is None:
            return False

        if status.Status == str(MultiCheckoutStatusEnum.Settled):
            return True

        if status.Status == str(MultiCheckoutStatusEnum.PartCanceled):
            # 金額が０でないことも確認？
            return True
        return False

    def sales(self, request, order):
        # finish で全部終わっているので後処理不要
        pass

    @clear_exc
    def refresh(self, request, order):
        organization = c_models.Organization.query.filter_by(id=order.organization_id).one()
        multicheckout_api = get_multicheckout_3d_api(request, organization.setting.multicheckout_shop_name)
        real_order_no = order.order_no

        if order.is_inner_channel:
            logger.info('order %s is inner order' % order.order_no)
            return

        if order.delivered_at is not None:
            raise Exception('order %s is already delivered' % order.order_no)

        res = multicheckout_api.checkout_inquiry(real_order_no)
        if res.CmnErrorCd != '000000':
            raise MultiCheckoutSettlementFailure(
                message='checkout_sales_part_cancel: generic failure',
                order_no=order.order_no,
                back_url=back_url(request),
                error_code=res.CmnErrorCd,
                card_error_code=res.CardErrorCd
                )

        if res.Status not in (str(MultiCheckoutStatusEnum.Settled), str(MultiCheckoutStatusEnum.PartCanceled)):
            raise MultiCheckoutSettlementFailure("status of order %s (%s) is neither `Settled' nor `PartCanceled' (%s)" % (order.order_no, real_order_no, res.Status), order.order_no, None)

        if order.total_amount == res.SalesAmount:
            # no need to make requests
            logger.info('total amount (%s) of order %s (%s) is equal to the amount already committed (%s). nothing seems to be done' % (order.total_amount, order.order_no, real_order_no, res.SalesAmount))
            return
        elif order.total_amount > res.SalesAmount:
            # we can't get the amount increased later
            raise MultiCheckoutSettlementFailure('total amount (%s) of order %s (%s) cannot be greater than the amount already committed (%s)' % (order.total_amount, order.order_no, real_order_no, res.SalesAmount), order.order_no, None)

        part_cancel_res = multicheckout_api.checkout_sales_part_cancel(
            real_order_no,
            res.SalesAmount - order.total_amount,
            0)
        if part_cancel_res.CmnErrorCd != '000000':
            raise MultiCheckoutSettlementFailure(
                message='checkout_sales_part_cancel: generic failure',
                order_no=order.order_no,
                back_url=back_url(request),
                error_code=part_cancel_res.CmnErrorCd,
                card_error_code=part_cancel_res.CardErrorCd
                )

    @clear_exc
    def refund(self, request, order, refund_record):
        organization = c_models.Organization.query.filter_by(id=order.organization_id).one()
        multicheckout_api = get_multicheckout_3d_api(request, organization.setting.multicheckout_shop_name)
        real_order_no = order.order_no

        res = multicheckout_api.checkout_inquiry(real_order_no)
        if res.CmnErrorCd != '000000':
            raise MultiCheckoutSettlementFailure(
                message='checkout_sales_part_cancel: generic failure',
                order_no=order.order_no,
                back_url=back_url(request),
                error_code=res.CmnErrorCd,
                card_error_code=res.CardErrorCd
                )

        if res.Status not in (str(MultiCheckoutStatusEnum.Settled), str(MultiCheckoutStatusEnum.PartCanceled)):
            raise MultiCheckoutSettlementFailure("status of order %s (%s) is neither `Settled' nor `PartCanceled' (%s)" % (order.order_no, real_order_no, res.Status), order.order_no, None)

        remaining_amount = order.total_amount - refund_record.refund_total_amount

        if remaining_amount == res.SalesAmount:
            # no need to make requests
            logger.info('as the result of refunding %s, remaining amount (%s) of order %s (%s) will be equal to the amount already committed (%s). nothing seems to be done' % (order.refund_total_amount, remaining_amount, order.order_no, real_order_no, res.SalesAmount))
            return
        elif remaining_amount > res.SalesAmount:
            # we can't get the amount increased later
            raise MultiCheckoutSettlementFailure('remaining amount (%s) of order %s (%s) cannot be greater than the amount already committed (%s)' % (remaining_amount, order.order_no, real_order_no, res.SalesAmount), order.order_no, None)

        # 払い戻すべき金額を渡す必要がある
        part_cancel_res = multicheckout_api.checkout_sales_part_cancel(
            real_order_no,
            order.total_amount - remaining_amount,
            0)
        if part_cancel_res.CmnErrorCd != '000000':
            raise MultiCheckoutSettlementFailure(
                message='checkout_sales_part_cancel: generic failure',
                order_no=order.order_no,
                back_url=back_url(request),
                error_code=part_cancel_res.CmnErrorCd,
                card_error_code=part_cancel_res.CardErrorCd
                )

    @clear_exc
    def cancel(self, request, order):
        # 売り上げキャンセル
        organization = c_models.Organization.query.filter_by(id=order.organization_id).one()
        multicheckout_api = get_multicheckout_3d_api(request, organization.setting.multicheckout_shop_name)
        real_order_no = order.order_no

        order_no = order.order_no
        if request.registry.settings.get('multicheckout.testing', False):
            order_no = order.order_no + "00"

        res = multicheckout_api.checkout_inquiry(real_order_no)
        if res.CmnErrorCd != '000000':
            raise MultiCheckoutSettlementFailure(
                message='checkout_inquiry: generic failure',
                order_no=order.order_no,
                back_url=back_url(request),
                error_code=res.CmnErrorCd,
                card_error_code=res.CardErrorCd
                )

        if res.Status not in (str(MultiCheckoutStatusEnum.Settled), str(MultiCheckoutStatusEnum.PartCanceled)):
            raise MultiCheckoutSettlementFailure("status of order %s (%s) is neither `Settled' nor `PartCanceled' (%s)" % (order.order_no, real_order_no, res.Status), order.order_no, None)

        if self.sales_cancel_moratorium:
            logger.info(u'sales cancellation postponed at least for %d seconds: %s' % (self.sales_cancel_moratorium.seconds, order.order_no))
            multicheckout_api.schedule_cancellation(order_no, datetime.now() + self.sales_cancel_moratorium, 0, 0)
        else:
            logger.info(u'sales cancellation will be done immediately: %s', order.order_no)
            res = multicheckout_api.checkout_sales_part_cancel(order_no, res.SalesAmount, 0)
            if res.CmnErrorCd != '000000':
                raise MultiCheckoutSettlementFailure(
                    message='checkout_sales_cancel: generic failure',
                    order_no=order.order_no,
                    back_url=None,
                    error_code=res.CmnErrorCd,
                    card_error_code=res.CardErrorCd
                    )

    def get_order_info(self, request, order):
        if order.payment_delivery_pair.payment_method.payment_plugin_id != PLUGIN_ID:
            raise ValueError('payment_delivery_method_pair.payment_method.payment_plugin_is not MULTICHECKOUT_PAYMENT_PLUGIN_ID')
        info = None
        organization = order.organization
        multicheckout_api = get_multicheckout_3d_api(request, organization.setting.multicheckout_shop_name)
        recs, _ = multicheckout_api.get_transaction_info(order.order_no)
        for rec in recs:
            if rec['status'] == str(MultiCheckoutStatusEnum.Authorized): # authorization successful
                info = rec
                break
        if info is not None:
            info['ahead_com_name'] = get_multicheckout_ahead_com_name(info['ahead_com_cd'])
        return {
            u'approval_no': info and info['approval_no'],
            u'card_brand': info and info['card_brand'],
            u'ahead_com_code': info and info['ahead_com_cd'],
            u'ahead_com_name': info and info['ahead_com_name'],
            }

def card_number_mask(number):
    """ 下4桁以外をマスク"""
    return "*" * (len(number) - 4) + number[-4:]


@lbr_view_config(context=ICartPayment, name="payment-%d" % PLUGIN_ID, renderer=_overridable("card_confirm.html"))
def confirm_viewlet(context, request):
    """ 確認画面表示
    :param context: ICartPayment
    """

    order_session = request.session["order"]
    return dict(order=order_session, card_number_mask=card_number_mask)

@lbr_view_config(context=IOrderPayment, name="payment-%d" % PLUGIN_ID, renderer=_overridable("card_complete.html"))
def completion_viewlet(context, request):
    """ 完了画面表示
    :param context: IOrderPayment
    """
    return dict()

@lbr_view_config(context=ICompleteMailResource, name="payment-%d" % PLUGIN_ID, renderer=_overridable("card_mail_complete.html", fallback_ua_type='mail'))
@lbr_view_config(context=ILotsElectedMailResource, name="payment-%d" % PLUGIN_ID, renderer=_overridable("checkout_mail_complete.html", fallback_ua_type='mail'))
def completion_payment_mail_viewlet(context, request):
    """ 完了メール表示
    :param context: ICompleteMailPayment
    """
    notice=context.mail_data("P", "notice")
    order=context.order
    return dict(notice=notice, order=order)

@lbr_view_config(context=IOrderCancelMailResource, name="payment-%d" % PLUGIN_ID)
@lbr_view_config(context=ILotsRejectedMailResource, name="payment-%d" % PLUGIN_ID)
@lbr_view_config(context=ILotsAcceptedMailResource, name="payment-%d" % PLUGIN_ID)
def cancel_payment_mail_viewlet(context, request):
    """ 完了メール表示
    :param context: ICompleteMailPayment
    """
    return Response(text=u"＜クレジットカードでお支払いの方＞\n{0}".format(context.mail_data("P", "notice")))

@view_defaults(decorator=with_jquery.not_when(mobile_request))
class MultiCheckoutView(object):
    """ マルチ決済API
    """

    def __init__(self, request):
        self.request = request

    @clear_exc
    @lbr_view_config(route_name='payment.secure3d', request_method="GET", renderer=_selectable_renderer('card_form.html'))
    def card_info_secure3d_form(self):
        """ カード情報入力"""
        get_cart(self.request) # in expectation of raising NoCartError if the cart is already invalidated
        form = CardForm(formdata=self.request.params, csrf_context=self.request.session)
        return dict(form=form)

    @clear_exc
    @lbr_view_config(route_name='payment.secure_code', request_method="POST", renderer=_selectable_renderer('card_form.html'))
    def card_info_secure_code(self):
        """ カード決済処理(セキュアコード)"""
        get_cart(self.request) # in expectation of raising NoCartError if the cart is already invalidated
        form = CardForm(formdata=self.request.params, csrf_context=self.request.session)
        if not form.validate():
            logger.debug("form error %s" % (form.errors,))
            self.request.errors = form.errors
            return dict(form=form)
        assert not form.csrf_token.errors
        order = self._form_to_order(form)
        self.request.session['order'] = order
        self.request.session['secure_type'] = 'secure_code'
        return self._secure_code(order['order_no'], order['card_number'], order['exp_year'], order['exp_month'], order['secure_code'])

    @clear_exc
    @lbr_view_config(route_name='payment.secure3d', request_method="POST", renderer=_selectable_renderer('card_form.html'))
    def card_info_secure3d(self):
        """ カード決済処理(3Dセキュア)
        """
        get_cart(self.request) # in expectation of raising NoCartError if the cart is already invalidated
        multicheckout_api = get_multicheckout_3d_api(self.request)
        form = CardForm(formdata=self.request.params, csrf_context=self.request.session)
        if not form.validate():
            logger.debug("form error %s" % (form.errors,))
            self.request.errors = form.errors
            return dict(form=form)
        assert not form.csrf_token.errors

        order = self._form_to_order(form)

        self.request.session['order'] = order
        if not multicheckout_api.is_enable_secure3d(order['card_number']):
            self.request.session['secure_type'] = 'secure_code'
            return self._secure_code(order['order_no'], order['card_number'], order['exp_year'], order['exp_month'], order['secure_code'])

        self.request.session['secure_type'] = 'secure_3d'
        return self._secure3d(order['card_number'], order['exp_year'], order['exp_month'])

    def _form_to_order(self, form):
        cart = get_cart(self.request)

        # 変換
        card_number = form['card_number'].data
        exp_year = form['exp_year'].data
        exp_month = form['exp_month'].data
        secure_code = form['secure_code'].data
        card_holder_name = form['card_holder_name'].data.upper()

        order = self.request.session['order']
        order.update(
            order_no=cart.order_no,
            card_holder_name=card_holder_name,
            card_number=card_number,
            exp_year=exp_year,
            exp_month=exp_month,
            secure_code=secure_code,
        )

        return order

    def _secure_code(self, order_no, card_number, exp_year, exp_month, secure_code):
        """ セキュアコード認証 """
        multicheckout_api = get_multicheckout_3d_api(self.request)
        cart = get_cart(self.request)
        order = self.request.session['order']
        # 変換
        order_no = order['order_no']

        item_name = api.get_item_name(self.request, cart.name)

        try:
            checkout_auth_result = multicheckout_api.checkout_auth_secure_code(
                cart.order_no,
                item_name, cart.total_amount, 0, order['client_name'], order['email_1'],
                order['card_number'], order['exp_year'] + order['exp_month'], order['card_holder_name'],
                order['secure_code'],
            )

            if checkout_auth_result.CmnErrorCd != '000000':
                raise MultiCheckoutSettlementFailure(
                    message='card_info_secure3d_callback: generic failure',
                    ignorable=True,
                    order_no=order['order_no'],
                    back_url=back_url(self.request),
                    error_code=checkout_auth_result.CmnErrorCd
                    )
        except MultiCheckoutSettlementFailure as e:
            logger.info(u'card_info_secure3d_callback: 決済エラー order_no = %s, error_code = %s' % (e.order_no, e.error_code))
            self.request.session.flash(get_error_message(self.request, e.error_code))
            raise
        except Exception:
            # MultiCheckoutSettlementFailure 以外の例外 (通信エラーなど)
            logger.exception('multicheckout plugin')
            raise MultiCheckoutSettlementFailure(
                message='uncaught exception',
                order_no=order['order_no'],
                back_url=back_url(self.request))

        self.request.session['order'] = order

        return HTTPFound(location=get_confirm_url(self.request))

    def _secure3d(self, card_number, exp_year, exp_month):
        """ セキュア3D """
        multicheckout_api = get_multicheckout_3d_api(self.request)
        cart = get_cart(self.request)
        order = self.request.session['order']
        try:
            enrol = multicheckout_api.secure3d_enrol(cart.order_no, card_number, exp_year, exp_month, cart.total_amount)
        except Exception:
            # MultiCheckoutSettlementFailure 以外の例外 (通信エラーなど)
            logger.exception('multicheckout plugin')
            raise MultiCheckoutSettlementFailure(
                message='uncaught exception',
                order_no=order['order_no'],
                back_url=back_url(self.request))
        if enrol.is_enable_auth_api():
            form=m_h.secure3d_acs_form(self.request, complete_url(self.request), enrol)
            self.request.response.text = form
            return self.request.response
        # elif enrol.is_enable_secure3d():
        #     # セキュア3D認証エラーだが決済APIを利用可能
        #     logger.debug("3d secure is failed ErrorCd = %s RetCd = %s" %(enrol.ErrorCd, enrol.RetCd))
        else:
            # セキュア3D認証エラー
            logger.info(u'secure3d not availble: order_no=%s, error_code=%s, return_code=%s' % (order['order_no'], enrol.ErrorCd, enrol.RetCd))
            self.request.session['secure_type'] = 'secure_code'
            return self._secure_code(order['order_no'], order['card_number'], order['exp_year'], order['exp_month'], order['secure_code'])

    @clear_exc
    @lbr_view_config(route_name='payment.secure3d_result', request_method="POST", renderer=_selectable_renderer("confirm.html"))
    def card_info_secure3d_callback(self):
        """ カード情報入力(3Dセキュア)コールバック
        3Dセキュア認証結果取得
        """
        multicheckout_api = get_multicheckout_3d_api(self.request)
        cart = get_cart(self.request)

        order = self.request.session['order']
        # 変換
        try:
            callback_params = multicheckout_api.get_callback_params()
        except Exception as e:
            raise MultiCheckoutSettlementFailure(
                message='failed to retrieve callback params: %s' % e.message,
                ignorable=True,
                order_no=cart.order_no,
                back_url=back_url(self.request),
                error_code=None,
                return_code=None
                )
        order.update(callback_params)
        order['order_no'] = cart.order_no

        try:
            auth_result = multicheckout_api.secure3d_auth(cart.order_no, callback_params['pares'], callback_params['md'])
            item_name = api.get_item_name(self.request, cart.name)

            # TODO: エラーメッセージ
            #if not auth_result.is_enable_auth_checkout():
            #    return HTTPFound(back_url(self.request))

            # TODO: エラーメッセージ
            if not auth_result.is_enable_secure3d():
                # セキュア3D認証顔面で「キャンセル」ボタンを押したときに
                # ここに遷移し得る
                if auth_result.is_secure3d_continuable():
                    raise MultiCheckoutSettlementFailure(
                        message='card_info_secure3d_callback: secure3d aborted?',
                        ignorable=True,
                        order_no=order['order_no'],
                        back_url=back_url(self.request),
                        error_code=auth_result.ErrorCd,
                        return_code=auth_result.RetCd
                        )
                else:
                    raise MultiCheckoutSettlementFailure(
                        message='card_info_secure3d_callback: secure3d not enabled?',
                        ignorable=True,
                        order_no=order['order_no'],
                        back_url=back_url(self.request),
                        error_code=auth_result.ErrorCd,
                        return_code=auth_result.RetCd
                        )

            logger.debug('call checkout auth')
            checkout_auth_result = multicheckout_api.checkout_auth_secure3d(
                cart.order_no,
                item_name, cart.total_amount, 0, order['client_name'], order['email_1'],
                order['card_number'], order['exp_year'] + order['exp_month'], order['card_holder_name'],
                mvn=auth_result.Mvn, xid=auth_result.Xid, ts=auth_result.Ts,
                eci=auth_result.Eci, cavv=auth_result.Cavv, cavv_algorithm=auth_result.Cavva,
            )
            logger.debug('called checkout auth')
            # TODO: エラーチェック CmnErrorCd CardErrorCd
            if checkout_auth_result.CmnErrorCd != '000000':
                raise MultiCheckoutSettlementFailure(
                    message='card_info_secure3d_callback: generic failure',
                    ignorable=True,
                    order_no=order['order_no'],
                    back_url=back_url(self.request),
                    error_code=checkout_auth_result.CmnErrorCd,
                    card_error_code=checkout_auth_result.CardErrorCd
                    )
        except MultiCheckoutSettlementFailure as e:
            import sys
            logger.info(u'card_info_secure3d_callback', exc_info=sys.exc_info())
            self.request.session.flash(get_error_message(self.request, e.error_code))
            raise
        except Exception:
            # MultiCheckoutSettlementFailure 以外の例外 (通信エラーなど)
            import sys
            logger.info(u'card_info_secure3d_callback', exc_info=sys.exc_info())
            raise MultiCheckoutSettlementFailure(
                message='uncaught exception',
                order_no=order['order_no'],
                back_url=back_url(self.request))

        tran = dict(
            mvn=auth_result.Mvn, xid=auth_result.Xid, ts=auth_result.Ts,
            eci=auth_result.Eci, cavv=auth_result.Cavv, cavv_algorithm=auth_result.Cavva,
        )
        order['tran'] = tran
        self.request.session['order'] = order

        return HTTPFound(location=get_confirm_url(self.request))

def includeme(config):
    # 決済系(マルチ決済)
    sales_cancel_moratorium = config.registry.settings.get('altair.payments.multicheckout.sales_cancel_moratorium')
    if sales_cancel_moratorium is not None:
        sales_cancel_moratorium = parse_time_spec(sales_cancel_moratorium)
    if sales_cancel_moratorium is not None:
        logger.info('sales_cancel_moratorium is set to %d' % sales_cancel_moratorium.seconds)
    else:
        logger.info('sales_cancel_moratorium is not specified')
    config.add_payment_plugin(MultiCheckoutPlugin(sales_cancel_moratorium), PLUGIN_ID)
    config.add_route("payment.secure3d", 'payment/3d')
    config.add_route("payment.secure3d_result", 'payment/3d/result')
    config.add_route("payment.secure_code", 'payment/scode')
    config.scan(__name__)
