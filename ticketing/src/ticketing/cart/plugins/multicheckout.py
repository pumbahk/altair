# -*- coding:utf-8 -*-

from datetime import datetime
from zope.interface import implementer
from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from ticketing.multicheckout import helpers as m_h
from ticketing.multicheckout import api as multicheckout_api
from ticketing.core import models as c_models
from ticketing.orders import models as o_models
from ..interfaces import IPaymentPlugin, ICartPayment, IOrderPayment
from .models import DBSession
from .. import schema
from .. import logger
from .. import helpers as h
from .. import api

PLUGIN_ID = 1

def includeme(config):
    # 決済系(マルチ決済)
    config.add_payment_plugin(MultiCheckoutPlugin(), PLUGIN_ID)
    config.add_route("payment.secure3d", 'payment/3d')
    config.add_route("cart.secure3d_result", 'payment/3d/result')
    config.scan(__name__)


@implementer(IPaymentPlugin)
class MultiCheckoutPlugin(object):
    def prepare(self, request, cart):
        """ 3Dセキュア認証 """
        return HTTPFound(location=request.route_url("payment.secure3d"))

    def finish(self, request, cart):
        """ 売り上げ確定 """
        order = request.session['order']
        order_id = order['order_id']
        pares = order['pares']
        md = order['md']
        tran = order['tran']
        item_name = api.get_item_name(request, cart.performance)

        checkout_sales_result = multicheckout_api.checkout_sales_secure3d(
            request, order_id,
            item_name, cart.total_amount, 0, order['client_name'], order['mail_address'],
            order['card_number'], order['exp_year'] + order['exp_month'], order['card_holder_name'],
            mvn=tran['mvn'], xid=tran['xid'], ts=tran['ts'],
            eci=tran['eci'], cavv=tran['cavv'], cavv_algorithm=tran['cavv_algorithm'],
        )

        # TODO: エラーチェック

        DBSession.add(checkout_sales_result)

        order = o_models.Order.create_from_cart(cart)
        order.multicheckout_approval_no = checkout_sales_result.ApprovalNo
        order.paid_at = datetime.now()
        cart.finish()

        return order

def card_number_mask(number):
    """ 下4桁以外をマスク"""
    return "*" * (len(number) - 4) + number[-4:]

@view_config(context=ICartPayment, name="payment-1", renderer="ticketing.cart.plugins:templates/card_confirm.html")
def confirm_viewlet(context, request):
    """ 確認画面表示 
    :param context: ICartPayment
    """

    order_session = request.session["order"]
    logger.debug("order_session %s" % order_session)
    return dict(order=order_session, card_number_mask=card_number_mask)

@view_config(context=IOrderPayment, name="payment-1")
def completion_viewlet(context, request):
    """ 完了画面表示 
    :param context: IOrderPayment
    """
    return Response(text=u"クレジットカード")

class MultiCheckoutView(object):
    """ マルチ決済API
    """

    def __init__(self, request):
        self.request = request

    @view_config(route_name='payment.secure3d', request_method="GET", renderer='carts/card_form.html')
    def card_info_secure3d_form(self):
        """ カード情報入力"""
        return dict()

    @view_config(route_name='payment.secure3d', request_method="POST", renderer='carts/card_form.html')
    def card_info_secure3d(self):
        """ カード情報入力(3Dセキュア)
        """
        form = schema.CardForm(formdata=self.request.params)
        if not form.validate():
            logger.debug("form error %s" % (form.errors,))
            # TODO: 入力エラー表示
            return dict()
        assert api.has_cart(self.request)
        cart = api.get_cart(self.request)

        # 変換
        order_id = cart.id
        card_number = form['card_number'].data
        exp_year = form['exp_year'].data
        exp_month = form['exp_month'].data
        order = self.request.session['order']
        order.update(
            order_no=order_id,
            card_holder_name=self.request.params['card_holder_name'],
            card_number=card_number,
            exp_year=exp_year,
            exp_month=exp_month,
        )
        self.request.session['order'] = order
        enrol = multicheckout_api.secure3d_enrol(self.request, order_id, card_number, exp_year, exp_month, cart.total_amount)
        if enrol.is_enable_auth_api():
            form=m_h.secure3d_acs_form(self.request, self.request.route_url('cart.secure3d_result'), enrol)
            self.request.response.text = form
            return self.request.response
        elif enrol.is_enable_secure3d():
            # セキュア3D認証エラーだが決済APIを利用可能
            logger.debug("3d secure is failed ErrorCd = %s RetCd = %s" %(enrol.ErrorCd, enrol.RetCd))

        else:
            # セキュア3D認証エラー
            logger.debug("3d secure is failed ErrorCd = %s RetCd = %s" %(enrol.ErrorCd, enrol.RetCd))
        return dict()

    @view_config(route_name='cart.secure3d_result', request_method="POST", renderer="carts/confirm.html")
    def card_info_secure3d_callback(self):
        """ カード情報入力(3Dセキュア)コールバック
        3Dセキュア認証結果取得
        """
        assert api.has_cart(self.request)
        cart = api.get_cart(self.request)

        order = self.request.session['order']
        # 変換
        order_id = str(cart.id) + "00"
        pares = multicheckout_api.get_pares(self.request)
        md = multicheckout_api.get_md(self.request)
        order['pares'] = pares
        order['md'] = md
        order['order_id'] = order_id

        auth_result = multicheckout_api.secure3d_auth(self.request, order_id, pares, md)
        item_name = api.get_item_name(self.request, cart.performance)

        # TODO: エラーメッセージ
        if not auth_result.is_enable_auth_checkout():
            return HTTPFound(self.request.route_url('payment.secure3d'))

        checkout_auth_result = multicheckout_api.checkout_auth_secure3d(
            self.request, order_id,
            item_name, cart.total_amount, 0, order['client_name'], order['mail_address'],
            order['card_number'], order['exp_year'] + order['exp_month'], order['card_holder_name'],
            mvn=auth_result.Mvn, xid=auth_result.Xid, ts=auth_result.Ts,
            eci=auth_result.Eci, cavv=auth_result.Cavv, cavv_algorithm=auth_result.Cavva,
        )
        # TODO: エラーチェック CmnErrorCd CardErrorCd

        tran = dict(
            mvn=auth_result.Mvn, xid=auth_result.Xid, ts=auth_result.Ts,
            eci=auth_result.Eci, cavv=auth_result.Cavv, cavv_algorithm=auth_result.Cavva,
        )
        order['tran'] = tran
        self.request.session['order'] = order

        DBSession.add(checkout_auth_result)

        return HTTPFound(location=self.request.route_url('payment.confirm'))
