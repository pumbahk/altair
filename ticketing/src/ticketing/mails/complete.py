# -*- coding:utf-8 -*-
from pyramid_mailer import get_mailer
from .api import get_complete_mail, preview_text_from_message, message_settings_override
import logging
logger = logging.getLogger(__name__)

import itertools
from pyramid import renderers
from pyramid_mailer.message import Message
from .interfaces import ICompleteMail
from .api import get_mailinfo_traverser
from zope.interface import implementer
from .api import create_or_update_mailinfo,  create_fake_order
from ticketing.cart import helpers as ch ##
from ticketing.core.models import MailTypeEnum
import functools

complete_mailinfo_traverser = functools.partial(
    get_mailinfo_traverser, 
    ## xxx: uggg
    access=lambda d, k, default="" : d.get(MailTypeEnum.CompleteMail, {}).get(k, default), 
    default=u"", 
)

__all__ = ["build_message", "send_mail", "preview_text", "create_or_update_mailinfo", "create_fake_order"]
def build_message(request, order):
    complete_mail = get_complete_mail(request)
    message = complete_mail.build_message(order)
    return message

def send_mail(request, order, override=None):
    mailer = get_mailer(request)
    message = build_message(request, order)
    message_settings_override(message, override)
    mailer.send(message)
    logger.info("send complete mail to %s" % message.recipients)

def preview_text(request, order):
    message = build_message(request, order)
    return preview_text_from_message(message)
   
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
        mail_from = self.get_email_from(organization)
        bcc = [mail_from]

        mail_body = self.build_mail_body(order)
        return Message(
            subject=subject,
            recipients=[order.shipping_address.email],
            bcc=bcc,
            body=mail_body,
            sender=mail_from)

    def _build_mail_body(self, order):
        sa = order.shipping_address 
        pair = order.payment_delivery_pair
        seats = itertools.chain.from_iterable((p.seats for p in order.ordered_products))

        traverser = complete_mailinfo_traverser(self.request, order)
        value = dict(h=ch, 
                     order=order,
                     name=u"{0} {1}".format(sa.last_name, sa.first_name),
                     name_kana=u"{0} {1}".format(sa.last_name_kana, sa.first_name_kana),
                     tel_no=sa.tel_1,
                     tel2_no=sa.tel_2,
                     email=sa.email,
                     order_no=order.order_no,
                     order_datetime=ch.mail_date(order.created_at), 
                     order_items=order.ordered_products,
                     order_total_amount=order.total_amount,
                     performance=order.performance,
                     system_fee=order.system_fee,
                     delivery_fee=order.delivery_fee,
                     transaction_fee=order.transaction_fee,
                     payment_method_name=pair.payment_method.name, 
                     delivery_method_name=pair.delivery_method.name, 
                     seats = seats, 
                     ### mail info
                     footer = traverser.data["footer"],
                     notice = traverser.data["notice"],
                     )
        return value

    def build_mail_body(self, order):
        value = self._build_mail_body(order)
        return renderers.render(self.mail_template, value, request=self.request)
