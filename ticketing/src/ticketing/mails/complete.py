# -*- coding:utf-8 -*-
from pyramid_mailer import get_mailer
from . import PURCHASE_MAILS
from .api import get_purchaseinfo_mail, preview_text_from_message, message_settings_override
from .api import get_mailinfo_traverser
from .api import create_or_update_mailinfo,  create_fake_order
from .forms import OrderInfoRenderer, OrderInfoDefault, OrderInfo
from ticketing.cart import helpers as ch ##
import logging
logger = logging.getLogger(__name__)

from pyramid import renderers
from pyramid_mailer.message import Message
from .interfaces import ICompleteMail
from zope.interface import implementer
from ticketing.core.models import MailTypeEnum
import functools

__all__ = ["build_message", "send_mail", "preview_text", "create_or_update_mailinfo", "create_fake_order"]

def access_data(data, k, default=""):
    try:
        return data[str(MailTypeEnum.CompleteMail)][k]
    except KeyError:
        return default

class OrderCompleteInfoDefault(OrderInfoDefault):
    tel = OrderInfo(name="tel", label=u"電話番号", getval=lambda order : order.shipping_address.tel_1 or "")
    mail = OrderInfo(name="mail", label=u"メールアドレス", getval=lambda order : order.shipping_address.email_1)

def get_mailtype_description():
    return u"購入完了メール"

def get_order_info_default():
    return OrderCompleteInfoDefault

get_traverser = functools.partial(get_mailinfo_traverser, access=access_data, default=u"")
get_complete_mail = functools.partial(get_purchaseinfo_mail, name=PURCHASE_MAILS["complete"])

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

    def get_mail_subject(self, organization, traverser):
        return (traverser.data["subject"] or 
                u"チケット予約受付完了のお知らせ 【{organization}】".format(organization=organization.name))

    def get_mail_sender(self, organization, traverser):
        return (traverser.data["sender"] or organization.contact_email)

    def build_message(self, order):
        organization = order.ordered_from or self.request.organization
        traverser = get_traverser(self.request, order)
        subject = self.get_mail_subject(organization, traverser)
        mail_from = self.get_mail_sender(organization, traverser)
        bcc = [mail_from]

        mail_body = self.build_mail_body(order)
        return Message(
            subject=subject,
            recipients=[order.shipping_address.email_1],
            bcc=bcc,
            body=mail_body,
            sender=mail_from)

    def _build_mail_body(self, order):
        sa = order.shipping_address 
        pair = order.payment_delivery_pair
        traverser = get_traverser(self.request, order)
        info_renderder = OrderInfoRenderer(order, traverser.data, default_impl=get_order_info_default())
        value = dict(h=ch, 
                     order=order,
                     get=info_renderder.get, 
                     name=u"{0} {1}".format(sa.last_name, sa.first_name),
                     payment_method_name=pair.payment_method.name, 
                     delivery_method_name=pair.delivery_method.name, 
                     ### mail info
                     footer = traverser.data["footer"],
                     notice = traverser.data["notice"],
                     header = traverser.data["header"],
                     )
        return value

    def build_mail_body(self, order):
        value = self._build_mail_body(order)
        return renderers.render(self.mail_template, value, request=self.request)
