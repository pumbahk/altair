# -*- coding:utf-8 -*-
import logging
import sqlahelper
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound
from ticketing.cart.selectable_renderer import selectable_renderer
from ticketing.qr.image import qrdata_as_image_response
from . import schemas
from . import api
from ticketing.mobile import mobile_view_config
from ticketing.core.utils import IssuedAtBubblingSetter
from datetime import datetime

from ticketing.qr.utils import build_qr_by_history_id
from ticketing.qr.utils import build_qr_by_token_id

logger = logging.getLogger(__name__)

DBSession = sqlahelper.get_session()

class InvalidForm(Exception):
    def __init__(self, form):
        self.form = form

class OrderReviewView(object):
    def __init__(self, request):
        self.request = request
        self.context = request.context

    def __call__(self):
        return dict()

    @mobile_view_config(route_name='order_review.form',
                        request_method="GET", renderer=selectable_renderer("ticketing.orderreview:templates/%(membership)s/order_review_mobile/form.html"))
    @view_config(route_name='order_review.form', request_method="GET", 
                 renderer=selectable_renderer("ticketing.orderreview:templates/%(membership)s/order_review/form.html"))
    def get(self):
        form = schemas.OrderReviewSchema(self.request.params)
        return {"form": form}

    @mobile_view_config(route_name='order_review.show', request_method="POST", 
                        renderer=selectable_renderer("ticketing.orderreview:templates/%(membership)s/order_review_mobile/show.html"))
    @view_config(route_name='order_review.show', request_method="POST", 
                 renderer=selectable_renderer("ticketing.orderreview:templates/%(membership)s/order_review/show.html"))
    def post(self):
        form = schemas.OrderReviewSchema(self.request.params)
        if not form.validate():
            raise InvalidForm(form)

        order, sej_order = self.context.get_order()
        if not form.object_validate(self.request, order):
            raise InvalidForm(form)
        return dict(order=order, sej_order=sej_order, shipping_address=order.shipping_address)

@mobile_view_config(context=InvalidForm, 
                    renderer=selectable_renderer("ticketing.orderreview:templates/%(membership)s/order_review_mobile/form.html"))
@view_config(context=InvalidForm, 
             renderer=selectable_renderer("ticketing.orderreview:templates/%(membership)s/order_review/form.html"))
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
@view_config(route_name="contact", renderer=selectable_renderer("ticketing.orderreview:templates/%(membership)s/static/contact.html"))
@mobile_view_config(route_name="contact", renderer=selectable_renderer("ticketing.orderreview:templates/%(membership)s/static_mobile/contact.html"))
def contact_view(context, request):
    return dict()

@mobile_view_config(route_name='order_review.qr_confirm', renderer=selectable_renderer("ticketing.orderreview:templates/%(membership)s/order_review/qr_confirm.html"))
@view_config(route_name='order_review.qr_confirm', renderer=selectable_renderer("ticketing.orderreview:templates/%(membership)s/order_review/qr_confirm.html"))
def order_review_qr_confirm(context, request):
    ticket_id = int(request.matchdict.get('ticket_id', 0))
    sign = request.matchdict.get('sign', 0)
    
    ticket = build_qr_by_history_id(request, ticket_id)
    
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
@view_config(route_name='order_review.qr', renderer=selectable_renderer("ticketing.orderreview:templates/%(membership)s/order_review/qr.html"))
def order_review_qr_html(context, request):
    ticket_id = int(request.matchdict.get('ticket_id', 0))
    sign = request.matchdict.get('sign', 0)
    
    ticket = build_qr_by_history_id(request, ticket_id)
    
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
    
    ticket = build_qr_by_history_id(request, ticket_id)
    
    if ticket == None or ticket.sign != sign:
        raise HTTPNotFound()
    return qrdata_as_image_response(ticket)

@mobile_view_config(route_name='order_review.qr_print', request_method='POST', renderer=selectable_renderer("ticketing.orderreview:templates/%(membership)s/order_review/qr.html"))
@view_config(route_name='order_review.qr_print', request_method='POST', renderer=selectable_renderer("ticketing.orderreview:templates/%(membership)s/order_review/qr.html"))
def order_review_qr_print(context, request):
    ticket = build_qr_by_token_id(request, request.params['order_no'], request.params['token'])
    
    issued_setter = IssuedAtBubblingSetter(datetime.now())
    issued_setter.issued_token(ticket.item_token)
    issued_setter.start_bubbling()

    return dict(
        sign = ticket.qr[0:8],
        order = ticket.order,
        ticket = ticket,
        performance = ticket.performance,
        event = ticket.event,
        product = ticket.product,
        )

@mobile_view_config(route_name='order_review.qr_send', request_method="POST", 
             renderer=selectable_renderer("ticketing.orderreview:templates/%(membership)s/order_review/send.html"))
@view_config(route_name='order_review.qr_send', request_method="POST", 
             renderer=selectable_renderer("ticketing.orderreview:templates/%(membership)s/order_review/send.html"))
def order_review_send_mail(context, request):
    # TODO: validate mail address
    
    mail = request.params['mail']
    # send mail using template
    form = schemas.SendMailSchema(request.POST)

    if not form.validate():
        return dict(mail=mail, 
                    message=u"Emailの形式が正しくありません")

    try:
        sender = context.membership.organization.contact_email
        api.send_qr_mail(request, context, mail, sender)
        
    except Exception, e:
        logger.error(e.message, exc_info=1)
        ## この例外は違う...
        raise HTTPNotFound()

    message = u"%s宛にメールをお送りしました。" % mail
    return dict(
        mail = mail,
        message = message
        )

@mobile_view_config(name="render.mail", 
             renderer=selectable_renderer("ticketing.orderreview:templates/%(membership)s/order_review/qr.txt"))
@view_config(name="render.mail", 
             renderer=selectable_renderer("ticketing.orderreview:templates/%(membership)s/order_review/qr.txt"))
def render_qrmail_viewlet(context, request):
    ticket = build_qr_by_token_id(request, request.params['order_no'], request.params['token'])
    sign = ticket.qr[0:8]
    if ticket.order.shipping_address:
        name = ticket.order.shipping_address.last_name + ticket.order.shipping_address.first_name
    else:
        name = u''
    
    return dict(
        name=name,
        event=ticket.event, 
        performance=ticket.performance, 
        product=ticket.product, 
        seat=ticket.seat, 
        mail = request.params['mail'],
        url = request.route_url('order_review.qr_confirm', ticket_id=ticket.id, sign=sign),
    )
