# -*- coding:utf-8 -*-
import logging
import transaction
from datetime import datetime
from zope.interface import implementer
from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound

from wtforms import fields
from wtforms.ext.csrf.session import SessionSecureForm
from wtforms.validators import Regexp, Length

from altair.multicheckout import helpers as m_h
from altair.multicheckout import api as multicheckout_api
from altair.multicheckout import detect_card_brand, get_card_ahead_com_name
from altair.multicheckout.models import (
    MultiCheckoutOrderStatus,
    MultiCheckoutStatusEnum,
)
from altair.app.ticketing.core import models as c_models
from altair.app.ticketing.payments.interfaces import IPaymentPlugin, IOrderPayment
from altair.app.ticketing.cart.interfaces import ICartPayment
from altair.app.ticketing.mails.interfaces import ICompleteMailPayment, IOrderCancelMailPayment
from altair.app.ticketing.mails.interfaces import ILotsAcceptedMailPayment
from altair.app.ticketing.mails.interfaces import ILotsElectedMailPayment
from altair.app.ticketing.mails.interfaces import ILotsRejectedMailPayment
from altair.formhelpers import (
    Required,
    Translations,
    ignore_space_hyphen,
    capitalize,
)

from .models import DBSession
from .. import logger
from altair.app.ticketing.cart import api
from altair.app.ticketing.cart.views import is_organization_rs # XXX
from altair.app.ticketing.cart.exceptions import NoCartError, InvalidCartStatusError
from altair.app.ticketing.cart.selectable_renderer import selectable_renderer
from ..exceptions import PaymentPluginException
from altair.app.ticketing.views import mobile_request
from altair.app.ticketing.fanstatic import with_jquery
from altair.app.ticketing.payments.api import get_cart

logger = logging.getLogger(__name__)

from . import MULTICHECKOUT_PAYMENT_PLUGIN_ID as PAYMENT_ID

class MultiCheckoutSettlementFailure(PaymentPluginException):
    def __init__(self, message, order_no, back_url, error_code=None, return_code=None):
        super(MultiCheckoutSettlementFailure, self).__init__(message, order_no, back_url)
        self.error_code = error_code
        self.return_code = return_code

def back_url(request):
    return request.route_url("payment.secure3d")

def confirm_url(request):
    return request.session.get('payment_confirm_url')
    #return request.route_url('payment.confirm')

def complete_url(request):
    return request.route_url('cart.secure3d_result')

def includeme(config):
    # 決済系(マルチ決済)
    config.add_payment_plugin(MultiCheckoutPlugin(), PAYMENT_ID)
    config.add_route("payment.secure3d", 'payment/3d')
    config.add_route("cart.secure3d_result", 'payment/3d/result')
    config.add_route("payment.secure_code", 'payment/scode')
    config.scan(__name__)


error_messages = {
    '001002': u'注文が不正です最初からお試しください。',
    '001009': u'購入者氏名が不正です',
    '001012': u'カード番号が不正です',
    '001013': u'カード有効期限が不正です',
    '001014': u'カード名義人が不正です',
    '001018': u'セキュリティコードが不正です',
}


class CSRFSecureForm(SessionSecureForm):
    SECRET_KEY = 'EPj00jpfj8Gx1SjnyLxwBBSQfnQ9DJYe0Ym'

CARD_NUMBER_REGEXP = r'^\d{14,16}$'
CARD_HOLDER_NAME_REGEXP = r'^[A-Z\s]+$'
CARD_EXP_YEAR_REGEXP = r'^\d{2}$'
CARD_EXP_MONTH_REGEXP = r'^\d{2}$'
CARD_SECURE_CODE_REGEXP = r'^\d{3,4}$'

class CardForm(CSRFSecureForm):
    def _get_translations(self):
        return Translations({
            'This field is required.' : u'入力してください',
            'Not a valid choice' : u'選択してください',
            'Invalid email address.' : u'Emailの形式が正しくありません。',
            'Field must be at least %(min)d characters long.' : u'正しく入力してください。',
            'Field must be between %(min)d and %(max)d characters long.': u'正しく入力してください。',
            'Invalid input.': u'形式が正しくありません。',
        })

    card_number = fields.TextField('card',
                                   filters=[ignore_space_hyphen], 
                                   validators=[Length(14, 16), Regexp(CARD_NUMBER_REGEXP), Required()])
    exp_year = fields.TextField('exp_year', validators=[Length(2), Regexp(CARD_EXP_YEAR_REGEXP)])
    exp_month = fields.TextField('exp_month', validators=[Length(2), Regexp(CARD_EXP_MONTH_REGEXP)])
    card_holder_name = fields.TextField('card_holder_name', filters=[capitalize], validators=[Length(2), Regexp(CARD_HOLDER_NAME_REGEXP)])
    secure_code = fields.TextField('secure_code', validators=[Length(3, 4), Regexp(CARD_SECURE_CODE_REGEXP)])


def get_error_message(request, error_code):
    return u'決済エラー:' + error_messages.get(error_code, u'決済に失敗しました。カードや内容を確認の上再度お試しください。')

def get_order_no(request, order_like):
    if request.registry.settings.get('multicheckout.testing', False):
        return order_like.order_no + "00"
    return order_like.order_no

@implementer(IPaymentPlugin)
class MultiCheckoutPlugin(object):
    def prepare(self, request, cart):
        """ 3Dセキュア認証 """
        notice = cart.sales_segment.auth3d_notice
        request.session['altair.app.ticketing.payments.auth3d_notice'] = notice
        return HTTPFound(location=back_url(request))

    def validate(self, request, cart):
        """ 確定前の状態確認 """
        order_no = get_order_no(request, cart)
        status = MultiCheckoutOrderStatus.by_order_no(order_no)
        # オーソリ済みであること
        if status is None or status.Status != str(MultiCheckoutStatusEnum.Authorized):
            logger.debug('multicheckout status is not authorized (%s)' % order_no)
            raise MultiCheckoutSettlementFailure(
                message='multicheckout status is not authorized (%s)' % order_no,
                order_no=order_no,
                back_url=back_url(request)
                )

    def finish(self, request, cart):
        """ 売り上げ確定(3D認証) """
        order = request.session['order']
        order_no = order['order_no']
        card_brand = None
        card_number = order.get('card_number')
        if card_number:
            card_brand = detect_card_brand(request, card_number)

        try:
            if not cart.has_different_amount:
                checkout_sales_result = multicheckout_api.checkout_sales(
                    request, get_order_no(request, cart),
                )
            else:
                ## 金額変更での売上確定
                checkout_sales_result = multicheckout_api.checkout_sales_different_amount(
                    request, get_order_no(request, cart), cart.different_amount,
                )
            if checkout_sales_result.CmnErrorCd != '000000':
                raise MultiCheckoutSettlementFailure(
                    message='finish_secure: generic failure',
                    order_no=order_no,
                    back_url=back_url(request),
                    error_code=checkout_sales_result.CmnErrorCd
                    )
        except MultiCheckoutSettlementFailure as e:
            # XXX: これは本当は呼び出し元でやってほしい
            logger.info(u'finish_secure: 決済エラー order_no = %s, error_code = %s' % (e.order_no, e.error_code))
            request.session.flash(get_error_message(request, e.error_code))
            raise
        except Exception:
            # MultiCheckoutSettlementFailure 以外の例外 (通信エラーなど)
            logger.exception('multicheckout plugin')
            raise MultiCheckoutSettlementFailure(
                message='uncaught exception',
                order_no=order_no,
                back_url=back_url(request))
        finally:
            # checkout_auth_cancel が失敗する可能性があるので、try-finally必要
            try:
                if cart.has_different_amount:
                    ## 抽選特有の事情により、キャンセルは管理画面から行う
                    pass
                else:
                    multicheckout_api.checkout_auth_cancel(request, get_order_no(request, cart))
            finally:
                transaction.commit()

        ahead_com_code = checkout_sales_result.AheadComCd

        c_models.Order.query.session.add(cart)
        order = c_models.Order.create_from_cart(cart)
        order.card_brand = card_brand
        order.card_ahead_com_code = ahead_com_code
        order.card_ahead_com_name = get_card_ahead_com_name(request, ahead_com_code)
        order.multicheckout_approval_no = checkout_sales_result.ApprovalNo
        order.paid_at = datetime.now()
        cart.finish()

        return order

    def finished(self, request, order):
        """ 売上確定済か判定 """

        status = DBSession.query(MultiCheckoutOrderStatus).filter(
            MultiCheckoutOrderStatus.OrderNo == order.order_no
        ).first()
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

    def refresh(self, request, order):
        real_order_no = get_order_no(request, order)

        if order.delivered_at is not None:
            raise Exception('order %s is already delivered' % order.order_no)

        res = multicheckout_api.checkout_inquiry(request, real_order_no)
        if res.CmnErrorCd != '000000':
            raise MultiCheckoutSettlementFailure(
                message='checkout_sales_part_cancel: generic failure',
                order_no=order.order_no,
                back_url=back_url(self.request),
                error_code=part_cancel_res.CmnErrorCd
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
            request,
            real_order_no,
            res.SalesAmount - order.total_amount,
            0)
        if part_cancel_res.CmnErrorCd != '000000':
            raise MultiCheckoutSettlementFailure(
                message='checkout_sales_part_cancel: generic failure',
                order_no=order.order_no,
                back_url=back_url(self.request),
                error_code=part_cancel_res.CmnErrorCd
                )


def card_number_mask(number):
    """ 下4桁以外をマスク"""
    return "*" * (len(number) - 4) + number[-4:]


@view_config(context=ICartPayment, name="payment-%d" % PAYMENT_ID, renderer="altair.app.ticketing.payments.plugins:templates/card_confirm.html")
def confirm_viewlet(context, request):
    """ 確認画面表示 
    :param context: ICartPayment
    """

    order_session = request.session["order"]
    return dict(order=order_session, card_number_mask=card_number_mask)

@view_config(context=IOrderPayment, name="payment-%d" % PAYMENT_ID, renderer="altair.app.ticketing.payments.plugins:templates/card_complete.html")
def completion_viewlet(context, request):
    """ 完了画面表示 
    :param context: IOrderPayment
    """
    return dict()

@view_config(context=ICompleteMailPayment, name="payment-%d" % PAYMENT_ID, renderer="altair.app.ticketing.payments.plugins:templates/card_mail_complete.html")
@view_config(context=ILotsElectedMailPayment, name="payment-%d" % PAYMENT_ID, renderer="altair.app.ticketing.payments.plugins:templates/checkout_mail_complete.html")
def completion_payment_mail_viewlet(context, request):
    """ 完了メール表示
    :param context: ICompleteMailPayment
    """
    notice=context.mail_data("notice")
    order=context.order
    return dict(notice=notice, order=order)

@view_config(context=IOrderCancelMailPayment, name="payment-%d" % PAYMENT_ID)
@view_config(context=ILotsRejectedMailPayment, name="payment-%d" % PAYMENT_ID)
@view_config(context=ILotsAcceptedMailPayment, name="payment-%d" % PAYMENT_ID)
def cancel_payment_mail_viewlet(context, request):
    """ 完了メール表示
    :param context: ICompleteMailPayment
    """
    return Response(text=u"＜クレジットカードでお支払いの方＞\n{0}".format(context.mail_data("notice")))

@view_defaults(decorator=with_jquery.not_when(mobile_request))
class MultiCheckoutView(object):
    """ マルチ決済API
    """

    def __init__(self, request):
        self.request = request

    @view_config(route_name='payment.secure3d', request_method="GET", renderer=selectable_renderer('%(membership)s/pc/card_form.html'))
    @view_config(route_name='payment.secure3d', request_method="GET", request_type='altair.mobile.interfaces.IMobileRequest', renderer=selectable_renderer('%(membership)s/mobile/card_form.html'))
    @view_config(route_name='payment.secure3d', request_method="GET", request_type="altair.mobile.interfaces.ISmartphoneRequest", custom_predicates=(is_organization_rs, ), renderer=selectable_renderer("RT/smartphone/card_form.html"))
    def card_info_secure3d_form(self):
        """ カード情報入力"""
        form = CardForm(formdata=self.request.params, csrf_context=self.request.session)
        return dict(form=form)

    @view_config(route_name='payment.secure_code', request_method="POST", renderer=selectable_renderer('%(membership)s/pc/card_form.html'))
    @view_config(route_name='payment.secure_code', request_method="POST", request_type='altair.mobile.interfaces.IMobileRequest', renderer=selectable_renderer('%(membership)s/mobile/card_form.html'))
    @view_config(route_name='payment.secure_code', request_method="POST", request_type="altair.mobile.interfaces.ISmartphoneRequest", custom_predicates=(is_organization_rs, ), renderer=selectable_renderer('%(membership)s/pc/card_form.html'))
    def card_info_secure_code(self):
        """ カード決済処理(セキュアコード)"""
        form = CardForm(formdata=self.request.params, csrf_context=self.request.session)
        if not form.validate():
            logger.debug("form error %s" % (form.errors,))
            self.request.errors = form.errors
            return dict(form=form)
        assert not form.csrf_token.errors
        get_cart(self.request)
        order = self._form_to_order(form)

        self.request.session['order'] = order
        self.request.session['secure_type'] = 'secure_code'
        return self._secure_code(order['order_no'], order['card_number'], order['exp_year'], order['exp_month'], order['secure_code'])

    @view_config(route_name='payment.secure3d', request_method="POST", renderer=selectable_renderer('%(membership)s/pc/card_form.html'))
    @view_config(route_name='payment.secure3d', request_method="POST", request_type='altair.mobile.interfaces.IMobileRequest', renderer=selectable_renderer('%(membership)s/mobile/card_form.html'))
    @view_config(route_name='payment.secure3d', request_method="POST", request_type="altair.mobile.interfaces.ISmartphoneRequest", custom_predicates=(is_organization_rs, ), renderer=selectable_renderer("RT/smartphone/card_form.html"))
    def card_info_secure3d(self):
        """ カード決済処理(3Dセキュア)
        """
        form = CardForm(formdata=self.request.params, csrf_context=self.request.session)
        if not form.validate():
            logger.debug("form error %s" % (form.errors,))
            self.request.errors = form.errors
            return dict(form=form)
        assert not form.csrf_token.errors
        get_cart(self.request) # raises NoCartError if no cart is bound to the request

        order = self._form_to_order(form)

        self.request.session['order'] = order
        if not multicheckout_api.is_enable_secure3d(self.request, order['card_number']):
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

        order = self.request.session.get('order', dict())
        order.update(
            order_no=get_order_no(self.request, cart),
            card_holder_name=card_holder_name,
            card_number=card_number,
            exp_year=exp_year,
            exp_month=exp_month,
            secure_code=secure_code,
        )

        return order

    def _secure_code(self, order_no, card_number, exp_year, exp_month, secure_code):
        """ セキュアコード認証 """
        cart = get_cart(self.request)
        order = self.request.session['order']
        # 変換
        order_no = order['order_no']

        item_name = api.get_item_name(self.request, cart.name)

        try:
            checkout_auth_result = multicheckout_api.checkout_auth_secure_code(
                self.request, get_order_no(self.request, cart),
                item_name, cart.total_amount, 0, order['client_name'], order['email_1'],
                order['card_number'], order['exp_year'] + order['exp_month'], order['card_holder_name'],
                order['secure_code'],
            )

            if checkout_auth_result.CmnErrorCd != '000000':
                raise MultiCheckoutSettlementFailure(
                    message='card_info_secure3d_callback: generic failure',
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

        return HTTPFound(location=confirm_url(self.request))

    def _secure3d(self, card_number, exp_year, exp_month):
        """ セキュア3D """
        cart = get_cart(self.request)
        order = self.request.session['order']
        try:
            enrol = multicheckout_api.secure3d_enrol(self.request, get_order_no(self.request, cart), card_number, exp_year, exp_month, cart.total_amount)
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
            logger.debug("3d secure is failed ErrorCd = %s RetCd = %s" %(enrol.ErrorCd, enrol.RetCd))
            self.request.session['secure_type'] = 'secure_code'
            return self._secure_code(order['order_no'], order['card_number'], order['exp_year'], order['exp_month'], order['secure_code'])

    @view_config(route_name='cart.secure3d_result', request_method="POST", renderer=selectable_renderer("%(membership)s/pc/confirm.html"))
    def card_info_secure3d_callback(self):
        """ カード情報入力(3Dセキュア)コールバック
        3Dセキュア認証結果取得
        """
        cart = get_cart(self.request)

        order = self.request.session['order']
        # 変換
        pares = multicheckout_api.get_pares(self.request)
        md = multicheckout_api.get_md(self.request)
        order['pares'] = pares
        order['md'] = md
        order['order_no'] = get_order_no(self.request, cart)

        try:
            auth_result = multicheckout_api.secure3d_auth(self.request, get_order_no(self.request, cart), pares, md)
            item_name = api.get_item_name(self.request, cart.name)

            # TODO: エラーメッセージ
            #if not auth_result.is_enable_auth_checkout():
            #    return HTTPFound(back_url(self.request))

            # TODO: エラーメッセージ
            if not auth_result.is_enable_secure3d():
                raise MultiCheckoutSettlementFailure(
                    message='card_info_secure3d_callback: secure3d not enabled?',
                    order_no=order['order_no'],
                    back_url=back_url(self.request),
                    error_code=auth_result.ErrorCd,
                    return_code=auth_result.RetCd
                    )

            logger.debug('call checkout auth')
            checkout_auth_result = multicheckout_api.checkout_auth_secure3d(
                self.request, get_order_no(self.request, cart),
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

        tran = dict(
            mvn=auth_result.Mvn, xid=auth_result.Xid, ts=auth_result.Ts,
            eci=auth_result.Eci, cavv=auth_result.Cavv, cavv_algorithm=auth_result.Cavva,
        )
        order['tran'] = tran
        self.request.session['order'] = order

        return HTTPFound(location=confirm_url(self.request))
