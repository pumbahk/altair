# -*- coding:utf-8 -*-
import logging
import sqlahelper
import json
from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from altair.app.ticketing.cart.selectable_renderer import selectable_renderer
from altair.app.ticketing.qr.image import qrdata_as_image_response
from . import schemas
from . import api
from altair.mobile import mobile_view_config
from altair.app.ticketing.core.utils import IssuedAtBubblingSetter
from altair.app.ticketing.core.api import get_organization
from datetime import datetime
from altair.app.ticketing.mailmags.api import get_magazines_to_subscribe, multi_subscribe, multi_unsubscribe
from altair.app.ticketing.payments import plugins

import helpers as h
from ..users.api import get_user
from altair.app.ticketing.cart import api as cart_api
from altair.app.ticketing.qr.utils import build_qr_by_history_id
from altair.app.ticketing.qr.utils import build_qr_by_token_id, build_qr_by_orion
from altair.auth import who_api as get_who_api
from altair.app.ticketing.fc_auth.api import do_authenticate
from .api import safe_get_contact_url, is_mypage_organization, is_rakuten_auth_organization

from altair.app.ticketing.core.models import Order, OrderedProduct, OrderedProductItem, OrderedProductItemToken

logger = logging.getLogger(__name__)

DBSession = sqlahelper.get_session()

class InvalidForm(Exception):
    def __init__(self, form):
        self.form = form

class InvalidGuestForm(Exception):
    def __init__(self, form):
        self.form = form

class MypageView(object):

    def __init__(self, request):
        self.request = request
        self.context = request.context

    @mobile_view_config(route_name='mypage.show', request_method="GET", custom_predicates=(is_mypage_organization, ),
                 renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/mypage/show_mobile.html"))
    @mobile_view_config(route_name='mypage.show', request_method="GET", custom_predicates=(is_mypage_organization, is_rakuten_auth_organization), permission='rakuten_auth',
                 renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/mypage/show_mobile.html"))
    @view_config(route_name='mypage.show', request_method="GET", custom_predicates=(is_mypage_organization, ),
                 renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/mypage/show.html"))
    @view_config(route_name='mypage.show', request_method="GET", custom_predicates=(is_mypage_organization, is_rakuten_auth_organization), permission='rakuten_auth',
                 renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/mypage/show.html"))
    def show(self):

        authenticated_user = self.context.authenticated_user()
        user = get_user(authenticated_user)
        per = 10

        if not user:
            raise HTTPNotFound()

        shipping_address = self.context.get_shipping_address(user)
        page=self.request.params.get("page", 1)
        orders = self.context.get_orders(user, page, per)
        entries = self.context.get_lots_entries(user, page, per)

        magazines_to_subscribe = None
        if shipping_address:
            magazines_to_subscribe = get_magazines_to_subscribe(get_organization(self.request), shipping_address.emails)

        return dict(
            shipping_address=shipping_address,
            orders=orders,
            lot_entries=entries,
            mailmagazines_to_subscribe=magazines_to_subscribe,
            h=h,
        )

    @mobile_view_config(route_name='mypage.order.show', custom_predicates=(is_mypage_organization, ),
                 renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/mypage/order_show_mobile.html"))
    @mobile_view_config(route_name='mypage.order.show', custom_predicates=(is_mypage_organization, is_rakuten_auth_organization), permission='rakuten_auth',
                 renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/mypage/order_show_mobile.html"))
    @view_config(route_name='mypage.order.show', custom_predicates=(is_mypage_organization, ),
                 renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/mypage/order_show.html"))
    @view_config(route_name='mypage.order.show', custom_predicates=(is_mypage_organization, is_rakuten_auth_organization), permission='rakuten_auth',
                 renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/mypage/order_show.html"))
    def order_show(self):

        authenticated_user = self.context.authenticated_user()
        user = get_user(authenticated_user)

        if not user:
            raise HTTPNotFound()

        order, sej_order = self.context.get_order()

        if not order:
            raise HTTPNotFound()

        return dict(order=order, sej_order=sej_order, shipping_address=order.shipping_address)

    @mobile_view_config(route_name='mypage.mailmag.confirm', request_method="POST", custom_predicates=(is_mypage_organization, ),
                 renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/mypage/mailmag_confirm_mobile.html"))
    @mobile_view_config(route_name='mypage.mailmag.confirm', request_method="POST", custom_predicates=(is_mypage_organization, is_rakuten_auth_organization), permission='rakuten_auth',
                 renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/mypage/mailmag_confirm_mobile.html"))
    @view_config(route_name='mypage.mailmag.confirm', request_method="POST", custom_predicates=(is_mypage_organization, ),
                 renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/mypage/mailmag_confirm.html"))
    @view_config(route_name='mypage.mailmag.confirm', request_method="POST", custom_predicates=(is_mypage_organization, is_rakuten_auth_organization), permission='rakuten_auth',
                 renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/mypage/mailmag_confirm.html"))
    def mailmag_confirm(self):

        authenticated_user = self.context.authenticated_user()
        user = get_user(authenticated_user)

        if not user:
            raise HTTPNotFound()

        shipping_address = self.context.get_shipping_address(user)
        magazines_to_subscribe = get_magazines_to_subscribe(get_organization(self.request), shipping_address.emails)
        subscribe_ids = self.request.params.getall('mailmagazine')

        return dict(
            mails=shipping_address.emails,
            mailmagazines_to_subscribe=magazines_to_subscribe,
            subscribe_ids=subscribe_ids,
            h=h,
        )

    @mobile_view_config(route_name='mypage.mailmag.complete', request_method="POST", custom_predicates=(is_mypage_organization, ),
                 renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/mypage/mailmag_complete_mobile.html"))
    @mobile_view_config(route_name='mypage.mailmag.complete', request_method="POST", custom_predicates=(is_mypage_organization, is_rakuten_auth_organization), permission='rakuten_auth',
                 renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/mypage/mailmag_complete_mobile.html"))
    @view_config(route_name='mypage.mailmag.complete', request_method="POST", custom_predicates=(is_mypage_organization, ),
                 renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/mypage/mailmag_complete.html"))
    @view_config(route_name='mypage.mailmag.complete', request_method="POST", custom_predicates=(is_mypage_organization, is_rakuten_auth_organization), permission='rakuten_auth',
                 renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/mypage/mailmag_complete.html"))
    def mailmag_complete(self):

        authenticated_user = self.context.authenticated_user()
        user = get_user(authenticated_user)

        if not user:
            raise HTTPNotFound()

        shipping_address = self.context.get_shipping_address(user)
        magazines_to_subscribe = get_magazines_to_subscribe(get_organization(self.request), shipping_address.emails)
        emails = shipping_address.emails
        subscribe_ids = self.request.params.getall('mailmagazine')

        unsubscribe_ids = []
        for mailmagazine, subscribed in magazines_to_subscribe:
            if not str(mailmagazine.id) in subscribe_ids:
                unsubscribe_ids.append(mailmagazine.id)

        multi_subscribe(user, emails, subscribe_ids)
        multi_unsubscribe(user, emails, unsubscribe_ids)

        return dict(
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

    @view_config(request_method="GET", route_name='order_review.form', renderer='json', http_cache=60,
                 custom_predicates=(is_mypage_organization, ))
    def login_form(self):
        membership = self.context.get_membership().name
        self.select_renderer(membership)

        # このformは、モバイルのためだけに必要
        form = schemas.OrderReviewSchema(self.request.params)
        return dict(username='', form=form)

    @view_config(request_method="POST", route_name='order_review.form', renderer='string',
                 custom_predicates=(is_mypage_organization, ))
    def login(self):
        who_api = get_who_api(self.request, name="fc_auth")

        membership = self.context.get_membership().name
        username = self.request.params['username']
        password = self.request.params['password']

        authenticated = None
        headers = None
        identity = None

        result = do_authenticate(self.request, membership, username, password)
        if result is not None:
            # result には user_id が含まれているが、これを identity とすべきかは
            # 議論の余地がある。user_id を identity にしてしまえば DB 負荷を
            # かなり減らすことができるだろう。
            identity = {
                'login': True,
                'membership': membership,
                'username': username,
                }

        if identity is not None:
            authenticated, headers = who_api.login(identity)

        if authenticated is None:
            self.select_renderer(membership)
            return {'username': username,
                    'message': u'IDまたはパスワードが一致しません'}

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
    @mobile_view_config(route_name='guest.order_review.form',
                        request_method="GET", renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/order_review_mobile_guest/form.html"))
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
    def post(self):
        form = schemas.OrderReviewSchema(self.request.params)
        if not form.validate():
            raise InvalidForm(form)

        order, sej_order = self.context.get_order()
        if not form.object_validate(self.request, order):
            raise InvalidForm(form)
        return dict(order=order, sej_order=sej_order, shipping_address=order.shipping_address)

    @mobile_view_config(route_name='guest.order_review.show', request_method="POST",
                        renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/order_review_mobile_guest/show.html"))
    @view_config(route_name='guest.order_review.show',
                 renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/order_review_guest/show.html"))
    def guest_post(self):
        form = schemas.OrderReviewSchema(self.request.params)
        if not form.validate():
            raise InvalidGuestForm(form)

        order, sej_order = self.context.get_order()
        if not form.object_validate(self.request, order):
            raise InvalidGuestForm(form)
        return dict(order=order, sej_order=sej_order, shipping_address=order.shipping_address)

@mobile_view_config(context=InvalidForm,
                    renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/order_review_mobile/form.html"))
@view_config(context=InvalidForm, 
             renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/order_review/form.html"))
def order_review_form_view(context, request):
    request.errors = context.form.errors
    return dict(form=context.form)

@view_config(context=InvalidGuestForm,
             renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/order_review_guest/form.html"))
@mobile_view_config(context=InvalidGuestForm,
                    renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/order_review_mobile_guest/form.html"))
def guest_order_review_form_view(context, request):
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


@view_config(route_name='order_review.qrdraw', xhr=False)
def order_review_qr_image(context, request):
    ticket_id = int(request.matchdict.get('ticket_id', 0))
    sign = request.matchdict.get('sign', 0)
    
    ticket = build_qr_by_history_id(request, ticket_id)
    if ticket is None:
        raise HTTPNotFound()

    if ticket.order.payment_delivery_pair.delivery_method.delivery_plugin_id == plugins.ORION_DELIVERY_PLUGIN_ID:
        # orion
        try:
            res_text = api.send_to_orion(request, context, None, ticket.item_token)
            logger.info("response = %s" % res_text)
            response = json.loads(res_text)
            if response['result'] == u"OK" and response.has_key('serial'):
                qr = build_qr_by_orion(request, ticket, response['serial'])
                return qrdata_as_image_response(qr)

            ## エラーメッセージ
            if response.has_key('message'):
                r = Response(status=500, content_type="text/html; charset=UTF-8")
                r.text = response['message']
                return r
        except Exception, e:
            logger.error(e.message, exc_info=1)
            raise e

    else:
        if ticket == None or ticket.sign != sign:
            raise HTTPNotFound()
        return qrdata_as_image_response(ticket)

@mobile_view_config(route_name='order_review.qr_print', request_method='POST', renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/order_review/qr.html"))
@view_config(route_name='order_review.qr_print', request_method='POST', renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/order_review/qr.html"))
def order_review_qr_print(context, request):
    ticket = build_qr_by_token_id(request, request.params['order_no'], request.params['token'])
    ## historical reason. ticket variable is one of TicketPrintHistory object.

    issued_setter = IssuedAtBubblingSetter(datetime.now())
    issued_setter.issued_token(ticket.item_token)
    issued_setter.start_bubbling()
        
    if ticket.seat is None:
        gate = None
    else:
        gate = ticket.seat.attributes.get("gate", None)

    if ticket.order.payment_delivery_pair.delivery_method.delivery_plugin_id == plugins.ORION_DELIVERY_PLUGIN_ID:
        # orion
        try:
            if ticket.order.order_no != request.params['order_no']:
                raise Exception(u"Wrong order number or token: (%s, %s)" % (request.params['order_no'], request.params['token']))
            res_text = api.send_to_orion(request, context, None, ticket.item_token)
            logger.info("response = %s" % res_text)
            response = json.loads(res_text)
        except Exception, e:
            logger.exception(res_text)
            ## この例外は違う...
            raise HTTPNotFound()

        if response['result'] == u"OK" and response.has_key('serial'):
            qr = build_qr_by_orion(request, ticket, response['serial'])
        else:
            if response.has_key('message'):
                #return dict(
                #    event = ticket.order.performance.event,
                #    performance = ticket.order.performance,
                #    message = response['message']
                #)
                r = Response(status=500, content_type="text/html; charset=UTF-8")
                r.text = response['message']
                return r
            raise Exception()
        
        return dict(
            sign = qr.sign,
            order = ticket.order,
            ticket = ticket,
            performance = ticket.order.performance,
            event = ticket.order.performance.event,
            product = ticket.ordered_product_item.ordered_product.product,
            gate = gate
        )
    elif ticket.order.payment_delivery_pair.delivery_method.delivery_plugin_id == plugins.QR_DELIVERY_PLUGIN_ID:
        # altair
        
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
        sender = context.membership.organization.setting.default_mail_sender
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

    res_text = None
    try:
        data = OrderedProductItemToken.filter_by(id = request.params['token']).one()
        if data.item.ordered_product.order.order_no != request.params['order_no']:
            raise Exception(u"Wrong order number or token: (%s, %s)" % (request.params['order_no'], request.params['token']))
        res_text = api.send_to_orion(request, context, mail, data)
        logger.info("response = %s" % res_text)
    except Exception, e:
        logger.error(e.message, exc_info=1)
        ## この例外は違う...
        raise HTTPNotFound()

    response = None
    try:
        response = json.loads(res_text)
        # TODO: 返り値を検証する
    except Exception, e:
        logger.error(e.message + " (res_text: %s)" % res_text, exc_info=1)
        raise HTTPNotFound()

    if response != None and response['result'] == u"OK":
        return dict(mail=mail,
                    message = u"電子チケットについてのメールを%s宛に送信しました!!" % mail)
    
    # エラーメッセージ
    return dict(
        mail = mail,
        # そのまま出すのも微妙だがコード化されてないからしょうがない
        message = response['message']
        )
