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

    @view_config(route_name="top", request_method="POST", renderer="string")
    def require_secure3d(self):

        secure3d = api.secure3d_enrol(
            request=self.request,
            order_no=self.gen_order_no(),
            card_number=self.request.params['card_number'],
            exp_year=self.request.params['exp_year'],
            exp_month=self.request.params['exp_month'],
            total_amount=int(self.request.params['total_amount']),
        )

        logger.debug("acs_url = %s" % secure3d.AcsUrl)
        return h.secure3d_acs_form(self.request, self.request.route_url('top'), secure3d)