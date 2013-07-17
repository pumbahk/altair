# -*- coding:utf-8 -*-

from datetime import datetime, date
from pyramid.view import view_config
from altair.app.ticketing.multicheckout import api, logger
from altair.app.ticketing.multicheckout import helpers as h

class IndexView(object):
    def __init__(self, request):
        self.request = request

    def gen_order_no(self):
        now = datetime.now()
        return now.strftime("%Y%m%d%H%M%S") + "00"

    @view_config(route_name="top", renderer="index.mak", request_method="GET")
    def index(self):
        order_no = self.gen_order_no()
        return dict(order_no=order_no)

    @view_config(route_name="top", request_method="POST", renderer="redirect_post.mak")
    def post(self):
        request_api = self.request.params['API']
        result = None

        if request_api == 'secure3d_enrol':
            self.request.session['order'] = dict(
                order_no=self.request.params['order_no'],
                client_name=self.request.params['client_name'],
                total_amount=int(self.request.params['total_amount']),
                card_holder_name=self.request.params['card_holder_name'],
                card_number=self.request.params['card_number'],
                exp_year=self.request.params['exp_year'],
                exp_month=self.request.params['exp_month'],
                mail_address=self.request.params['mail_address'],
            )

            result = api.secure3d_enrol(
                request=self.request,
                order_no=self.request.params['order_no'],
                card_number=self.request.params['card_number'],
                exp_year=self.request.params['exp_year'],
                exp_month=self.request.params['exp_month'],
                total_amount=int(self.request.params['total_amount']),
            )

            if result.is_enable_auth_api():
                logger.debug("acs_url = %s" % result.AcsUrl)
                return dict(form=h.secure3d_acs_form(self.request, self.request.route_url('secure3d_result'), result))

        elif request_api == 'checkout_auth_secure_code':
            result = api.checkout_auth_secure_code(
                request=self.request,
                order_no=self.request.params['order_no'],
                item_name=u'テストアイテム',
                amount=self.request.params['total_amount'],
                tax=0,
                client_name=self.request.params['client_name'],
                mail_address=self.request.params['mail_address'],
                card_no=self.request.params['card_number'],
                card_limit=self.request.params['exp_year'] + self.request.params['exp_month'],
                card_holder_name=self.request.params['card_holder_name'],
                secure_code=self.request.params['secure_code'],
                free_data=None,
                item_cd=None,
                date=date
            )

        elif request_api == 'checkout_auth_cancel':
            result = api.checkout_auth_cancel(
                self.request,
                self.request.params['order_no']
            )

        elif request_api == 'checkout_sales_secure3d':
            result = api.checkout_sales_secure3d(
                request=self.request,
                order_no=self.request.params['order_no'],
                item_name='',
                amount=0,
                tax=0,
                client_name='',
                mail_address='',
                card_no='',
                card_limit='',
                card_holder_name='',
                mvn='',
                xid='',
                ts='',
                eci='',
                cavv='',
                cavv_algorithm='',
                free_data='',
                item_cod='',
                date=date
            )

        elif request_api == 'checkout_sales_secure_code':
            result = api.checkout_sales_secure_code(
                request=self.request,
                order_no=self.request.params['order_no'],
                item_name='',
                amount=0,
                tax=0,
                client_name='',
                mail_address='',
                card_no='',
                card_limit='',
                card_holder_name='',
                secure_code='',
                free_data='',
                item_cd='',
                date=date
            )

        elif request_api == 'checkout_sales_cancel':
            result = api.checkout_sales_cancel(
                self.request,
                self.request.params['order_no']
            )

        elif request_api == 'checkout_sales_part_cancel':
            result = api.checkout_sales_part_cancel(
                self.request,
                self.request.params['order_no'],
                int(self.request.params['total_amount']),
                0
            )

        elif request_api == 'checkout_inquiry':
            result = api.checkout_inquiry(
                self.request,
                self.request.params['order_no']
            )

        self.request.response.text = unicode(vars(result))
        return self.request.response


class Secure3DResultView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name="secure3d_result", renderer="string", request_method="POST")
    def results(self):
        order = self.request.session['order']
        pares = api.get_pares(self.request)
        md = api.get_md(self.request)

        auth_result = api.secure3d_auth(self.request, order['order_no'], pares, md)
        checkout_auth_result = api.checkout_auth_secure3d(
            self.request,
            order_no=order['order_no'],
            item_name=u'テストアイテム',
            amount=order['total_amount'],
            tax=0,
            client_name=order['client_name'],
            mail_address=order['mail_address'],
            card_no=order['card_number'],
            card_limit=order['exp_year'] + order['exp_month'],
            card_holder_name=order['card_holder_name'],
            mvn=auth_result.Mvn,
            xid=auth_result.Xid,
            ts=auth_result.Ts,
            eci=auth_result.Eci,
            cavv=auth_result.Cavv,
            cavv_algorithm=auth_result.Cavva,
        )
        return vars(checkout_auth_result)
