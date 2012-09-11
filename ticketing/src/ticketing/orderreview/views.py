# -*- coding:utf-8 -*-
import logging
from pyramid.view import view_config, render_view_to_response
from ticketing.core.models import Order, OrderedProduct, OrderedProductItem, ProductItem, Performance, Seat, TicketPrintHistory
from ticketing.qr import qr
from pyramid.response import Response
import StringIO
import qrcode

from . import schemas

builder = qr()
builder.key = u"THISISIMPORTANTSECRET"

logger = logging.getLogger(__name__)

class InvalidForm(Exception):
    def __init__(self, form):
        self.form = form

class OrderReviewView(object):
    def __init__(self, request):
        self.request = request
        self.context = request.context

    def __call__(self):
        return dict()

    def get(self):
        form = schemas.OrderReviewSchema(self.request.params)
        return {"form": form}

    def post(self):
        form = schemas.OrderReviewSchema(self.request.params)
        if not form.validate():
            raise InvalidForm(form)

        order, sej_order = self.context.get_order()
        if not form.object_validate(order):
            raise InvalidForm(form)
        return dict(order=order, sej_order=sej_order, shipping_address=order.shipping_address)

def order_review_form_view(context, request):
    request.errors = context.form.errors
    return dict(form=context.form)

def exception_view(context, request):
    logger.error("The error was: %s" % context, exc_info=request.exc_info)
    return dict()

def notfound_view(context, request):
    logger.error("The error was: %s" % context, exc_info=request.exc_info)
    return dict()

@view_config(name="contact")
def contact_view(context, request):
    return dict()

def build_qr(ticket_id):
    from sqlalchemy.orm.exc import NoResultFound
    ticket = None
    try:
        ticket = TicketPrintHistory\
        .filter_by(id = ticket_id)\
        .join(TicketPrintHistory.ordered_product_item)\
        .join(OrderedProductItem.ordered_product)\
        .join(OrderedProduct.order)\
        .join(Order.user)\
        .join(OrderedProductItem.product_item)\
        .join(ProductItem.performance)\
        .join(Performance.event)\
        .one()
    except NoResultFound, e:
        return None
    
    ticket.seat = ticket.seat
    ticket.performance = ticket.ordered_product_item.product_item.performance
    ticket.event = ticket.performance.event
    ticket.product = ticket.ordered_product_item.ordered_product.product
    ticket.order = ticket.ordered_product_item.ordered_product.order
    
    ticket.qr = builder.sign(builder.make(dict(
                    serial=("%d" % ticket.id),
                    performance=ticket.performance.code,
                    order=ticket.order.order_no,
                    date=ticket.performance.start_on.strftime("%Y%m%d"),
                    type=ticket.product.id,
                    seat=ticket.seat.l0_id,
                    seat_name=ticket.seat.name,
                    )))
    ticket.sign = ticket.qr[0:8]
    
    return ticket

def order_review_qr_html(context, request):
    ticket_id = int(request.matchdict.get('ticket_id', 0))
    sign = request.matchdict.get('sign', 0)
    
    ticket = build_qr(ticket_id)
    
    if ticket == None or ticket.sign != sign:
        raise HTTPNotFound()
    
    return dict(
        sign = sign,
        order = ticket.order,
        ticket = ticket,
        performance = ticket.performance,
        event = ticket.event,
        product = ticket.product,
    )
    
@view_config(route_name='order_review.qrdraw', xhr=False, permission="view")
def order_review_qr_image(context, request):
    ticket_id = int(request.matchdict.get('ticket_id', 0))
    sign = request.matchdict.get('sign', 0)
    
    ticket = build_qr(ticket_id)
    
    if ticket == None or ticket.sign != sign:
        raise HTTPNotFound()
    
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        )
    qr.add_data(ticket.qr)
    qr.make(fit=True)
    img = qr.make_image()
    r = Response(status=200, content_type="image/png")
    buf = StringIO.StringIO()
    img.save(buf, 'PNG')
    r.body = buf.getvalue()
    return r
