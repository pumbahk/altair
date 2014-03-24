# -*- coding:utf-8 -*-
import logging
from pyramid.view import render_view_to_response
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
from altair.app.ticketing.core.api import get_organization, get_organization_setting, is_mobile_request
from altair.app.ticketing.mails.api import get_appropriate_message_part
from pyramid.threadlocal import get_current_registry
from altair.app.ticketing.core import api as c_api
from altair.app.ticketing.qr.utils import get_matched_token_from_token_id
import urllib
import urllib2
import json

from altair.app.ticketing.core.models import Order, OrderedProduct, OrderedProductItem, OrderedProductItemToken

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

def get_contact_url(request, fail_exc=ValueError):
    organization = get_organization(request)
    if organization is None:
        raise fail_exc("organization is not found")
    setting = get_organization_setting(request, organization)
    if is_mobile_request(request):
        if setting.contact_mobile_url is None:
            raise fail_exc("contact url is not found. (organization_id = %s)" % (organization.id))
        return setting.contact_mobile_url
    else:
        if setting.contact_pc_url is None:
            raise fail_exc("contact url is not found. (organization_id = %s)" % (organization.id))
        return setting.contact_pc_url

def safe_get_contact_url(request, default=""):
    try:
        return get_contact_url(request, Exception)
    except Exception as e:
        logger.warn(str(e))
        return default

def send_to_orion(request, context, recipient, ticket):
    settings = request.registry.settings
    api_url = settings.get('orion.create_url')
    if api_url is None:
        raise Exception("orion.api_uri is None")
    print "target url is %s" % api_url
    
    order = ticket.order
    product = ticket.product
    item = ticket.ordered_product_item.product_item
    performance = ticket.performance
    event = performance.event
    site = performance.venue.site
    org = event.organization
    segment = order.sales_segment
    seat = ticket.seat
    orion = performance.orion
    
    obj = dict()
    obj['token'] = ticket.item_token_id
    obj['recipient'] = dict(mail = recipient)
    obj['order'] = dict(number = order.order_no,
                        sequence = ticket.item_token.serial,
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
        obj['seat'] = dict(name = product.seat_stock_type.name)
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
    
    data = json.dumps(obj)
    logger.info("Create request to Orion API: %s" % data);
    req = urllib2.Request(api_url, data, headers={ u'Content-Type': u'text/json; charset="UTF-8"' })
    stream = urllib2.urlopen(req);
    headers = stream.info()
    if stream.code == 200:
        res = unicode(stream.read(), 'utf-8')
        return res
    else:
        raise Exception("server returned unexpected status: %d (payload) %r" % (stream.code, stream.read()))

def is_mypage_organization(context, request):
    organization = c_api.get_organization(request)
    mypage_orgs = [15, 24]
    for org in mypage_orgs:
        if organization.id == org:
            return True
    return False

def is_rakuten_auth_organization(context, request):
    organization = c_api.get_organization(request)
    rakuten_auth_orgs = [15]
    for org in rakuten_auth_orgs:
        if organization.id == org:
            return True
    return False
