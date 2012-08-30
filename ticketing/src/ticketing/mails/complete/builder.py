# -*- coding:utf-8 -*-
import itertools
from pyramid import renderers
from pyramid_mailer.message import Message
from ..interfaces import ICompleteMail
from zope.interface import implementer

from ticketing.cart import helpers as ch ##

class FindStopAccessor(object):
    def __init__(self, wrapper, d):
        self.wrapper = wrapper
        self.d = d

    def __repr__(self):
        return repr(self.d)

    def _get_failback(self, k):
        chained = self.wrapper.chained
        if chained:
            return chained.data[k]

    def __getitem__(self, k):
        if self.d is None:
            return None
        return self.d.get(k) or self._get_failback(k)

    def getall(self, k):
        r = []
        this = self.wrapper
        while this:
            v = this.data.d.get(k)
            if v:
                r.append(v)
            this = this.chained
        return r

class EmailInfoTraverser(object):
    def __init__(self, accessor_impl=FindStopAccessor):
        self.chained = None
        self.target = None
        self._configured = False
        self._accessor_impl = accessor_impl

    def visit(self, target):
        if not self._configured:
            getattr(self, "visit_"+(target.__class__.__name__))(target)
            self._configured = True
        return self

    def _set_data(self, mailinfo):
        self._data = mailinfo
        self.data = self._accessor_impl(self, mailinfo.data if mailinfo else None)

    def visit_Performance(self, performance):
        event = performance.event
        self.target = performance
        self._set_data(performance.extra_mailinfo)

        root = self.__class__(accessor_impl=self._accessor_impl)
        self.chained = root 
        root.visit(event)
        
    def visit_Event(self, event):
        organization = event.organization
        self.target = event
        self._set_data(event.extra_mailinfo)

        root = self.__class__(accessor_impl=self._accessor_impl)
        self.chained = root 
        root.visit(organization)

    def visit_Organization(self, organization):
        self.target = organization
        self._set_data(organization.extra_mailinfo)

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
        organization = order.ordered_from
        sa = order.shipping_address 
        pair = order.payment_delivery_pair
        seats = itertools.chain.from_iterable((p.seats for p in order.ordered_products))

        traverser = EmailInfoTraverser().visit(organization)
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

