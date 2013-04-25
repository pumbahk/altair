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

from ticketing.multicheckout import helpers as m_h
from ticketing.multicheckout import api as multicheckout_api
from ticketing.multicheckout import detect_card_brand, get_card_ahead_com_name
from ticketing.core import models as c_models
from ticketing.payments.interfaces import IPaymentPlugin, IOrderPayment
from ticketing.cart.interfaces import ICartPayment
from ticketing.mails.interfaces import ICompleteMailPayment, IOrderCancelMailPayment
from ticketing.formhelpers import (
    Required,
    Translations,
    ignore_space_hyphen,
    capitalize,
)
from .models import DBSession
from .. import logger
from ticketing.cart import api
from ticketing.cart.exceptions import NoCartError
from ticketing.cart.selectable_renderer import selectable_renderer
from ..exceptions import PaymentPluginException
from ticketing.views import mobile_request
from ticketing.fanstatic import with_jquery
from ticketing.payments.api import get_cart

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

def get_order_no(request, cart):
    
    if request.registry.settings.get('multicheckout.testing', False):
        #return "%012d" % cart.id + "00"
        return cart.order_no + "00"
    return cart.order_no

@implementer(IPaymentPlugin)
class MultiCheckoutPlugin(object):
    def prepare(self, request, cart):
        """ 3Dセキュア認証 """
        return HTTPFound(location=back_url(request))

    def finish(self, request, cart):
        """ 売り上げ確定(3D認証) """
        order = request.session['order']
        order_no = order['order_no']
        card_brand = detect_card_brand(request, order['card_number'])

        checkout_sales_result = multicheckout_api.checkout_sales(
            request, get_order_no(request, cart),
        )
        
        if checkout_sales_result.CmnErrorCd != '000000':
            logger.info(u'finish_secure: 決済エラー order_no = %s, error_code = %s' % (order_no, checkout_sales_result.CmnErrorCd))
            multicheckout_api.checkout_auth_cancel(request, get_order_no(request, cart))
            request.session.flash(get_error_message(request, checkout_sales_result.CmnErrorCd))
            transaction.commit()
            raise MultiCheckoutSettlementFailure(
                message='finish_secure: generic failure',
                order_no=order_no,
                back_url=back_url(request),
                error_code=checkout_sales_result.CmnErrorCd
                )
        ahead_com_code = checkout_sales_result.AheadComCd

        order = c_models.Order.create_from_cart(cart)
        order.card_brand = card_brand
        order.card_ahead_com_code = ahead_com_code
        order.card_ahead_com_name = get_card_ahead_com_name(request, ahead_com_code)
        order.multicheckout_approval_no = checkout_sales_result.ApprovalNo
        order.paid_at = datetime.now()
        cart.finish()

        return order

def card_number_mask(number):
    """ 下4桁以外をマスク"""
    return "*" * (len(number) - 4) + number[-4:]


@view_config(context=ICartPayment, name="payment-%d" % PAYMENT_ID, renderer="ticketing.payments.plugins:templates/card_confirm.html")
def confirm_viewlet(context, request):
    """ 確認画面表示 
    :param context: ICartPayment
    """

    order_session = request.session["order"]
    logger.debug("order_session %s" % order_session)
    return dict(order=order_session, card_number_mask=card_number_mask)

@view_config(context=IOrderPayment, name="payment-%d" % PAYMENT_ID, renderer="ticketing.payments.plugins:templates/card_complete.html")
def completion_viewlet(context, request):
    """ 完了画面表示 
    :param context: IOrderPayment
    """
    return dict()

@view_config(context=ICompleteMailPayment, name="payment-%d" % PAYMENT_ID, renderer="ticketing.payments.plugins:templates/card_mail_complete.html")
def completion_payment_mail_viewlet(context, request):
    """ 完了メール表示
    :param context: ICompleteMailPayment
    """
    notice=context.mail_data("notice")
    return dict(notice=notice)

@view_config(context=IOrderCancelMailPayment, name="payment-%d" % PAYMENT_ID)
def cancel_payment_mail_viewlet(context, request):
    """ 完了メール表示
    :param context: ICompleteMailPayment
    """
    return Response(context.mail_data("notice"))

@view_defaults(decorator=with_jquery.not_when(mobile_request))
class MultiCheckoutView(object):
    """ マルチ決済API
    """

    def __init__(self, request):
        self.request = request

    @view_config(route_name='payment.secure3d', request_method="GET", renderer=selectable_renderer('carts/%(membership)s/card_form.html'))
    @view_config(route_name='payment.secure3d', request_type='altair.mobile.interfaces.IMobileRequest', request_method="GET", renderer=selectable_renderer('carts_mobile/%(membership)s/card_form.html'))
    def card_info_secure3d_form(self):
        """ カード情報入力"""
        form = CardForm(formdata=self.request.params, csrf_context=self.request.session)
        return dict(form=form)

    @view_config(route_name='payment.secure_code', request_method="POST", renderer=selectable_renderer('carts/%(membership)s/card_form.html'))
    @view_config(route_name='payment.secure_code', request_type='altair.mobile.interfaces.IMobileRequest', request_method="POST", renderer=selectable_renderer('carts_mobile/%(membership)s/card_form.html'))
    def card_info_secure_code(self):
        """ カード決済処理(セキュアコード)"""
        form = CardForm(formdata=self.request.params, csrf_context=self.request.session)
        if not form.validate():
            logger.debug("form error %s" % (form.errors,))
            self.request.errors = form.errors
            return dict(form=form)
        assert not form.csrf_token.errors
        cart = get_cart(self.request)
        order = self._form_to_order(form)

        self.request.session['order'] = order
        self.request.session['secure_type'] = 'secure_code'
        return self._secure_code(order['order_no'], order['card_number'], order['exp_year'], order['exp_month'], order['secure_code'])

    @view_config(route_name='payment.secure3d', request_method="POST", renderer=selectable_renderer('carts/%(membership)s/card_form.html'))
    @view_config(route_name='payment.secure3d', request_type='altair.mobile.interfaces.IMobileRequest', request_method="POST", renderer=selectable_renderer('carts_mobile/%(membership)s/card_form.html'))
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


        checkout_auth_result = multicheckout_api.checkout_auth_secure_code(
            self.request, get_order_no(self.request, cart),
            item_name, cart.total_amount, 0, order['client_name'], order['email_1'],
            order['card_number'], order['exp_year'] + order['exp_month'], order['card_holder_name'],
            order['secure_code'],
        )

        if checkout_auth_result.CmnErrorCd != '000000':
            logger.info(u'card_info_secure3d_callback: 決済エラー order_no = %s, error_code = %s' % (order['order_no'], checkout_auth_result.CmnErrorCd))
            self.request.session.flash(get_error_message(self.request, checkout_auth_result.CmnErrorCd))
            raise MultiCheckoutSettlementFailure(
                message='card_info_secure3d_callback: generic failure',
                order_no=order['order_no'],
                back_url=back_url(self.request),
                error_code=checkout_auth_result.CmnErrorCd
                )

        self.request.session['order'] = order

        #DBSession.add(checkout_auth_result)

        return HTTPFound(location=confirm_url(self.request))


    def _secure3d(self, card_number, exp_year, exp_month):
        """ セキュア3D """
        cart = get_cart(self.request)
        order = self.request.session['order']
        enrol = multicheckout_api.secure3d_enrol(self.request, get_order_no(self.request, cart), card_number, exp_year, exp_month, cart.total_amount)
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
        form = CardForm(csrf_context=self.request.session)
        return dict(form=form)

    @view_config(route_name='cart.secure3d_result', request_method="POST", renderer=selectable_renderer("carts/%(membership)s/confirm.html"))
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
            logger.info(u'card_info_secure3d_callback: 決済エラー order_no = %s, error_code = %s' % (checkout_auth_result.OrderNo, checkout_auth_result.CmnErrorCd))
            self.request.session.flash(get_error_message(self.request, checkout_auth_result.CmnErrorCd))
            raise MultiCheckoutSettlementFailure(
                message='card_info_secure3d_callback: generic failure',
                order_no=order['order_no'],
                back_url=back_url(self.request),
                error_code=checkout_auth_result.CmnErrorCd
                )

        tran = dict(
            mvn=auth_result.Mvn, xid=auth_result.Xid, ts=auth_result.Ts,
            eci=auth_result.Eci, cavv=auth_result.Cavv, cavv_algorithm=auth_result.Cavva,
        )
        order['tran'] = tran
        self.request.session['order'] = order

        #DBSession.add(checkout_auth_result)

        return HTTPFound(location=confirm_url(self.request))
