# -*- coding:utf-8 -*-
import logging
from pyramid.view import view_config

from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.response import Response
from ticketing.core.models import Order, OrderedProduct, OrderedProductItem, ProductItem, Performance, Seat, TicketPrintHistory
from ticketing.core import models as m
from ticketing.cart.rakuten_auth.api import authenticated_user, forget
from ticketing.cart import api
from .helpers import make_order_data
from ticketing.orderreview.views import build_qr_by_token_id, order_review_qr_image

import webhelpers.paginate as paginate
import ticketing.cart.plugins.qr
from ticketing.qr import qr
import StringIO
import qrcode

import sqlahelper

DBSession = sqlahelper.get_session()

logger = logging.getLogger(__name__)

builder = qr()
builder.key = u"THISISIMPORTANTSECRET"

class MyPageView(object):

    def __init__(self, request):
        self.request = request

    @view_config(route_name='mypage.index', renderer='mypage/index.html', xhr=False, permission="view")
    def index(self):

        openid = authenticated_user(self.request)
        user = api.get_or_create_user(self.request, openid['clamed_id'])

        q = self.request.POST.get('q')
        sort = self.request.GET.get('sort', 'Order.id')
        direction = self.request.GET.get('direction', 'asc')
        if direction not in ['asc', 'desc']:
            direction = 'asc'

        query = Order.filter(Order.user_id == user.id)
        if q:
            print ">>>>>>>>>>>>>>"
            print q
            print ">>>>>>>>>>>>>>"
            query = Order.filter(Order.order_no == q)
        query = query.order_by(sort + ' ' + direction)

        # search condition
        if self.request.method == 'POST':
            condition = self.request.POST.get('order_number')
            if condition:
                query = query.filter(Order.order_no==condition)

        orders = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=20,
            url=paginate.PageURL_WebOb(self.request)
        )

        print user.user_profile
        logger.debug(user.user_profile)
        return dict(
            q = q,
            user = user.user_profile,
            orders = orders
        )

    @view_config(route_name='mypage.logout', renderer='mypage/logout.html', xhr=False, permission="view")
    def logout(self):
        """
        """
        headers = forget(self.request)
        return HTTPFound(location = '/',
                         headers = headers)



    @view_config(route_name='mypage.order', renderer='mypage/order.html', xhr=False, permission="view")
    def order(self):

        openid = authenticated_user(self.request)
        user = api.get_or_create_user(self.request, openid['clamed_id'])
        order_id = int(self.request.matchdict.get('order_id', 0))

        from sqlalchemy.orm.exc import NoResultFound
        order = None
        try:
            order = Order.filter_by(id = order_id , user_id = user.id).one()
        except NoResultFound, e:
            raise HTTPNotFound()

        tickets = None
        if order.payment_delivery_pair.delivery_method.delivery_plugin_id == ticketing.cart.plugins.qr.DELIVERY_PLUGIN_ID:
            """QRコード発行の場合"""
            # 以下の処理はcart/plugins/qr.py内のと同じ...
            tickets = [ ]
            for op in order.ordered_products:
                for opi in op.ordered_product_items:
                    for s in opi.seats:
                        # 発行済みかどうかを取得
                        history = TicketPrintHistory.filter_by(ordered_product_item_id = opi.id, seat_id = s.id).first()
                        _order = order
                        class QRTicket:
                            order = _order
                            performance = order.performance
                            product = op.product
                            seat = s
                            printed_at = history.created_at if history else ''
                        ticket = QRTicket()
                        tickets.append(ticket)

        import locale
        locale.setlocale(locale.LC_ALL, 'ja_JP')
        return dict(
            order = make_order_data(order),
            tel = order.shipping_address.tel_1,
            tickets = tickets,
            user = user.user_profile
        )
    
    @view_config(route_name='mypage.qr_print', renderer='mypage/qr.html', xhr=False, permission="view")
    def show_qr_page(self):
        openid = authenticated_user(self.request)
        user = api.get_or_create_user(self.request, openid['clamed_id'])
        
        ticket = build_qr_by_token_id(self.request.params['order_no'], self.request.params['seat'])
        
        return dict(
            sign = ticket.qr[0:8],
            ticket = ticket,
            order = ticket.order,
            product = ticket.product,
            performance = ticket.performance,
            event = ticket.event,
        )

    @view_config(route_name='mypage.qr_send', renderer='mypage/send.html', xhr=False, permission="view")
    def send_qr_mail(self):
        mail = self.request.params['mail']
        
        ## TODO: send mail
        
        return dict(
            mail = mail
            )

    @view_config(route_name='qr.draw', xhr=False, permission="view")
    def get_qr_image(self):
        return order_review_qr_image(None, self.request)
