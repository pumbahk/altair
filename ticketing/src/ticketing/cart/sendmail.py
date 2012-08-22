# -*- coding:utf-8 -*-
from pyramid import renderers
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
from . import logger
from .api import get_complete_mail
from zope.interface import implementer
from .interfaces import ICompleteMail
from . import helpers as h

## dummy mailer
from pyramid_mailer.interfaces import IMailer
@implementer(IMailer)
class DevNullMailer(object):
    """
    this is like a pyramid_mailer.mailer.DummyMailer.
    but, this class *does not* store sent mail.
    """
    def send(self, message):    
        logger.info("*mail* send %s" % message)

    def send_immediately(self, message, fail_silently=False):
        logger.info("*mail* send_immediately(fail_silently=%s) %s" % (fail_silently, message))


    def send_to_queue(self, message):
        logger.info("*mail* send to queue %s" % message)

def devnull_mailer(config):
    mailer = DevNullMailer()
    config.registry.registerUtility(mailer, IMailer)

def on_order_completed(order_completed):
    order = order_completed.order
    request = order_completed.request
    message = create_message(request, order)
    mailer = get_mailer(request) ## todo.component化
    mailer.send(message)
    logger.info("send mail to %s" % message.recipients)

def create_message(request, order):
    complete_mail = get_complete_mail(request)
    return complete_mail.build_message(order)

@implementer(ICompleteMail)
class CompleteMail(object):
    def __init__(self, mail_template, request):
        self.mail_template = mail_template
        self.request = request

    def get_subject(self, organization):
        return u"チケット予約受付完了のお知らせ 【{organization.name}】".format(organization=organization)

    def get_email_from(self, organization):
        return organization.contact_email

    def build_message(self, order):
        organization = order.ordered_from
        subject = self.get_subject(organization)
        from_ = self.get_email_from(organization)
        mail_body = self.build_mail_body(order)
        return Message(
            subject=subject,
            recipients=[order.shipping_address.email],
            bcc=[from_],
            body=mail_body,
            sender=from_)

    def _build_mail_body(self, order):
        sa = order.shipping_address 
        pair = order.payment_delivery_pair
        seats = [dict(name=s.name, seat_no=s.seat_no)
                 for product in order.ordered_products
                 for item in product.ordered_product_items 
                 for s in item.seats]

        value = dict(order=order,
                name=u"{0} {1}".format(sa.last_name, sa.first_name),
                name_kana=u"{0} {1}".format(sa.last_name_kana, sa.first_name_kana),
                tel_no=sa.tel_1,
                tel2_no=sa.tel_2,
                email=sa.email,
                order_no=order.order_no,
                order_datetime=h.mail_date(order.created_at), 
                order_items=order.ordered_products,
                order_total_amount=order.total_amount,
                performance_name=order.performance.name,
                system_fee=order.system_fee,
                delivery_fee=order.delivery_fee,
                transaction_fee=order.transaction_fee,
                payment_method_name=pair.payment_method.name, 
                delivery_method_name=pair.delivery_method.name, 
                seats = seats
                     )
        return value

    def build_mail_body(self, order):
        value = self._build_mail_body(order)
        return renderers.render(self.mail_template, value, request=self.request)
