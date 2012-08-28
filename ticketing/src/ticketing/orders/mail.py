# -*- coding:utf-8 -*-

from pyramid import renderers
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

from ticketing.cart import helpers as h

import logging

logger = logging.getLogger(__name__)

mail_renderer_names = {
    '1': 'ticketing:templates/mail/order_cancel.txt',
    '2': 'ticketing:templates/mail/order_cancel.txt',
    '3': 'ticketing:templates/mail/order_cancel.txt',
    '4': 'ticketing:templates/mail/order_cancel.txt',
}

def on_order_canceled(event):
    message = create_cancel_message(event.request, event.order)
    mailer = get_mailer(event.request)
    mailer.send(message)
    logger.info('send cancel mail to %s' % message.recipients)

def create_cancel_message(request, order):
    plugin_id = str(order.payment_delivery_pair.payment_method.payment_plugin_id)
    if plugin_id not in mail_renderer_names:
        logger.warn('mail renderer not found for plugin_id %s' % plugin_id)
        return

    subject = u'ご注文キャンセルについて 【{organization.name}】'.format(organization=order.ordered_from)
    from_ = order.ordered_from.contact_email
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

    value = dict(
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
    )
    mail_body = renderers.render(mail_renderer_names[plugin_id], value, request=request)
    mail_body = unicode(mail_body, 'utf-8')

    message = Message(
        subject=subject,
        recipients=[order.shipping_address.email],
        body=mail_body,
        sender=from_)
    return message
