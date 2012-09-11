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
            tickets = [ ]
            pcode = order.performance.code
            pdate = order.performance.start_on.strftime("%Y%m%d")
            for ordered_product in order.items:
                for ordered_product_item in ordered_product.ordered_product_items:
                    for seat_item in ordered_product_item.seats:
                        class QRTicket:
                            serial = u""
                            performance_code = pcode
                            order = 0
                            performance_date = pdate
                            product = ordered_product.product
                            seat = seat_item
                            qr = u""
                        ticket = QRTicket()
                        history = m.TicketPrintHistory.filter_by(ordered_product_item_id=ordered_product_item.id, seat_id=seat_item.id).first()
                        if history == None:
                            # create TicketPrintHistory record
                            history = m.TicketPrintHistory(ordered_product_item_id=ordered_product_item.id, seat_id=seat_item.id)
                            m.DBSession.add(history)
                            m.DBSession.flush()
                        ticket.serial = history.id
                        ticket.qr = builder.sign(builder.make(dict(
                                    serial=("%d" % ticket.serial),
                                    performance=pcode,
                                    order=order.order_no,
                                    date=pdate,
                                    type=ticket.product.id,
                                    seat=seat_item.l0_id,
                                    seat_name=seat_item.name,
                                    )))
                        tickets.append(ticket)

        import locale
        locale.setlocale(locale.LC_ALL, 'ja_JP')
        return dict(
            order = make_order_data(order),
            tickets = tickets,
            user = user.user_profile
        )
    
    @view_config(route_name='mypage.qr', renderer='mypage/qr.html', xhr=False, permission="view")
    def show_qr_page(self):
        openid = authenticated_user(self.request)
        user = api.get_or_create_user(self.request, openid['clamed_id'])
        order_id = int(self.request.matchdict.get('order_id', 0))
        ticket_id = int(self.request.matchdict.get('ticket_id', 0))

        from sqlalchemy.orm.exc import NoResultFound
        ticket = None
        try:
            ticket = TicketPrintHistory\
            .filter_by(id = ticket_id)\
            .join(TicketPrintHistory.ordered_product_item)\
            .join(OrderedProductItem.ordered_product)\
            .join(OrderedProduct.order)\
            .join(Order.user)\
            .filter_by(id = user.id)\
            .join(OrderedProductItem.product_item)\
            .join(ProductItem.performance)\
            .join(Performance.event)\
            .one()
        except NoResultFound, e:
            raise HTTPNotFound()
        
        seat = ticket.seat
        performance = ticket.ordered_product_item.product_item.performance
        event = performance.event
        product = ticket.ordered_product_item.ordered_product.product
        order = ticket.ordered_product_item.ordered_product.order
        
        logger.debug(ticket)
        logger.debug(order)
        logger.debug(product)
        
        ticket.qr = builder.sign(builder.make(dict(
                    serial=("%d" % ticket.id),
                    performance=performance.code,
                    order=order.order_no,
                    date=performance.start_on.strftime("%Y%m%d"),
                    type=product.id,
                    seat=seat.l0_id,
                    seat_name=seat.name,
                    )))
        
        return dict(
            order = order,
            product = product,
            ticket = ticket,
            performance = performance,
            event = event,
        )

@view_config(route_name='qr.draw', xhr=False, permission="view")
def get_qr_image(self):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
    )
    data = self.GET.get("d")
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image()
    r = Response(status=200, content_type="image/png")
    buf = StringIO.StringIO()
    img.save(buf, 'PNG')
    r.body = buf.getvalue()
    return r
