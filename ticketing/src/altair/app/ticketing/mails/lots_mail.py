# -*- coding:utf-8 -*-
import logging
from pyramid_mailer.message import Message
from pyramid.compat import text_type
from zope.interface import implementer
from pyramid.renderers import render
from altair.app.ticketing.core import models as c_models
from altair.app.ticketing.payments import plugins
from altair.app.ticketing.lots.helpers import announce_time_label
from altair.app.ticketing.cart import helpers as ch
from .api import create_or_update_mailinfo, get_mail_setting_default, get_appropriate_message_part, create_mail_request
from .forms import SubjectInfoWithValue, SubjectInfo, SubjectInfoDefault
from .forms import SubjectInfoRenderer
from .resources import MailForLotContext
from .interfaces import (
    ICompleteMailResource,
    ILotEntryInfoMail,
    ILotsAcceptedMailResource,
    ILotsElectedMailResource,
    ILotsRejectedMailResource,
    )

logger = logging.getLogger(__name__)

def get_mailtype_description():
    return u"抽選メール"

def get_subject_info_default():
    return LotsInfoDefault()

class LotsInfoDefault(SubjectInfoDefault):
    def get_announce_date(request, lot_entry):
        d = lot_entry.lot.lotting_announce_datetime
        if d:
            return announce_time_label(lot_entry.lot)
        return u"-"

    first_sentence_default = u"""この度は、お申込みいただき、誠にありがとうございました。
抽選申込が完了いたしましたので、ご連絡させていただきます。

抽選結果発表後、抽選結果確認ページにて当選・落選をご確認下さい。
"""
    first_sentence = SubjectInfoWithValue(name="first_sentence", label=u"はじめの文章", value="", getval=(lambda request, _: LotsInfoDefault.first_sentence_default))
    event_name = SubjectInfo(name="event_name", label=u"イベント名", getval=lambda request, lot_entry: lot_entry.lot.event.title)
    lot_name = SubjectInfo(name="lot_name", label=u"受付名称", getval=lambda request, lot_entry: lot_entry.lot.name)
    announce_date = SubjectInfo(name="announce_date", label=u"抽選結果発表日時", getval=get_announce_date)
    review_url = SubjectInfo(name="review_url", label=u"抽選結果確認ページ", getval=lambda request, _ : request.view_context.lots_orderreview_page_url)
    system_fee = SubjectInfo(name=u"system_fee", label=u"システム利用料", getval=lambda request, _: "") #xxx:
    special_fee = SubjectInfo(name=u"special_fee", label=u"特別手数料", getval=lambda request, _: "") #xxx:
    special_fee_name = SubjectInfo(name=u"special_fee_name", label=u"特別手数料名", getval=lambda request, _: "") #xxx:
    transaction_fee = SubjectInfo(name=u"transaction_fee", label=u"決済手数料", getval=lambda request, _: "") #xxx:
    delivery_fee = SubjectInfo(name=u"delivery_fee", label=u"発券／引取手数料", getval=lambda request, _: "") #xxx:
    total_amount = SubjectInfo(name=u"total_amount", label=u"合計金額", getval=lambda request, _: "") #xxx:
    entry_no = SubjectInfo(name="entry_no", label=u"受付番号", getval=lambda request, subject: subject.entry_no)


@implementer(ILotsAcceptedMailResource)
class LotsAcceptedMailResource(MailForLotContext):
    """ 申し込み完了メール """
    mtype = c_models.MailTypeEnum.LotsAcceptedMail

@implementer(ILotsElectedMailResource, ICompleteMailResource)
class LotsElectedMailResource(MailForLotContext):
    """ 当選メール """
    mtype = c_models.MailTypeEnum.LotsElectedMail


@implementer(ILotsRejectedMailResource)
class LotsRejectedMailResource(MailForLotContext):
    """ 落選メール """
    mtype = c_models.MailTypeEnum.LotsRejectedMail


@implementer(ILotEntryInfoMail)
class LotsMail(object):
    def __init__(self, mail_template):
        self.mail_template = mail_template

    def get_mail_subject(self, request, organization, traverser):
        raise NotImplementedError

    def validate(self, lot_entry):
        if not lot_entry.shipping_address or not lot_entry.shipping_address.email_1:
            logger.info('lot_entry has not shipping_address or email id=%s' % lot_entry.id)
        return True

    def build_message_from_mail_body(self, request, (lot_entry, elected_wish), traverser, mail_body):
        if not self.validate(lot_entry):
            logger.warn("validation error")
            return

        organization = lot_entry.lot.event.organization or request.context.organization
        mail_setting_default = get_mail_setting_default(request)
        subject = self.get_mail_subject(request, organization, traverser)
        sender = mail_setting_default.get_sender(request, traverser, organization)
        bcc = mail_setting_default.get_bcc(request, traverser, organization)
        mail_body = mail_body
        return Message(
            subject=subject,
            recipients=[lot_entry.shipping_address.email_1],
            bcc=bcc,
            body=get_appropriate_message_part(request, lot_entry.shipping_address.email_1, mail_body),
            sender=sender)

    def build_message(self, request, subject, traverser):
        mail_body = self.build_mail_body(request, subject, traverser)
        return self.build_message_from_mail_body(request, subject, traverser, mail_body)

    def _body_tmpl_vars(self, request, (lot_entry, elected_wish), traverser):
        shipping_address = lot_entry.shipping_address
        pair = lot_entry.payment_delivery_method_pair
        info_renderder = SubjectInfoRenderer(request, lot_entry, traverser.data, default_impl=get_subject_info_default())
        value = dict(h=ch,
                     fee_type=ch.fee_type,
                     plugins=plugins,
                     lot_entry=lot_entry,
                     extra_form_data=lot_entry.get_lot_entry_attribute_pair_pairs(request),
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

    def build_mail_body(self, request, subject, traverser):
        organization = subject[0].organization
        mail_request = create_mail_request(request, organization, self.build_context_factory(subject))
        value = self._body_tmpl_vars(mail_request, subject, traverser)
        retval = render(self.mail_template, value, request=mail_request)
        assert isinstance(retval, text_type)
        return retval


class LotsAcceptedMail(LotsMail):
    def get_mail_subject(self, request, organization, traverser):
        return (traverser.data["subject"] or
                u'抽選申込受付完了のお知らせ 【{organization}】'.format(organization=organization.name))

    def build_context_factory(self, subject):
        return lambda request: LotsAcceptedMailResource(request, subject)

class LotsElectedMail(LotsMail):
    def get_mail_subject(self, request, organization, traverser):
        return (traverser.data["subject"] or
                u'抽選当選のお知らせ 【{organization}】'.format(organization=organization.name))

    def build_context_factory(self, subject):
        return lambda request: LotsElectedMailResource(request, subject)

class LotsRejectedMail(LotsMail):
    def get_mail_subject(self, request, organization, traverser):
        return (traverser.data["subject"] or
                u'抽選予約結果のお知らせ 【{organization}】'.format(organization=organization.name))

    def build_message_from_mail_body(self, request, subject, traverser, mail_body):
        message = super(LotsRejectedMail, self).build_message_from_mail_body(request, subject, traverser, mail_body)
        # 落選メールはbccしない
        message.bcc = []
        logger.info('send rejected mail ({recipients})'.format(recipients=message.recipients))
        return message

    def build_context_factory(self, subject):
        return lambda request: LotsRejectedMailResource(request, subject)
