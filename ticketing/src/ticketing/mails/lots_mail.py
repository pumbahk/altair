# -*- coding:utf-8 -*-
from ticketing.payments import plugins
from pyramid_mailer.message import Message
from .renderers import render
from .api import create_or_update_mailinfo,  create_fake_order as _create_fake_order
from .forms import SubjectInfoWithValue, SubjectInfo, SubjectInfoDefault
from .forms import SubjectInfoRenderer
import logging
from ticketing.cart import helpers as ch
from .fake import FakeObject
logger = logging.getLogger(__name__)

def create_fake_order(request, organization, payment_plugin_id, delivery_plugin_id, event=None, performance=None):
    lot_entry = _create_fake_order(request, organization, payment_plugin_id, delivery_plugin_id, event=event, performance=performance)
    elected_wish = FakeObject.create(name="elected_wish")
    return lot_entry, elected_wish

def get_mailtype_description():
    return u"抽選メール"

def get_subject_info_default():
    return LotsInfoDefault()

class LotsInfoDefault(SubjectInfoDefault):
    def get_announce_date(lot_entry):
        d = lot_entry.lot.lotting_announce_datetime
        return u"{d.year}年{d.month:02}月{d.day:02}日 {d.hour:02}:{d.minute:02}～".format(d=d) if d else u"-"

    first_sentence_default = u"""この度は、お申込みいただき、誠にありがとうございました。
抽選申込が完了いたしましたので、ご連絡させていただきます。

抽選結果発表日時以降、抽選結果確認ページにて当選・落選をご確認下さい。
"""

    first_sentence = SubjectInfoWithValue(name="first_sentence", label=u"はじめの文章", getval=(lambda _: LotsInfoDefault.first_sentence_default),  value=first_sentence_default)
    event_name = SubjectInfo(name="event_name", label=u"イベント名", getval=lambda lot_entry: lot_entry.lot.event.title)
    lot_name = SubjectInfo(name="lot_name", label=u"受付名称", getval=lambda lot_entry: lot_entry.lot.name)
    announce_date = SubjectInfo(name="announce_date", label=u"抽選結果発表日時", getval=get_announce_date)
    review_url = SubjectInfo(name="review_url", label=u"抽選結果確認ページ", getval=lambda _ : "https://rt.tstar.jp/lots/review")

    system_fee = SubjectInfo(name=u"system_fee", label=u"システム利用料", getval=lambda _: "") #xxx:
    transaction_fee = SubjectInfo(name=u"transaction_fee", label=u"決済手数料", getval=lambda _: "") #xxx:
    delivery_fee = SubjectInfo(name=u"delivery_fee", label=u"発券／引取手数料", getval=lambda _: "") #xxx:
    total_amount = SubjectInfo(name=u"total_amount", label=u"合計金額", getval=lambda _: "") #xxx:
    entry_no = SubjectInfo(name="entry_no", label=u"受付番号", getval=lambda subject : subject.entry_no)

class LotsMail(object):
    def __init__(self, mail_template, request):
        self.mail_template = mail_template
        self.request = request

    def get_mail_subject(self, organization, traverser):
        raise NotImplementedError

    def get_mail_sender(self, organization, traverser):
        return (traverser.data["sender"] or organization.contact_email)

    def validate(self, lot_entry):
        if not lot_entry.shipping_address or not lot_entry.shipping_address.email_1:
            logger.info('lot_entry has not shipping_address or email id=%s' % lot_entry.id)
        return True

    def build_message(self, (lot_entry, elected_wish), traverser):
        if not self.validate(lot_entry):
            logger.warn("validation error")
            return 

        organization = lot_entry.lot.event.organization or self.request.context.organization
        subject = self.get_mail_subject(organization, traverser)
        mail_from = self.get_mail_sender(organization, traverser)
        bcc = [mail_from]

        mail_body = self.build_mail_body((lot_entry, elected_wish), traverser)
        return Message(
            subject=subject,
            recipients=[lot_entry.shipping_address.email_1],
            bcc=bcc,
            body=mail_body,
            sender=mail_from)


    def _body_tmpl_vars(self, (lot_entry, elected_wish), traverser):
        shipping_address = lot_entry.shipping_address 
        pair = lot_entry.payment_delivery_pair
        info_renderder = SubjectInfoRenderer(lot_entry, traverser.data, default_impl=get_subject_info_default())
        value = dict(h=ch, 
                     fee_type=ch.fee_type, 
                     plugins=plugins, 
                     lot_entry=lot_entry,
                     shipping_address=shipping_address,
                     get=info_renderder.get, 
                     name=u"{0} {1}".format(shipping_address.last_name, shipping_address.first_name),
                     payment_method_name=pair.payment_method.name, 
                     delivery_method_name=pair.delivery_method.name, 
                     elected_wish=elected_wish, 
                     ### mail info
                     footer = traverser.data["footer"],
                     notice = traverser.data["notice"],
                     header = traverser.data["header"],
                     )
        return value

    def build_mail_body(self, subject, traverser):
        value = self._body_tmpl_vars(subject, traverser)
        return render(self.mail_template, value, request=self.request)


class LotsAcceptedMail(LotsMail):
    def get_mail_subject(self, organization, traverser):
        return (traverser.data["subject"] or 
                u'抽選申込受付完了のお知らせ 【{organization}】'.format(organization=organization.name))

class LotsElectedMail(LotsMail):
    def get_mail_subject(self, organization, traverser):
        return (traverser.data["subject"] or 
                u'抽選当選のお知らせ 【{organization}】'.format(organization=organization.name))

class LotsRejectedMail(LotsMail):
    def get_mail_subject(self, organization, traverser):
        return (traverser.data["subject"] or 
                u'抽選予約結果のお知らせ 【{organization}】'.format(organization=organization.name))


