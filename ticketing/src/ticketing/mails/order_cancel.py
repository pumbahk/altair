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
from .api import get_purchaseinfo_mail
from . import PURCHASE_MAILS
from ticketing.core.models import MailTypeEnum
import logging
from . import forms
from .forms import OrderInfoRenderer, OrderInfoDefault, OrderInfo, OrderInfoWithValue
from ticketing.cart import helpers as ch ##
from .interfaces import ICancelMail
from zope.interface import implementer

logger = logging.getLogger(__name__)

__all__ = ["build_message", "send_mail", "preview_text", "create_or_update_mailinfo", "create_fake_order"]

def access_data(data, k, default=""):
    try:
        return data[str(MailTypeEnum.PurchaseCancelMail)][k]
    except KeyError:
        return default


class OrderCancelInfoDefault(OrderInfoDefault):
    def get_shipping_address_info(order):
        sa = order.shipping_address
        params = dict(last_name = sa.last_name, 
                      first_name = sa.first_name, 
                      zip = sa.zip, 
                      prefecture = sa.prefecture, 
                      city = sa.city, 
                      addres_1 = sa.addres_1, 
                      addres_2 = sa.addres_2)
        return u"""\
${last_name} ${first_name} 様
〒 ${zip}
${prefecture} ${city}
${address_1} ${address_2}""" % params

    ordered_from = OrderInfo(name=u"ordered_from", label=u"販売会社", getval=lambda order: order.ordered_from.name)
    payment_method = OrderInfo(name=u"payment_method", label=u"支払方法",  getval=lambda order: order.payment_delivery_pair.payment_method.name)
    delivery_method = OrderInfo(name=u"delivery_method", label=u"引取方法",  getval=lambda order: order.delivery_delivery_pair.delivery_method.name)
    address = OrderInfo(name="address", label=u"送付先", getval=get_shipping_address_info)

    cancel_reason_default=u"""\
　・お客様からキャンセルのご連絡があったため
　・期限内のご入金がなくキャンセル扱いとしたため
　・二重注文により、ひとつをキャンセル処理したため
"""
    ## getvalが文字列の場合は、input formになり文言を変更できる
    cancel_reason = OrderInfoWithValue(name="cancel_reason", label=u"キャンセル理由", 
                                       getval=lambda order: OrderCancelInfoDefault.cancel_reason_default, value=cancel_reason_default)
    
def get_order_info_default():
    return OrderCancelInfoDefault()

def get_mailtype_description():
    return u"購入キャンセルメール"

get_traverser = functools.partial(get_mailinfo_traverser, access=access_data, default=u"")
get_cancel_mail = functools.partial(get_purchaseinfo_mail, name=PURCHASE_MAILS["cancel"])

def build_message(request, order):
    cancel_mail = get_cancel_mail(request)
    message = cancel_mail.build_message(order)
    return message

def send_mail(request, order, override=None):
    mailer = get_mailer(request)
    message = build_message(request, order)
    message_settings_override(message, override)
    mailer.send(message)
    logger.info("send cancel mail to %s" % message.recipients)

def preview_text(request, order):
    message = build_message(request, order)
    return preview_text_from_message(message)

create_cancel_message = build_message

## 不要?
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

@implementer(ICancelMail)    
class CancelMail(object):
    def __init__(self, mail_template, request):
        self.mail_template = mail_template
        self.request = request

    def get_mail_subject(self, organization, traverser):
        return (traverser.data["subject"] or 
                u'ご注文キャンセルについて 【{organization}】'.format(organization=organization.name))

    def get_mail_sender(self, organization, traverser):
        return (traverser.data["sender"] or organization.contact_email)

    def validate(self, order):
        if not order.shipping_address or not order.shipping_address.email_1:
            logger.info('order has not shipping_address or email id=%s' % order.id)
        return True

    def build_message(self, order):
        if not self.validate(order):
            logger.warn("validation error")
            return 

        organization = order.ordered_from or self.request.context.organization
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
        info_renderder = OrderInfoRenderer(order, traverser.data, default_impl=OrderCancelInfoDefault)
        title=order.ordered_products[0].product.event.title,
        value = dict(h=ch, 
                     order=order,
                     title=title, 
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
