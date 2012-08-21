# -*- coding:utf-8 -*-
import logging
from pyramid.view import view_config

from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from ticketing.core.models import Order, OrderedProduct, OrderedProductItem, Seat
from ticketing.core import models as m
from ticketing.cart.rakuten_auth.api import authenticated_user, forget
from ticketing.cart import api
from .helpers import make_order_data

import webhelpers.paginate as paginate
import ticketing.cart.plugins.qr
from ticketing.qr import qr

import sqlahelper

DBSession = sqlahelper.get_session()

logger = logging.getLogger(__name__)

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
        if order.payment_delivery_pair.delivery_method.delivery_plugin_id == ticketing.cart.plugins.qr.PLUGIN_ID:
            """QRコード発行の場合"""
            builder = qr()
            builder.key = u"THISISIMPORTANTSECRET"
            tickets = [ ]
            pcode = order.performance.code
            pdate = order.performance.start_on.strftime("%Y%m%d")
            for ordered_product in order.items:
                for ordered_product_item in ordered_product.ordered_product_items:
                    for seat_item in ordered_product_item.seats:
                        class QRTicket:
                            serial = u"1"
                            performance_code = pcode
                            performance_date = pdate
                            product = ordered_product.product
                            seat = seat_item
                            qr = builder.sign(builder.make(dict(
                                serial=u"1",
                                performance=pcode,
                                order=order.order_no,
                                date=pdate,
                                type=100,
                                seat=seat_item.name,
                            )))
                        ticket = QRTicket()
                        history = m.TicketPrintHistory.filter_by(ordered_product_item_id=ordered_product_item.id, seat_id=seat_item.id).first()
                        if history == None:
                            history = m.TicketPrintHistory(ordered_product_item_id=ordered_product_item.id, seat_id=seat_item.id)
                            m.DBSession.add(history)
                            m.DBSession.flush()
                        ticket.serial = history.id
                        tickets.append(ticket)

        import locale
        locale.setlocale(locale.LC_ALL, 'ja_JP')
        return dict(
            order = make_order_data(order),
            tickets = tickets,
            user = user.user_profile
        )
