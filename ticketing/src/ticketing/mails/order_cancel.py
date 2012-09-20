# -*- coding:utf-8 -*-
from pyramid_mailer import get_mailer
from pyramid import renderers
from pyramid_mailer.message import Message
import functools
from .api import preview_text_from_message
from .api import message_settings_override
from .api import create_or_update_mailinfo
from .api import create_fake_order
from .api import get_mailinfo_traverser
from .api import get_mail_utility
from ticketing.cart import helpers as h
from ticketing.core.models import MailTypeEnum
import logging
from . import forms


logger = logging.getLogger(__name__)

__all__ = ["build_message", "send_mail", "preview_text", "create_or_update_mailinfo", "create_fake_order"]

empty = {}
get_traverser = functools.partial(
    get_mailinfo_traverser, 
    ## xxx: uggg
    access=lambda d, k, default="" : d.get(str(MailTypeEnum.PurchaseCancelMail), empty).get(k, default), 
    default=u"", 
)

def build_message(request, order):
    return create_cancel_message(request, order)

def preview_text(request, order):
    message = create_cancel_message(request, order)
    return preview_text_from_message(message)

def send_mail(request, order, override=None):
    mailer = get_mailer(request)
    message = create_cancel_message(request, order)
    message_settings_override(message, override)
    mailer.send(message)
    logger.info("send cancel mail to %s" % message.recipients)


mail_renderer_names = {
    '1': 'ticketing:templates/mail/order_cancel.txt',
    '2': 'ticketing:templates/mail/order_cancel.txt',
    '3': 'ticketing:templates/mail/order_cancel.txt',
    '4': 'ticketing:templates/mail/order_cancel.txt',
}

def payment_notice(request, order):
    get_mail_utility(request, MailTypeEnum.PurchaseCancelMail)
    trv = get_traverser(request, order)
    notice=trv.data[forms.MailInfoTemplate.payment_key(order, "notice")]
    return notice

def delivery_notice(request, order):
    get_mail_utility(request, MailTypeEnum.PurchaseCancelMail)
    trv = get_traverser(request, order)
    notice=trv.data[forms.MailInfoTemplate.delivery_key(order, "notice")]
    return notice
    
def create_cancel_message(request, order):
    if not order.shipping_address or not order.shipping_address.email:
        logger.info('order has not shipping_address or email id=%s' % order.id)
        return

    plugin_id = str(order.payment_delivery_pair.payment_method.payment_plugin_id)
    if plugin_id not in mail_renderer_names:
        logger.warn('mail renderer not found for plugin_id %s' % plugin_id)
        return

    traverser = get_traverser(request, order)
    subject = (traverser.data["sender"] or u'ご注文キャンセルについて 【{organization.name}】'.format(organization=order.ordered_from))
    from_ = (traverser.data["sender"] or order.ordered_from.contact_email)
    product_message_format = u'{product}　{price}（円）× {quantity}\r\n'
    products = ''
    for ordered_product in order.ordered_products:
        products += product_message_format.format(
            product=ordered_product.product.name,
            price=h.format_currency(ordered_product.price),
            quantity=ordered_product.quantity,
        )

    performance = order.ordered_products[0].ordered_product_items[0].product_item.performance
    venue_info = ''
    if performance.venue.id != 1:  # ダミー会場でないなら
        venue_info = u'{venue} ({start_on}開演)'.format(venue=performance.venue.name, start_on=performance.start_on)
    pair = order.payment_delivery_pair

    value = dict(
        h=h, 
        order=order,
        sa=order.shipping_address,
        products=products,
        venue=venue_info,
        title=order.ordered_products[0].product.event.title,
        system_fee=h.format_currency(order.system_fee),
        transaction_fee=h.format_currency(order.transaction_fee),
        delivery_fee=h.format_currency(order.delivery_fee),
        total_amount=h.format_currency(order.total_amount),
        contact_email=order.ordered_from.contact_email,
        payment_method_name=pair.payment_method.name, 
        delivery_method_name=pair.delivery_method.name, 

        ### mail info
        footer = traverser.data["footer"],
        notice = traverser.data["notice"],
        header = traverser.data["header"],
    )
    mail_body = renderers.render(mail_renderer_names[plugin_id], value, request=request)
    mail_body = unicode(mail_body, 'utf-8')
    from_ = order.ordered_from.contact_email

    message = Message(
        subject=subject,
        recipients=[order.shipping_address.email],
        bcc=[from_], 
        body=mail_body,
        sender=from_)
    return message
