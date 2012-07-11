# -*- coding:utf-8 -*-
from pyramid import renderers
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
import logging
from ticketing.sej.models import SejOrder

logger = logging.getLogger(__name__)

mail_renderer_names = {
    '1': 'mail/89ERS_Completion_EMAIL_NEW_CreditCard.txt',
    '3': 'mail/89ERS_Completion_EMAIL_NEW_SEJ.txt',
    '4': 'mail/89ERS_Completion_EMAIL_NEW_Combined.txt',
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
    if plugin_id not in mail_renderer_names:
        logger.warn('mail renderer not found for plugin_id %s' % plugin_id)
        return
    renderer_name = mail_renderer_names[plugin_id]
    organization = order.ordered_from
    subject = u"受付完了メール 【{organization.name}】".format(organization=organization)
    from_ = u"order@ticket.rakuten.co.jp"
    sa = order.shipping_address 
    value = dict(order=order,
                name=u"{0} {1}".format(sa.last_name, sa.first_name),
                name_kana=u"{0} {1}".format(sa.last_name_kana, sa.first_name_kana),
                tel_no=sa.tel_1,
                email=sa.email,
                order_no=order.order_no,
                order_datetime=u'{d.year}年 {d.month}月 {d.day}日 {d.hour}時 {d.minute}分'.format(d=order.created_at),
                order_items=order.ordered_products,
                order_total_amount=order.total_amount,
                performance_name=order.performance.name,
                system_fee=order.system_fee,
                delivery_fee=order.delivery_fee,
                transaction_fee=order.transaction_fee,
                 )
    populate_with_extra_info = extra_info_populators.get(plugin_id)
    populate_with_extra_info and populate_with_extra_info(order, value)
    mail_body = renderers.render(renderer_name, value, request=request)

    message = Message(
        subject=subject,
        recipients=[sa.email],
        body=mail_body,
        sender=from_)
    return message
