# -*- coding:utf-8 -*-
import logging
from pyramid.view import render_view_to_response
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
from altair.app.ticketing.core.api import get_organization_setting
from altair.app.ticketing.cart import api as cart_api
from altair.app.ticketing.cart.api import get_organization
from altair.app.ticketing.mails.api import get_appropriate_message_part
import altair.app.ticketing.orders.orion as orion_api
from pyramid.threadlocal import get_current_registry
from altair.app.ticketing.qr.utils import get_matched_token_from_token_id
from altair.sqlahelper import get_db_session

from altair.app.ticketing.orders.models import (
    Order,
    OrderedProduct,
    OrderedProductItem,
    OrderedProductItemToken,
    )

logger = logging.getLogger(__name__)

def send_qr_mail(request, context, recipient, sender):
    mail_body = get_mailbody_from_viewlet(request, context, "render.mail")
    return _send_mail_simple(request, recipient, sender, mail_body, 
                             subject=u"QRチケットに関しまして", )

def get_mailbody_from_viewlet(request, context, viewname):
    response = render_view_to_response(context, request, name=viewname)
    if response is None:
        raise ValueError
    return response.text

def _send_mail_simple(request, recipient, sender, mail_body, subject=u"QRチケットに関しまして"):
    message = Message(
            subject=subject, 
            recipients=[recipient], 
            #bcc=bcc,
            body=get_appropriate_message_part(request, recipient, mail_body),
            sender=sender)
    return get_mailer(request).send(message)

def send_to_orion(request, context, recipient, data):
    order = data.item.ordered_product.order
    product = data.item.ordered_product.product
    item = data.item
    performance = product.performance
    event = performance.event
    site = performance.venue.site
    org = event.organization
    segment = order.sales_segment
    seat = data.seat
    orion = performance.orion
    
    obj = dict()
    obj['token'] = data.id
    obj['recipient'] = dict(mail = recipient)
    obj['order'] = dict(number = order.order_no,
                        sequence = data.serial,
                        created_at = str(order.paid_at))
    obj['performance'] = dict(code = performance.code, name = performance.name,
                              open_on = str(performance.open_on) if performance.open_on is not None else None,
                              start_on = str(performance.start_on) if performance.start_on is not None else None,
                              end_on = str(performance.end_on) if performance.end_on is not None else None)
    obj['performance']['event'] = dict(code = event.code, title = event.title, abbreviated_title = event.abbreviated_title)
    obj['performance']['site'] = dict(name = site.name, prefecture = site.prefecture, address = (site.city or u'')+(site.address_1 or u'')+(site.address_2 or u''), phone = site.tel_1)
    obj['performance']['organization'] = dict(code = org.code, name = org.name)
    obj['performance']['web'] = orion.web
    obj['segment'] = dict(name = segment.name)
    obj['product'] = dict(name = product.name, price = int(product.price))
    if seat is not None:
        obj['seat'] = dict(name = seat.name, type = seat.stock.stock_type.name, number = seat.seat_no)
        for k, v in seat.attributes.items():
            if k not in obj['seat']:
                obj['seat'][k] = v
    else:
        obj['seat'] = dict(name = product.seat_stock_type.name, type = product.seat_stock_type.name)
    obj['coupons'] = list()
    obj['coupons'].append(dict(name = seat.name if seat is not None else product.name,
                               qr = (orion.qr_enabled==1),
                               pattern = orion.pattern))
    if (not orion.coupon_2_name is None) and (not orion.coupon_2_name == u''):
        obj['coupons'].append(dict(name = orion.coupon_2_name, qr = (orion.coupon_2_qr_enabled==1), pattern = orion.coupon_2_pattern))
    obj['instruction'] = dict(general = orion.instruction_general,
                              performance = orion.instruction_performance)
    obj['theme'] = dict(header = orion.header_url,
                        background = orion.background_url,
                        icon = orion.icon_url)
    
    return orion_api.create(request, obj)

def is_mypage_organization(context, request):
    organization = get_organization(request)
    return organization.setting.enable_mypage

def is_rakuten_auth_organization(context, request):
    organization = cart_api.get_organization(request)
    rakuten_auth_orgs = [15]
    for org in rakuten_auth_orgs:
        if organization.id == org:
            return True
    return False
