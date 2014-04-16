# -*- coding:utf-8 -*-
from pyramid.renderers import render
from pyramid_mailer.message import Message
from pyramid.compat import text_type
import logging
from .forms import SubjectInfoRenderer
from .forms import OrderInfoDefault, SubjectInfo, SubjectInfoWithValue
from altair.app.ticketing.cart import helpers as ch ##
from .interfaces import IPurchaseInfoMail
from zope.interface import implementer
from .api import create_or_update_mailinfo,  create_fake_order, get_mail_setting_default, get_appropriate_message_part, get_default_contact_reference

logger = logging.getLogger(__name__)

class OrderCancelInfoDefault(OrderInfoDefault):
    def get_shipping_address_info(request, order):
        sa = order.shipping_address
        if sa is None:
            return u"inner"
        params = dict(last_name = sa.last_name, 
                      first_name = sa.first_name, 
                      zip = sa.zip, 
                      prefecture = sa.prefecture, 
                      city = sa.city, 
                      address_1 = sa.address_1, 
                      address_2 = sa.address_2)
        return u"""\
{last_name} {first_name} 様
〒 {zip}
{prefecture} {city}
{address_1} {address_2}""".format(**params)

    ordered_from = SubjectInfo(name=u"ordered_from", label=u"販売会社", getval=lambda request, order: order.ordered_from.name)
    payment_method = SubjectInfo(name=u"payment_method", label=u"支払方法",  getval=lambda request, order: order.payment_delivery_pair.payment_method.name)
    delivery_method = SubjectInfo(name=u"delivery_method", label=u"引取方法",  getval=lambda request, order: order.payment_delivery_pair.delivery_method.name)
    address = SubjectInfo(name="address", label=u"送付先", getval=get_shipping_address_info)
    def get_contact(request, order):
        # XXX: 本来は recipient の情報を含んだ context を SubjectInfoRenderer
        # のコンストラクタが受け取って、それをここまで引き回すべきである
        emails = order.shipping_address.emails if order.shipping_address else None
        recipient = emails[0] if len(emails) > 0 else None
        contact_ref = get_default_contact_reference(request, order.ordered_from, recipient)
        return u"""\
%s
商品、決済・発送に関するお問い合わせ %s""" % (order.ordered_from.name, contact_ref)
    contact = SubjectInfo(name=u"contact", label=u"お問い合わせ", getval=get_contact)

    cancel_reason_default=u"""\
　・期限内のご入金がなくキャンセル扱いとしたため
　・弊社判断によるキャンセル処理を行ったため
"""
    ## getvalが文字列の場合は、input formになり文言を変更できる
    cancel_reason = SubjectInfoWithValue(name="cancel_reason", label=u"キャンセル理由", 
                                       getval=lambda request, order: OrderCancelInfoDefault.cancel_reason_default, value=cancel_reason_default)
    
def get_subject_info_default():
    return OrderCancelInfoDefault()

def get_mailtype_description():
    return u"購入キャンセルメール"

@implementer(IPurchaseInfoMail)    
class CancelMail(object):
    def __init__(self, mail_template):
        self.mail_template = mail_template

    def get_mail_subject(self, request, organization, traverser):
        return (traverser.data["subject"] or 
                u'ご注文キャンセルについて 【{organization}】'.format(organization=organization.name))

    def get_mail_sender(self, request, organization, traverser):
        return (traverser.data["sender"] or organization.setting.default_mail_sender)

    def validate(self, order):
        if not order.shipping_address or not order.shipping_address.email_1:
            logger.info('order has not shipping_address or email id=%s' % order.id)
        return True

    def build_message(self, request, subject, traverser):
        mail_body = self.build_mail_body(request, subject, traverser)
        return self.build_message_from_mail_body(request, subject, traverser, mail_body)

    def build_message_from_mail_body(self, request, order, traverser, mail_body):
        if not self.validate(order):
            logger.warn("validation error")
            return 
        organization = order.ordered_from or request.context.organization
        mail_setting_default = get_mail_setting_default(request)
        subject = self.get_mail_subject(request, organization, traverser)
        sender = mail_setting_default.get_sender(request, traverser, organization)
        bcc = mail_setting_default.get_bcc(request, traverser, organization)
        primary_recipient = order.shipping_address.email_1 if order.shipping_address else None
        return Message(
            subject=subject,
            recipients=[primary_recipient] if primary_recipient else [],
            bcc=bcc,
            body=get_appropriate_message_part(request, primary_recipient, mail_body),
            sender=sender)

    def _body_tmpl_vars(self, request, order, traverser):
        sa = order.shipping_address 
        pair = order.payment_delivery_pair
        info_renderder = SubjectInfoRenderer(request, order, traverser.data, default_impl=OrderCancelInfoDefault)
        title=order.performance.event.title
        value = dict(h=ch, 
                     order=order,
                     title=title, 
                     get=info_renderder.get, 
                     name=u"{0} {1}".format(sa.last_name, sa.first_name) if sa else u"inner", 
                     payment_method_name=pair.payment_method.name, 
                     delivery_method_name=pair.delivery_method.name, 
                     ### mail info
                     footer = traverser.data["footer"],
                     notice = traverser.data["notice"],
                     header = traverser.data["header"],
                     )
        return value

    def build_mail_body(self, request, order, traverser):
        value = self._body_tmpl_vars(request, order, traverser)
        retval = render(self.mail_template, value, request=request)
        assert isinstance(retval, text_type)
        return retval
