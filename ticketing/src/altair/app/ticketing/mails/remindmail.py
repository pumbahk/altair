# -*- coding:utf-8 -*-
from zope.interface import implementer
from pyramid.renderers import render
from pyramid_mailer.message import Message
from pyramid.compat import text_type
from altair.viewhelpers import DefaultDateTimeFormatter
from altair.app.ticketing.cart import helpers as ch ##


from .interfaces import IRemindMail
from .forms import SubjectInfoRenderer
from .forms import OrderInfoDefault, SubjectInfo, SubjectInfoWithValue
from .api import (
    get_mail_setting_default,
    get_default_contact_reference,
    )

class RemindInfoDefault(OrderInfoDefault):
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
        emails = order.shipping_address.emails if order.shipping_address else []
        recipient = emails[0] if len(emails) > 0 else None
        contact_ref = get_default_contact_reference(request, order.ordered_from, recipient)
        return u"""\
%s
商品、決済・発送に関するお問い合わせ %s""" % (order.ordered_from.name, contact_ref)
    contact = SubjectInfo(name=u"contact", label=u"お問い合わせ", getval=get_contact)


@implementer(IRemindMail)
class SejRemindMail(object):
    def __init__(self, mail_template):
        self.mail_template = mail_template

    def get_mail_subject(self, request, organization, traverser):
        return (traverser.data["subject"] or
                u'<<重要>> 支払期限についてのご案内【{organization}】'.format(organization=organization.name))

    def build_mail_body(self, request, something, traverser):
        value = self._body_tmpl_vars(request, something, traverser)
        retval = render(self.mail_template, value, request=request)
        assert isinstance(retval, text_type)
        return retval

    def _body_tmpl_vars(self, request, order, traverser):
        sa = order.shipping_address
        pair = order.payment_delivery_pair
        info_renderder = SubjectInfoRenderer(request, order, traverser.data, default_impl=RemindInfoDefault)
        title=order.performance.event.title
        payment_due_at = DefaultDateTimeFormatter().format_datetime(order.sej_order.payment_due_at, with_weekday=True)
        value = dict(h=ch,
                     payment_du_at=payment_due_at,
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


    def build_message_from_mail_body(self, request, order, traverser, mail_body):
        organization = order.organization or request.context.organization
        mail_setting_default = get_mail_setting_default(request)
        subject = self.get_mail_subject(request, organization, traverser)
        bcc = mail_setting_default.get_bcc(request, traverser, organization)
        sender = mail_setting_default.get_sender(request, traverser, organization)
        primary_recipient = order.shipping_address.email_1 if order.shipping_address else None

        msg = Message(subject=subject, recipients=[primary_recipient],
                      bcc=bcc, body=mail_body, sender=sender)
        return msg

    def build_message(self, request, something, traverser):
        mail_body = self.build_mail_body(request, something, traverser)
        return self.build_message_from_mail_body(request, something, traverser, mail_body)
