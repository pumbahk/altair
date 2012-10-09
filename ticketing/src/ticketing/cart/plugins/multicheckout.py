# -*- coding:utf-8 -*-
import logging
from datetime import datetime
from zope.interface import implementer
from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from ticketing.multicheckout import helpers as m_h
from ticketing.multicheckout import api as multicheckout_api
from ticketing.core import models as c_models
from ..interfaces import IPaymentPlugin, ICartPayment, IOrderPayment, ICompleteMailPayment, IOrderCancelMailPayment
from .models import DBSession
from .. import schemas
from .. import logger
from .. import helpers as h
from .. import api
from ..exceptions import NoCartError
from ticketing.cart.selectable_renderer import selectable_renderer

logger = logging.getLogger(__name__)

PLUGIN_ID = 1

def includeme(config):
    # 決済系(マルチ決済)
    config.add_payment_plugin(MultiCheckoutPlugin(), PLUGIN_ID)
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

def get_error_message(request, error_code):
    return u'決済エラー:' + error_messages.get(error_code, u'決済に失敗しました。カードや内容を確認の上再度お試しください。')

def get_order_no(request, cart):
    
    if request.registry.settings.get('multicheckout.testing', False):
        return "%012d" % cart.id + "00"
    return cart.order_no

@implementer(IPaymentPlugin)
class MultiCheckoutPlugin(object):
    def prepare(self, request, cart):
        """ 3Dセキュア認証 """
        return HTTPFound(location=request.route_url("payment.secure3d"))

    def finish(self, request, cart):
        if request.session.get('secure_type') == 'secure_code':
            return self.finish_secure_code(request, cart)
        elif request.session.get('secure_type') == 'secure_3d':
            return self.finish_secure_3d(request, cart)
        else:
            assert False, u"unknown secure_type %s" % request.session.get('secure_type')

    def finish_secure_3d(self, request, cart):
        """ 売り上げ確定(3D認証) """
        order = request.session['order']
        order_no = order['order_no']
        pares = order['pares']
        md = order['md']
        tran = order['tran']
        item_name = api.get_item_name(request, cart.performance)

        checkout_sales_result = multicheckout_api.checkout_sales_secure3d(
            request, get_order_no(request, cart),
            item_name, cart.total_amount, 0, order['client_name'], order.get('mail_address', ''),
            order['card_number'], order['exp_year'] + order['exp_month'], order['card_holder_name'],
            mvn=tran['mvn'], xid=tran['xid'], ts=tran['ts'],
            eci=tran['eci'], cavv=tran['cavv'], cavv_algorithm=tran['cavv_algorithm'],
        )

        if checkout_sales_result.CmnErrorCd != '000000':
            logger.info(u'finish_secure_3d: 決済エラー order_no = %s, error_code = %s' % (order_no, checkout_sales_result.CmnErrorCd))
            multicheckout_api.checkout_auth_cancel(request, get_order_no(request, cart))
            request.session.flash(get_error_message(request, checkout_sales_result.CmnErrorCd))
            raise HTTPFound(location=request.route_url('payment.secure3d'))

        DBSession.add(checkout_sales_result)

        order = c_models.Order.create_from_cart(cart)
        order.multicheckout_approval_no = checkout_sales_result.ApprovalNo
        order.paid_at = datetime.now()
        cart.finish()

        return order

    def finish_secure_code(self, request, cart):
        """ 売り上げ確定 (セキュアコード認証) """
        order = request.session['order']
        order_no = order['order_no']
        item_name = api.get_item_name(request, cart.performance)

        checkout_sales_result = multicheckout_api.checkout_sales_secure_code(
            request, get_order_no(request, cart),
            item_name, cart.total_amount, 0, order['client_name'], order.get('mail_address', ''),
            order['card_number'], order['exp_year'] + order['exp_month'], order['card_holder_name'],
            order['secure_code'],
        )

        if checkout_sales_result.CmnErrorCd != '000000':
            logger.info(u'finish_secure_code: 決済エラー order_no = %s, error_code = %s' % (order_no, checkout_sales_result.CmnErrorCd))
            multicheckout_api.checkout_auth_cancel(request, get_order_no(request, cart))
            request.session.flash(get_error_message(request, checkout_sales_result.CmnErrorCd))
            raise HTTPFound(location=request.route_url('payment.secure3d'))

        DBSession.add(checkout_sales_result)

        order = c_models.Order.create_from_cart(cart)
        order.multicheckout_approval_no = checkout_sales_result.ApprovalNo
        order.paid_at = datetime.now()
        cart.finish()

        return order

def card_number_mask(number):
    """ 下4桁以外をマスク"""
    return "*" * (len(number) - 4) + number[-4:]

PAYMENT_ID = 1
@view_config(context=ICartPayment, name="payment-%d" % PAYMENT_ID, renderer="ticketing.cart.plugins:templates/card_confirm.html")
def confirm_viewlet(context, request):
    """ 確認画面表示 
    :param context: ICartPayment
    """

    order_session = request.session["order"]
    logger.debug("order_session %s" % order_session)
    return dict(order=order_session, card_number_mask=card_number_mask)

@view_config(context=IOrderPayment, name="payment-%d" % PAYMENT_ID, renderer="ticketing.cart.plugins:templates/card_complete.html")
def completion_viewlet(context, request):
    """ 完了画面表示 
    :param context: IOrderPayment
    """
    return dict()

@view_config(context=ICompleteMailPayment, name="payment-%d" % PAYMENT_ID)
             # renderer="ticketing.cart.plugins:templates/card_payment_mail_complete.html")
def completion_payment_mail_viewlet(context, request):
    """ 完了メール表示
    :param context: ICompleteMailPayment
    """
    notice=context.mail_data("notice")
    return Response(u"""
＜クレジットカードでのお支払いの方＞

予約成立と同時に、ご登録のクレジットカードにて自動的に決済手続きを行わせて頂きます。

お申込の取消、公演日・席種・枚数等の変更は出来ませんのでご注意ください。

クレジットカードの引き落としは、カード会社によって異なります。詳細はご利用のカード会社へお問い合わせください。
%s
""" % notice)

@view_config(context=IOrderCancelMailPayment, name="payment-%d" % PAYMENT_ID)
def cancel_payment_mail_viewlet(context, request):
    """ 完了メール表示
    :param context: ICompleteMailPayment
    """
    return Response(context.mail_data("notice"))

class MultiCheckoutView(object):
    """ マルチ決済API
    """

    def __init__(self, request):
        self.request = request

    @view_config(route_name='payment.secure3d', request_method="GET", renderer=selectable_renderer('carts/%(membership)s/card_form.html'))
    @view_config(route_name='payment.secure3d', request_type='ticketing.cart.interfaces.IMobileRequest', request_method="GET", renderer=selectable_renderer('carts_mobile/%(membership)s/card_form.html'))
    def card_info_secure3d_form(self):
        """ カード情報入力"""
        form = schemas.CardForm(formdata=self.request.params, csrf_context=self.request.session)
        return dict(form=form)

    @view_config(route_name='payment.secure_code', request_method="POST", renderer=selectable_renderer('carts/%(membership)s/card_form.html'))
    @view_config(route_name='payment.secure_code', request_type='ticketing.cart.interfaces.IMobileRequest', request_method="POST", renderer=selectable_renderer('carts_mobile/%(membership)s/card_form.html'))
    def card_info_secure_code(self):
        """ カード決済処理(セキュアコード)"""
        form = schemas.CardForm(formdata=self.request.params, csrf_context=self.request.session)
        if not form.validate():
            logger.debug("form error %s" % (form.errors,))
            self.request.errors = form.errors
            return dict(form=form)
        assert not form.csrf_token.errors
        if not api.has_cart(self.request):
            raise NoCartError()
        cart = api.get_cart(self.request)
        order = self._form_to_order(form)

        self.request.session['order'] = order
        self.request.session['secure_type'] = 'secure_code'
        return self._secure_code(order['order_no'], order['card_number'], order['exp_year'], order['exp_month'], order['secure_code'])

    @view_config(route_name='payment.secure3d', request_method="POST", renderer=selectable_renderer('carts/%(membership)s/card_form.html'))
    @view_config(route_name='payment.secure3d', request_type='ticketing.cart.interfaces.IMobileRequest', request_method="POST", renderer=selectable_renderer('carts_mobile/%(membership)s/card_form.html'))
    def card_info_secure3d(self):
        """ カード決済処理(3Dセキュア)
        """
        form = schemas.CardForm(formdata=self.request.params, csrf_context=self.request.session)
        if not form.validate():
            logger.debug("form error %s" % (form.errors,))
            self.request.errors = form.errors
            return dict(form=form)
        assert not form.csrf_token.errors
        if not api.has_cart(self.request):
            raise NoCartError()

        order = self._form_to_order(form)

        self.request.session['order'] = order
        if not multicheckout_api.is_enable_secure3d(self.request, order['card_number']):
            self.request.session['secure_type'] = 'secure_code'
            return self._secure_code(order['order_no'], order['card_number'], order['exp_year'], order['exp_month'], order['secure_code'])

        self.request.session['secure_type'] = 'secure_3d'
        return self._secure3d(order['card_number'], order['exp_year'], order['exp_month'])

    def _form_to_order(self, form):
        cart = api.get_cart(self.request)

        # 変換
        card_number = form['card_number'].data
        exp_year = form['exp_year'].data
        exp_month = form['exp_month'].data
        secure_code = form['secure_code'].data
        card_holder_name = form['card_holder_name'].data.upper()

        order = self.request.session['order']
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
        cart = api.get_cart(self.request)
        order = self.request.session['order']
        # 変換
        order_no = order['order_no']

        item_name = api.get_item_name(self.request, cart.performance)


        checkout_auth_result = multicheckout_api.checkout_auth_secure_code(
            self.request, get_order_no(self.request, cart),
            item_name, cart.total_amount, 0, order['client_name'], order['mail_address'],
            order['card_number'], order['exp_year'] + order['exp_month'], order['card_holder_name'],
            order['secure_code'],
        )

        if checkout_auth_result.CmnErrorCd != '000000':
            logger.info(u'card_info_secure3d_callback: 決済エラー order_no = %s, error_code = %s' % (order['order_no'], checkout_auth_result.CmnErrorCd))
            self.request.session.flash(get_error_message(self.request, checkout_auth_result.CmnErrorCd))
            raise HTTPFound(location=self.request.route_url('payment.secure3d'))

        self.request.session['order'] = order

        DBSession.add(checkout_auth_result)

        return HTTPFound(location=self.request.route_url('payment.confirm'))


    def _secure3d(self, card_number, exp_year, exp_month):
        """ セキュア3D """
        cart = api.get_cart(self.request)
        order = self.request.session['order']
        enrol = multicheckout_api.secure3d_enrol(self.request, get_order_no(self.request, cart), card_number, exp_year, exp_month, cart.total_amount)
        if enrol.is_enable_auth_api():
            form=m_h.secure3d_acs_form(self.request, self.request.route_url('cart.secure3d_result'), enrol)
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
        form = schemas.CardForm(csrf_context=self.request.session)
        return dict(form=form)

    @view_config(route_name='cart.secure3d_result', request_method="POST", renderer=selectable_renderer("carts/%(membership)s/confirm.html"))
    def card_info_secure3d_callback(self):
        """ カード情報入力(3Dセキュア)コールバック
        3Dセキュア認証結果取得
        """
        if not api.has_cart(self.request):
            raise NoCartError()
        cart = api.get_cart(self.request)

        order = self.request.session['order']
        # 変換
        pares = multicheckout_api.get_pares(self.request)
        md = multicheckout_api.get_md(self.request)
        order['pares'] = pares
        order['md'] = md
        order['order_no'] = get_order_no(self.request, cart)

        auth_result = multicheckout_api.secure3d_auth(self.request, get_order_no(self.request, cart), pares, md)
        item_name = api.get_item_name(self.request, cart.performance)

        # TODO: エラーメッセージ
        #if not auth_result.is_enable_auth_checkout():
        #    return HTTPFound(self.request.route_url('payment.secure3d'))

        # TODO: エラーメッセージ
        if not auth_result.is_enable_secure3d():
            return HTTPFound(self.request.route_url('payment.secure3d'))

        logger.debug('call checkout auth')
        checkout_auth_result = multicheckout_api.checkout_auth_secure3d(
            self.request, get_order_no(self.request, cart),
            item_name, cart.total_amount, 0, order['client_name'], order['mail_address'],
            order['card_number'], order['exp_year'] + order['exp_month'], order['card_holder_name'],
            mvn=auth_result.Mvn, xid=auth_result.Xid, ts=auth_result.Ts,
            eci=auth_result.Eci, cavv=auth_result.Cavv, cavv_algorithm=auth_result.Cavva,
        )
        logger.debug('called checkout auth')
        # TODO: エラーチェック CmnErrorCd CardErrorCd
        if checkout_auth_result.CmnErrorCd != '000000':
            logger.info(u'card_info_secure3d_callback: 決済エラー order_no = %s, error_code = %s' % (order['order_no'], checkout_auth_result.CmnErrorCd))
            self.request.session.flash(get_error_message(self.request, checkout_auth_result.CmnErrorCd))
            raise HTTPFound(location=self.request.route_url('payment.secure3d'))

        tran = dict(
            mvn=auth_result.Mvn, xid=auth_result.Xid, ts=auth_result.Ts,
            eci=auth_result.Eci, cavv=auth_result.Cavv, cavv_algorithm=auth_result.Cavva,
        )
        order['tran'] = tran
        self.request.session['order'] = order

        DBSession.add(checkout_auth_result)

        return HTTPFound(location=self.request.route_url('payment.confirm'))
