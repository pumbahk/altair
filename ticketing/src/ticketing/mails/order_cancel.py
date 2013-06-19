# -*- coding:utf-8 -*-
from pyramid import renderers
from pyramid_mailer.message import Message
import logging
from .forms import OrderInfoRenderer
from .forms import OrderInfoDefault, OrderInfo, OrderInfoWithValue
from ticketing.cart import helpers as ch ##
from .interfaces import ICancelMail
from zope.interface import implementer
from .api import create_or_update_mailinfo,  create_fake_order

logger = logging.getLogger(__name__)

class OrderCancelInfoDefault(OrderInfoDefault):
    def get_shipping_address_info(order):
        sa = order.shipping_address
        params = dict(last_name = sa.last_name, 
                      first_name = sa.first_name, 
                      zip = sa.zip, 
                      prefecture = sa.prefecture, 
                      city = sa.city, 
                      address_1 = sa.address_1, 
                      address_2 = sa.address_2)
        return u"""\
${last_name} ${first_name} 様
〒 ${zip}
${prefecture} ${city}
${address_1} ${address_2}""" % params

    ordered_from = OrderInfo(name=u"ordered_from", label=u"販売会社", getval=lambda order: order.ordered_from.name)
    payment_method = OrderInfo(name=u"payment_method", label=u"支払方法",  getval=lambda order: order.payment_delivery_pair.payment_method.name)
    delivery_method = OrderInfo(name=u"delivery_method", label=u"引取方法",  getval=lambda order: order.payment_delivery_pair.delivery_method.name)
    address = OrderInfo(name="address", label=u"送付先", getval=get_shipping_address_info)

    cancel_reason_default=u"""\
　・お客様からキャンセルのご連絡があったため
　・期限内のご入金がなくキャンセル扱いとしたため
　・二重注文により、ひとつをキャンセル処理したため
"""
    ## getvalが文字列の場合は、input formになり文言を変更できる
    cancel_reason = OrderInfoWithValue(name="cancel_reason", label=u"キャンセル理由", 
                                       getval=lambda order: OrderCancelInfoDefault.cancel_reason_default, value=cancel_reason_default)
    
def get_subject_info_default():
    return OrderCancelInfoDefault()

def get_mailtype_description():
    return u"購入キャンセルメール"

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

    def build_message(self, order, traverser):
        if not self.validate(order):
            logger.warn("validation error")
            return 

        organization = order.ordered_from or self.request.context.organization
        subject = self.get_mail_subject(organization, traverser)
        mail_from = self.get_mail_sender(organization, traverser)
        bcc = [mail_from]

        mail_body = self.build_mail_body(order, traverser)
        return Message(
            subject=subject,
            recipients=[order.shipping_address.email_1],
            bcc=bcc,
            body=mail_body,
            sender=mail_from)

    def _build_mail_body(self, order, traverser):
        sa = order.shipping_address 
        pair = order.payment_delivery_pair
        info_renderder = OrderInfoRenderer(order, traverser.data, default_impl=OrderCancelInfoDefault)
        title=order.performance.event.title,
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

    def build_mail_body(self, order, traverser):
        value = self._build_mail_body(order, traverser)
        return renderers.render(self.mail_template, value, request=self.request)
