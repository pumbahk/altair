# -*- coding:utf-8 -*-
from pyramid import renderers
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
import logging
from ticketing.sej.models import SejOrder
from .api import get_booster_settings
logger = logging.getLogger(__name__)

mail_renderer_names = {
    '1': 'mail/default_Completion_EMAIL_NEW_CreditCard.txt',
    '3': 'mail/default_Completion_EMAIL_NEW_SEJ.txt',
    '4': 'mail/default_Completion_EMAIL_NEW_Combined.txt',
}

extra_info_populators = {
    '3': lambda order, value: value.update(dict(sej_order=SejOrder.filter(SejOrder.order_id == order.order_no).first())),
}

def on_order_completed(order_completed):
    order = order_completed.order
    request = order_completed.request
    message = create_message(request, order)
    mailer = get_mailer(request)
    mailer.send(message)
    logger.info("send mail to %s" % message.recipients)

def create_message(request, order):
    plugin_id = str(order.payment_delivery_pair.payment_method.payment_plugin_id)
    bsettings = get_booster_settings(request)
    renderer_names = getattr(bsettings, "mail_renderer_names", mail_renderer_names)
    if plugin_id not in renderer_names:
        logger.warn('mail renderer not found for plugin_id %s' % plugin_id)
        return
    renderer_name = renderer_names[plugin_id]
    organization = order.ordered_from
    subject = getattr(bsettings, "mail_subject", None) or u"受付完了メール 【{organization.name}】".format(organization=organization)
    #from_ = u"89ers@ticketstar.jp"

    from_ = bsettings.mail_sender 
    shipping_address = order.shipping_address 
    value = dict(
        order=order,
        name=u"{0} {1}".format(
            shipping_address.last_name,
            shipping_address.first_name),
        name_kana=u"{0} {1}".format(
            shipping_address.last_name_kana,
            shipping_address.first_name_kana),
        tel_no=shipping_address.tel_1,
        tel2_no=shipping_address.tel_2,
        email_1=shipping_address.email_1,
        order_no=order.order_no,
        order_datetime=\
            u'{d.year}年 {d.month}月 {d.day}日 {d.hour}時 {d.minute}分' \
            .format(d=order.created_at),
        order_items=order.ordered_products,
        order_total_amount=order.total_amount,
        performance_name=order.performance.name,
        system_fee=order.system_fee,
        delivery_fee=order.delivery_fee,
        transaction_fee=order.transaction_fee,
        delivery_method_name=order.payment_delivery_pair.delivery_method.name
        )
    populators = getattr(bsettings, "mail_extra_info_populators", extra_info_populators)
    populate_with_extra_info = populators.get(plugin_id)
    populate_with_extra_info and populate_with_extra_info(order, value)
    mail_body = renderers.render(renderer_name, value, request=request)

    message = Message(
        subject=subject,
        recipients=[shipping_address.email_1],
        bcc=[from_],
        body=mail_body,
        sender=from_)
    return message
