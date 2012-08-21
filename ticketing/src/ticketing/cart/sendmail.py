# -*- coding:utf-8 -*-
from pyramid import renderers
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
from . import logger
from .api import get_complete_mail
from zope.interface import implementer
from .interfaces import ICompleteMail


def on_order_completed(order_completed):
    order = order_completed.order
    request = order_completed.request
    message = create_message(order)
    mailer = get_mailer(request) ## todo.component化
    mailer.send(message)
    logger.info("send mail to %s" % message.recipients)

def create_message(request, order):
    complete_mail = get_complete_mail(request)
    return complete_mail.send_mail(order)

@implementer(ICompleteMail)
class CompleteMail(object):
    def __init__(self, mail_template, request):
        self.mail_template = mail_template
        self.request = request

    def get_subject(self, organization):
        return u"受付完了メール 【{organization.name}】".format(organization=organization)

    def get_email_from(self, order):
        raise NotImplemented()

    def send_mail(self, order):
        organization = order.ordered_from
        subject = self.get_subject(organization)
        from_ = self.get_email_from(order)
        mail_body = self.build_mail_body(order)
        return Message(
            subject=subject,
            recipients=[order.shipping_address.email],
            bcc=[from_],
            body=mail_body,
            sender=from_)

    def build_mail_body(self, order):
        sa = order.shipping_address 
        value = dict(order=order,
                name=u"{0} {1}".format(sa.last_name, sa.first_name),
                name_kana=u"{0} {1}".format(sa.last_name_kana, sa.first_name_kana),
                tel_no=sa.tel_1,
                tel2_no=sa.tel_2,
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
        return renderers.render(self.mail_template, value, request=self.request)
