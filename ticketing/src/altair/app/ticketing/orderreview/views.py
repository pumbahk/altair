# -*- coding:utf-8 -*-
import logging
import sqlahelper
import json
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from altair.app.ticketing.cart.selectable_renderer import selectable_renderer
from altair.app.ticketing.qr.image import qrdata_as_image_response
from . import schemas
from . import api
from altair.mobile import mobile_view_config
from altair.app.ticketing.core.utils import IssuedAtBubblingSetter
from datetime import datetime

import helpers as h
from ..users.api import get_user
from altair.app.ticketing.cart import api as cart_api
from altair.app.ticketing.qr.utils import build_qr_by_history_id
from altair.app.ticketing.qr.utils import build_qr_by_token_id
from altair.auth import who_api as get_who_api
from .api import safe_get_contact_url, is_mypage_organization
logger = logging.getLogger(__name__)

DBSession = sqlahelper.get_session()

class InvalidForm(Exception):
    def __init__(self, form):
        self.form = form

class MypageView(object):

    def __init__(self, request):
        self.request = request
        self.context = request.context

    @view_config(route_name='mypage.show', request_method="GET", custom_predicates=(is_mypage_organization, ),
                 renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/mypage/show.html"))
    def show(self):

        authenticated_user = self.context.authenticated_user()
        user = get_user(authenticated_user)

        if not user:
            raise HTTPNotFound()

        shipping_address = self.context.get_shipping_address(user)
        orders = self.context.get_orders(user)
        entries = self.context.get_lots_entries(user)

        return dict(
            shipping_address=shipping_address,
            orders=orders,
            lot_entries=entries,
            h=h,
        )

class MypageLoginView(object):
    renderer_tmpl = "altair.app.ticketing.orderreview:templates/{membership}/order_review/form.html"
    renderer_tmpl_mobile = "altair.app.ticketing.orderreview:templates/{membership}/order_review_mobile/form.html"
    #renderer_tmpl_smartphone = "altair.app.ticketing.fc_auth:templates/{membership}/login_smartphone.html"

    def __init__(self, request):
        self.request = request
        self.context = request.context

    def select_renderer(self, membership):
        self.request.override_renderer = self.renderer_tmpl.format(membership=membership)
        if cart_api.is_mobile(self.request):
            self.request.override_renderer = self.renderer_tmpl_mobile.format(membership=membership)
        """
        elif cart_api.is_smartphone(self.request):
            self.request.override_renderer = self.renderer_tmpl_smartphone.format(membership=membership)
        else:
            self.request.override_renderer = self.renderer_tmpl.format(membership=membership)
        """

    @view_config(request_method="GET", route_name='order_review.form'
        , custom_predicates=(is_mypage_organization, ), renderer='json', http_cache=60)
    def login_form(self):
        membership = self.context.get_membership().name
        self.select_renderer(membership)

        # このformは、モバイルのためだけに必要
        form = schemas.OrderReviewSchema(self.request.params)
        return dict(username='', form=form)

    @view_config(request_method="POST", route_name='order_review.form', renderer='string'
        , custom_predicates=(is_mypage_organization, ))
    def login(self):
        who_api = get_who_api(self.request, name="fc_auth")
        membership = self.context.get_membership().name
        username = self.request.params['username']
        password = self.request.params['password']
        logger.debug("authenticate for membership %s" % membership)

        identity = {
            'membership': membership,
            'username': username,
            'password': password,
        }
        authenticated, headers = who_api.login(identity)

        if authenticated is None:
            self.select_renderer(membership)
            return {'username': username,
                    'message': u'IDかパスワードが一致しません'}

        res = HTTPFound(location=self.request.route_path("mypage.show"), headers=headers)

        return res

class OrderReviewView(object):
    def __init__(self, request):
        self.request = request
        self.context = request.context

    def __call__(self):
        return dict()

    @mobile_view_config(route_name='order_review.form',
                        request_method="GET", renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/order_review_mobile/form.html"))
    @view_config(route_name='order_review.form', request_method="GET", 
                 renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/order_review/form.html"))
    @view_config(route_name='guest.order_review.form', request_method="GET",
                 renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/order_review_guest/form.html"))
    def get(self):
        form = schemas.OrderReviewSchema(self.request.params)
        return {"form": form}

    @mobile_view_config(route_name='order_review.show', request_method="POST", 
                        renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/order_review_mobile/show.html"))
    @view_config(route_name='order_review.show', request_method="POST",
                 renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/order_review/show.html"))
    @view_config(route_name='guest.order_review.show',
                 renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/order_review_guest/show.html"))
    def post(self):
        form = schemas.OrderReviewSchema(self.request.params)
        if not form.validate():
            raise InvalidForm(form)

        order, sej_order = self.context.get_order()
        if not form.object_validate(self.request, order):
            raise InvalidForm(form)
        return dict(order=order, sej_order=sej_order, shipping_address=order.shipping_address)

@mobile_view_config(context=InvalidForm,
                    renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/order_review_mobile/form.html"))
@view_config(context=InvalidForm, 
             renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/order_review/form.html"))
def order_review_form_view(context, request):
    request.errors = context.form.errors
    return dict(form=context.form)

def exception_view(context, request):
    logger.error("The error was: %s" % context, exc_info=request.exc_info)
    return dict()

def notfound_view(context, request):
    return dict()

@view_config(name="contact")
@view_config(route_name="contact")
@mobile_view_config(route_name="contact")
def contact_view(context, request):
    return HTTPFound(safe_get_contact_url(request, default=request.route_path("order_review.form")))

@mobile_view_config(route_name='order_review.qr_confirm', renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/order_review/qr_confirm.html"))
@view_config(route_name='order_review.qr_confirm', renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/order_review/qr_confirm.html"))
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

@view_config(route_name='order_review.qr', renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/order_review/qr.html"))
def order_review_qr_html(context, request):
    ticket_id = int(request.matchdict.get('ticket_id', 0))
    sign = request.matchdict.get('sign', 0)

    ticket = build_qr_by_history_id(request, ticket_id)
    
    if ticket == None or ticket.sign != sign:
        raise HTTPNotFound()

    if ticket.seat is None:
        gate = None
    else:
        gate = ticket.seat.attributes.get("gate", None)
    
    return dict(
        sign = sign,
        order = ticket.order,
        ticket = ticket,
        performance = ticket.performance,
        event = ticket.event,
        product = ticket.product,
        gate = gate
    )

@view_config(route_name='order_review.qrdraw', xhr=False, permission="view")
def order_review_qr_image(context, request):
    ticket_id = int(request.matchdict.get('ticket_id', 0))
    sign = request.matchdict.get('sign', 0)
    
    ticket = build_qr_by_history_id(request, ticket_id)
    
    if ticket == None or ticket.sign != sign:
        raise HTTPNotFound()
    return qrdata_as_image_response(ticket)

@mobile_view_config(route_name='order_review.qr_print', request_method='POST', renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/order_review/qr.html"))
@view_config(route_name='order_review.qr_print', request_method='POST', renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/order_review/qr.html"))
def order_review_qr_print(context, request):
    ticket = build_qr_by_token_id(request, request.params['order_no'], request.params['token'])
    ## historical reason. ticket variable is one of TicketPrintHistory object.
    if ticket.seat is None:
        gate = None
    else:
        gate = ticket.seat.attributes.get("gate", None)
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
        gate = gate
        )

@mobile_view_config(route_name='order_review.qr_send', request_method="POST", 
             renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/order_review/send.html"))
@view_config(route_name='order_review.qr_send', request_method="POST", 
             renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/order_review/send.html"))
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
             renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/order_review/qr.txt"))
@view_config(name="render.mail", 
             renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/order_review/qr.txt"))
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

@mobile_view_config(route_name='order_review.orion_send', request_method="POST", 
             renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/order_review/send.html"))
@view_config(route_name='order_review.orion_send', request_method="POST", 
             renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/order_review/send.html"))
def order_review_send_to_orion(context, request):
    # TODO: validate mail address
    
    mail = request.params['mail']
    # send mail using template
    form = schemas.SendMailSchema(request.POST)

    if not form.validate():
        return dict(mail=mail, 
                    message=u"Emailの形式が正しくありません")

    response = None
    try:
        res_text = api.send_to_orion(request, context, mail)
        response = json.loads(res_text)
        # TODO: 返り値を検証する

    except Exception, e:
        logger.error(e.message, exc_info=1)
        ## この例外は違う...
        raise HTTPNotFound()

    if response != None and response['result'] == u"OK":
        message = u"電子チケットについてのメールを%s宛に送信しました!!" % mail
    else:
        # そのまま出すのも微妙だがコード化されてないからしょうがない
        message = response.message

    return dict(
        mail = mail,
        message = message
        )
