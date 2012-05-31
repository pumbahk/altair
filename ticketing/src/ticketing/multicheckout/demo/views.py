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
        self.request.session['order_no'] = order_no
        secure3d = api.secure3d_enrol(
            request=self.request,
            order_no=order_no,
            card_number=self.request.params['card_number'],
            exp_year=self.request.params['exp_year'],
            exp_month=self.request.params['exp_month'],
            total_amount=int(self.request.params['total_amount']),
        )

        logger.debug("acs_url = %s" % secure3d.AcsUrl)
        return dict(form=h.secure3d_acs_form(self.request, self.request.route_url('secure3d_result'), secure3d))

class Secure3DResultView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name="secure3d_result", renderer="string", request_method="POST")
    def secure3d_results(self):
        order_no = self.request.session['order_no']
        pares = self.request.params['PaRes']
        md = self.request.params['MD']

        auth_result = api.secure3d_auth(self.request, order_no, pares, md)
        return dict(
            ErrorCd=auth_result.ErrorCd,
            RetCd=auth_result.RetCd,
            Xid=auth_result.Xid,
            Ts=auth_result.Ts,
            Cavva=auth_result.Cavva,
            Cavv=auth_result.Cavv,
            Eci=auth_result.Eci,
            Mvn=auth_result.Mvn,
        )
