# -*- coding:utf-8 -*-
from pyramid_mailer import get_mailer
from .api import get_complete_mail, preview_text_from_message, update_mailinfo
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
    access=lambda d : d[MailStatusEnum.CompleteMail]
)

def build_message(request, order):
    complete_mail = get_complete_mail(request)
    message = complete_mail.build_message(order)
    return message

def send_mail(request, order):
    mailer = get_mailer(request)
    message = build_message(request, order)
    mailer.send(message)
    logger.info("send complete mail to %s" % message.recipients)

def preview_text(request, order):
    message = build_message(request, order)
    return preview_text_from_message(message)

update_mailinfo = update_mailinfo

###
class CompleteMailInfoTemplate(object):
    payment_choices = [("header", u"ヘッダ"), 
                       ("notice", u"注意事項"), 
                       ("footer", u"フッタ"), 
                       ]
    delivery_choices = [("header", u"ヘッダー"), 
                       ("notice", u"注意事項"), 
                       ("footer", u"フッター"), 
                       ]
    common_choices = [
        ("header", u"メールヘッダー"),
        ("notice", u"共通注意事項"), 
        ("footer", u"メールフッター"),
        ]

    def __init__(self, request, organization):
        self.request = request
        self.organization = organization

    def payment_methods_keys(self):
        for payment_method in self.organization.payment_method_list:
            for k, v in self.payment_choices:
                yield k, u"%s(%s)" % (v)

    def delivery_methods_keys(self):
        for delivery_method in self.organization.delivery_method_list:
            for k, v in self.delivery_choices:
                yield k, u"%s(%s)" % (v)

    def common_methods_keys(self):
        return self.common_choices

    def template_keys(self):
        return itertools.chain(
            self.common_methods_keys(), 
            self.payment_methods_keys(), 
            self.delivery_methods_keys())
    

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
                     footer = traverser.data["footer"]
                     )
        return value

    def build_mail_body(self, order):
        value = self._build_mail_body(order)
        return renderers.render(self.mail_template, value, request=self.request)
