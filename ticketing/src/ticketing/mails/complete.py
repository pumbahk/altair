# -*- coding:utf-8 -*-
from pyramid_mailer import get_mailer
from .api import get_complete_mail, preview_text_from_message, update_mailinfo, message_settings_override
import logging
logger = logging.getLogger(__name__)

import itertools
from pyramid import renderers
from pyramid_mailer.message import Message
from .interfaces import ICompleteMail
from .api import get_mailinfo_traverser
from zope.interface import implementer

from ticketing.cart import helpers as ch ##
from ticketing.core.models import MailStatusEnum
import functools

complete_mailinfo_traverser = functools.partial(
    get_mailinfo_traverser, 
    access=lambda d, k, default="" : d[MailStatusEnum.CompleteMail].get(k, default), 
    default=u"", 
)

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

update_mailinfo = update_mailinfo

###
from wtforms import Form
from wtforms import fields
from wtforms import widgets
from collections import namedtuple

def MailInfoFormFactory(template):
    attrs = {}
    for name, label in template.template_keys():
        attrs["payment_methods"] = fields.SelectField(label=u"決済方法", choices=template.payment_methods_keys())
        attrs["delivery_methods"] = fields.SelectField(label=u"配送方法", choices=template.delivery_methods_keys())
        attrs[name] = fields.TextField(label=label, widget=widgets.TextArea())
    return type("MailInfoForm", (Form, ), attrs)
    
class CompleteMailInfoTemplate(object):
    """
    data = {
      "header": u"ヘッダー", 
      "P0header": u"payment_plugin (0)header"
      "P1header": u"payment_plugin (1)header", 
      "D0header": u"deliveery_plugin (0)header"
      "D1header": u"deliveery_plugin (1)header", 
    }
    """
    def as_form(self):
        return MailInfoFormFactory(self)()

    payment_choices = [#("header", u"ヘッダ"), 
                       ("notice", u"注意事項"), 
                       #("footer", u"フッタ"), 
                       ]
    delivery_choices = [#("header", u"ヘッダー"), 
                       ("notice", u"注意事項"), 
                       #("footer", u"フッター"), 
                       ]
    common_choices = [
        ("header", u"メールヘッダー"),
        ("notice", u"共通注意事項"), 
        ("footer", u"メールフッター"),
        ]

    def __init__(self, request, organization):
        self.request = request
        self.organization = organization

    payment_key_fmt = "P%d%s"
    delivery_key_fmt = "D%d%s"

    @classmethod
    def payment_key(self, order, k):
        self.payment_key_fmt % (order.payment_plugin_id, k)

    @classmethod
    def delivery_key(self, order, k):
        self.delivery_key_fmt % (order.delivery_plugin_id, k)

    def payment_methods_keys(self, payment_id):
        candidates = self.organization.payment_method_list
        if payment_id:
            candidates = (m for m in candidates if m.payment_plugin_id==payment_id) #xxx:
        for payment_method in candidates:
            plugin_id = payment_method.payment_plugin_id
            plugin_name = payment_method.payment_plugin.name
            for k, v in self.payment_choices:
                yield self.payment_key_fmt % (plugin_id, k), u"%s(%s)" % (v, plugin_name)
        
    def delivery_methods_keys(self, delivery_id):
        candidates = self.organization.delivery_method_list
        if delivery_id:
            candidates = (m for m in candidates if m.delivery_plugin_id==delivery_id) #xxx:
        for delivery_method in candidates:
            plugin_id = delivery_method.delivery_plugin_id
            plugin_name = delivery_method.delivery_plugin.name
            for k, v in self.delivery_choices:
                yield self.delivery_key_fmt % (plugin_id, k), u"%s(%s)" % (v, plugin_name)

    def common_methods_keys(self):
        return self.common_choices

    def template_keys(self, payment_plugin_id=None, delivery_plugin_id=None):
        return itertools.chain(
            self.common_methods_keys(), 
            self.payment_methods_keys(payment_plugin_id), 
            self.delivery_methods_keys(delivery_plugin_id))
    

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
