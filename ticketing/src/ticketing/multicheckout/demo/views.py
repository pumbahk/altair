# -*- coding:utf-8 -*-
from datetime import datetime
from pyramid.view import view_config
from ticketing.multicheckout import api
from ticketing.multicheckout import helpers as h
from .. import logger

class IndexView(object):
    def __init__(self, request):
        self.request = request


    def gen_order_no(self):
        now = datetime.now()
        return now.strftime("%Y%m%d%H%M%S")

    @view_config(route_name="top", renderer="index.mak", request_method="GET")
    def index(self):
        return dict()

    @view_config(route_name="top", request_method="POST", renderer="redirect_post.mak")
    def require_secure3d(self):

        order_no = self.gen_order_no()
        self.request.session['order'] = dict(
            order_no=order_no,
            client_name=self.request.params['client_name'],
            amount=int(self.request.params['total_amount']),
            card_holder_name=self.request.params['card_holder_name'],
            card_number=self.request.params['card_number'],
            exp_year=self.request.params['exp_year'],
            exp_month=self.request.params['exp_month'],
            mail_address=self.request.params['mail_address'],
        )

        secure3d = api.secure3d_enrol(
            request=self.request,
            order_no=order_no,
            card_number=self.request.params['card_number'],
            exp_year=self.request.params['exp_year'],
            exp_month=self.request.params['exp_month'],
            total_amount=int(self.request.params['total_amount']),
        )

        if secure3d.is_enable_auth_api():
            logger.debug("acs_url = %s" % secure3d.AcsUrl)
            return dict(form=h.secure3d_acs_form(self.request, self.request.route_url('secure3d_result'), secure3d))
        else:
            self.request.response.text = "ErrorCd = %s, RetCd = %s" % (secure3d.ErrorCd, ErrorCd.RetCd)
            return self.request.response

class Secure3DResultView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name="secure3d_result", renderer="string", request_method="POST")
    def secure3d_results(self):
        order = self.request.session['order']
        order_no = order['order_no']
        amount = order['amount']
        tax = 0
        client_name = order['client_name']
        card_holder_name = order['card_holder_name']
        card_no = order['card_number']
        mail_address = order['mail_address']
        card_limit = order['exp_year'] + order['exp_month']
        item_name = u'テストアイテム'

        pares = api.get_pares(self.request)
        md = api.get_md(self.request)

        auth_result = api.secure3d_auth(self.request, order_no, pares, md)
        checkout_auth_result = api.checkout_auth_secure3d(
            self.request, order_no,
            item_name, amount, tax, client_name, mail_address,
            card_no, card_limit, card_holder_name,
            mvn=auth_result.Mvn, xid=auth_result.Xid, ts=auth_result.Ts,
            eci=auth_result.Eci, cavv=auth_result.Cavv, cavv_algorithm=auth_result.Cavva,
        )
        return dict(
            OrderNo=checkout_auth_result.OrderNo,
            Status=checkout_auth_result.Status,
            PublicTranId=checkout_auth_result.PublicTranId,
            AheadComCd=checkout_auth_result.AheadComCd,
            ApprovalNo=checkout_auth_result.ApprovalNo,
            CardErrorCd=checkout_auth_result.CardErrorCd,
            ReqYmd=checkout_auth_result.ReqYmd,
            CmnErrorCd=checkout_auth_result.CmnErrorCd,
        )
