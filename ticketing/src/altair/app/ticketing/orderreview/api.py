# -*- coding:utf-8 -*-
import logging
import hashlib
from pyramid.view import render_view_to_response
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

from altair.app.ticketing.cart import api as cart_api
from altair.app.ticketing.cart.api import get_organization
from altair.app.ticketing.mails.api import get_appropriate_message_part
from altair.app.ticketing.orders import orion as orion_api

from .models import ReviewAuthorization
logger = logging.getLogger(__name__)


def send_qr_mail(request, context, recipient, sender, subject):
    mail_body = get_mailbody_from_viewlet(request, context, "render.mail")
    return _send_mail_simple(request, recipient, sender, mail_body, subject=subject)


def send_qr_aes_mail(request, context, recipient, sender):
    mail_body = get_mailbody_from_viewlet(request, context, "render.mail_aes")
    return _send_mail_simple(request, recipient, sender, mail_body, subject=u"QRチケットに関しまして")


def send_qr_ticket_mail(request, context, recipient, sender):
    mail_body = get_mailbody_from_viewlet(request, context, "render.mail_qr_ticket")
    subject = u'【{}】QRチケットに関しまして'.format(context.organization.name)
    return _send_mail_simple(request, recipient, sender, mail_body, subject=subject)


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

def _build_orion_ticket_phone_verify(owner_phone_number, orion_ticket_phones):
    if owner_phone_number and orion_ticket_phones:
        return owner_phone_number + ',' + orion_ticket_phones
    elif owner_phone_number:
        return owner_phone_number
    elif orion_ticket_phones:
        return orion_ticket_phones
    else:
        return u''


def send_to_orion(request, context, recipient, data):
    order = data.item.ordered_product.order
    ordered_product_item = data.item
    ordered_product = data.item.ordered_product
    product_item = data.item.product_item
    product = data.item.ordered_product.product
    performance = product.performance
    event = performance.event
    site = performance.venue.site
    org = event.organization
    segment = order.sales_segment
    seat = data.seat
    orion = performance.orion
    owner_phone_number = order.get_send_to_orion_owner_phone_string(request)
    orion_ticket_phones = order.get_send_to_orion_phone_string(request)
    orion_ticket_phone_verify = _build_orion_ticket_phone_verify(owner_phone_number, orion_ticket_phones)
    shipping_address = order.shipping_address
    obj = dict()
    obj['token'] = data.id
    obj['recipient'] = dict(mail = recipient)
    obj['order'] = dict(number = order.order_no,
                        owner_phone_number=owner_phone_number,
                        orion_ticket_phone_verify=orion_ticket_phone_verify,
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
    obj['segment'] = dict(name=segment.name)
    obj['product'] = dict(name=product.name,
                          price=int(product_item.price),
                          item_name=product_item.name,
                          ordered_product_id=ordered_product.id,
                          ordered_item_id=ordered_product_item.id,
                          product_id=product.id,
                          product_item_id=product_item.id)
    obj['buyer'] = dict(first_name=shipping_address.first_name,
                        last_name=shipping_address.last_name)
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
                               toggle_enabled = (orion.toggle_enabled==1),
                               phone_verify_disabled = (orion.phone_verify_disabled==1),
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


def create_review_authorization(order_no, review_password, email, type):
    """
    ReviewAuthorizationテーブルへのInsert処理を実施します。
    :param order_no: 予約番号
    :param review_password: 受付確認用パスワード
    :param email: メールアドレス
    :param type: 区分コード
    :return: ReviewAuthorizationテーブルの主キー
    """
    review_authorization = ReviewAuthorization(
        order_no=order_no,
        review_password=hashlib.md5(review_password).hexdigest(),
        email=email,
        type=type
    )

    return ReviewAuthorization.create_review_authorization(review_authorization) 