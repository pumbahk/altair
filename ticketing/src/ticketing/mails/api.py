# -*- coding:utf-8 -*-
import sys
import traceback 
from .interfaces import (
    IMailUtility, 
    ITraverserFactory, 
    IMailSettingDefault
)
from datetime import datetime
from .fake import FakeObject
from .traverser import EmailInfoTraverser
import logging
from zope.interface import implementer
from ticketing.core.models import ExtraMailInfo, PaymentMethodPlugin, DeliveryMethodPlugin
from pyramid_mailer import get_mailer
logger = logging.getLogger(__name__)

def get_mail_utility(request, mailtype):
    return request.registry.getUtility(IMailUtility, str(mailtype))

def get_cached_traverser(request, mtype, subject):
    trv = getattr(subject, "_cached_mail_traverser", None)
    if trv is None:
        factory = request.registry.getUtility(ITraverserFactory, name=mtype)
        trv = subject._cached_mail_traverser = factory(subject)
    return trv

def get_mail_setting_default(request, name=""):
    return request.registry.getUtility(IMailSettingDefault, name=name)

@implementer(IMailSettingDefault)
class MailSettingDefaultGetter(object):
    def __init__(self, show_flash_message=False):
        self.show_flash_message = show_flash_message

    def _notify_bcc(self, request, bcc):
        textmessage = "ticketing.mails.bcc.silent = true, bcc = []. (bcc data --- {0})".format(bcc)
        if self.show_flash_message:
            request.session.flash(textmessage)
        logger.info(textmessage)

    def get_bcc(self, request, traverser, organization):
        val = traverser.data and traverser.data["bcc"]
        bcc_recipients = []
        if val:
            if val["use"] and val["value"]:
                bcc_recipients.extend(y for y in [x.strip() for x in val["value"].split("\n")] if y)
        if organization.setting.bcc_recipient is not None:
            bcc_recipients.append(organization.setting.bcc_recipient)
        self._notify_bcc(request, bcc_recipients)
        return bcc_recipients

    def get_sender(self, request, traverser, organization):
        return (traverser.data["sender"] or organization.contact_email)

class ExtraMailInfoAccessor(object):
    def __init__(self, mtype, default):
        self.mtype = mtype
        self.default = default

    def __call__(self, data, k, default=None):
        try:
            return data[self.mtype][k]
        except KeyError:
            return default or self.default

    def touch(self, data):
        try:
            return data[self.mtype]
        except KeyError:
            return False

@implementer(ITraverserFactory)
class MailTraverserFromOrder(object):
    def __init__(self, mtype, default=""):
        self.mtype = mtype
        self.default = default
        self.access = ExtraMailInfoAccessor(mtype=mtype, default=default)

    def __call__(self, order):
        performance = order.performance
        return EmailInfoTraverser(access=self.access, default=self.default).visit(performance)

@implementer(ITraverserFactory)
class MailTraverserFromLotsEntry(object):
    def __init__(self, mtype, default=""):
        self.mtype = mtype
        self.default = default
        self.access = ExtraMailInfoAccessor(mtype=mtype, default=default)

    def __call__(self, lots_entry):
        event = lots_entry.lot.event
        return EmailInfoTraverser(access=self.access, default=self.default).visit(event)

@implementer(IMailUtility)
class MailUtility(object):
    def __init__(self, module, mtype, factory):
        self.module = module
        self.factory = factory
        self.mtype = mtype

    def get_traverser(self, request, subject):
        if isinstance(subject, (list, tuple)):
            return get_cached_traverser(request, self.mtype, subject[0])
        return get_cached_traverser(request, self.mtype, subject)

    def build_message(self, request, subject):
        mail = self.factory(request)
        traverser = self.get_traverser(request, subject)
        message = mail.build_message(subject, traverser)
        return message

    def send_mail(self, request, subject, override=None):
        message = self.build_message(request, subject)
        if message is None:
            raise Exception("mail message is None")
        message_settings_override(message, override)

        message.recipients = [x for x in message.recipients if x]
        if not message.recipients:
            logger.warn("recipients is not found. skip.")
            return message

        mailer = get_mailer(request)
        mailer.send(message)
        logger.info("send complete mail to %s" % message.recipients)
        return message

    def preview_text(self, request, subject, limit=100):
        mail = self.factory(request)
        traverser = self.get_traverser(request, subject)
        try:
            mail_body = mail.build_mail_body(subject, traverser)
        except:
            etype, value, tb = sys.exc_info()
            mail_body = u''.join(s.decode("utf-8", errors="replace") for s in traceback.format_exception(etype, value, tb, limit))

        message = mail.build_message_from_mail_body(subject, traverser, mail_body)
        return preview_text_from_message(message)

    def __getattr__(self, k, default=None):
        return getattr(self.module, k)

def create_mailinfo(target, data, organization, event, performance, kind):
    if kind:
        data = {kind: data}
    target.extra_mailinfo = ExtraMailInfo(data=data)
    if target == performance:
        target.performance = performance
    elif target == event:
        target.event = event
    elif target == organization:
        target.organization = organization
    return target.extra_mailinfo

def update_mailinfo(target, data, kind=None):
    if kind:
        if not kind in target.extra_mailinfo.data:
            target.extra_mailinfo.data[kind] = {}
        target.extra_mailinfo.data[kind].update(data)
    else:
        target.extra_mailinfo.data.update(data)
    target.extra_mailinfo.data.changed()
    return target.extra_mailinfo

def create_or_update_mailinfo(request, data, organization=None, event=None, performance=None, kind=None):
    target = performance or event or organization
    assert target
    if target.extra_mailinfo is None:
        return create_mailinfo(target, data, organization, event, performance, kind)
    else:
        return update_mailinfo(target, data, kind)

def preview_text_from_message(message):
    params = dict(subject=message.subject, 
                  recipients=message.recipients, 
                  bcc=message.bcc, 
                  sender=message.sender, 
                  body=message.body)
    return u"""\
subject: %(subject)s
recipients: %(recipients)s
bcc: %(bcc)s
sender: %(sender)s
-------------------------------

%(body)s
""" % params

def dump_mailinfo(mailinfo, limit=50):
    for k, v in mailinfo.data.iteritems():
        print k, v if len(v) <= limit else v[:limit]

def message_settings_override(message, override):
    if override:
        if "recipient" in override:
            message.recipients = [override["recipient"]]
        if "subject" in override:
            message.sender = override["subject"]
        if "bcc" in override:
            bcc = override["bcc"]
            message.sender = bcc if hasattr(bcc, "length") else [bcc]
    return message


## fake
### TODO:refactroing
def create_fake_order(request, organization, payment_plugin_id, delivery_plugin_id, event=None, performance=None):
    ## must not save models 
    now = datetime.now()
    order = FakeObject("T")
    order.ordered_from = organization
    order.created_at = now
    order._cached_mail_traverser = None

    if event:
        order.performance._fake_root = event
    else:
        order.performance._fake_root = organization

    order.payment_delivery_pair.payment_method.payment_plugin_id = payment_plugin_id
    payment_plugin = PaymentMethodPlugin.query.filter_by(id=payment_plugin_id).first()
    if payment_plugin:
        order.payment_delivery_pair.payment_method.payment_plugin = payment_plugin
        order.payment_delivery_pair.payment_method.name = payment_plugin.name

    order.payment_delivery_pair.delivery_method.delivery_plugin_id = delivery_plugin_id
    delivery_plugin = DeliveryMethodPlugin.query.filter_by(id=delivery_plugin_id).first()
    if delivery_plugin:
        order.payment_delivery_pair.delivery_method.delivery_plugin = delivery_plugin
        order.payment_delivery_pair.delivery_method.name = delivery_plugin.name

    if event:
        order.performance.event = event
    if performance:
        order.performance = performance
    return order

def create_fake_lot_entry(request, organization, payment_plugin_id, delivery_plugin_id, event=None, performance=None):
    ## must not save models 
    now = datetime.now()
    lot_entry = FakeObject("T")
    lot_entry.lot_entryed_from = organization
    lot_entry.created_at = now
    lot_entry._cached_mail_traverser = None

    if performance:
        pass
    elif event:
        pass
    else:
        lot_entry.lot.event._fake_root = organization #lot_entry

    lot_entry.payment_delivery_pair.payment_method.payment_plugin_id = payment_plugin_id
    payment_plugin = PaymentMethodPlugin.query.filter_by(id=payment_plugin_id).first()
    if payment_plugin:
        lot_entry.payment_delivery_method_pair.payment_method.payment_plugin = payment_plugin #l
        lot_entry.payment_delivery_method_pair.payment_method.name = payment_plugin.name #l

    lot_entry.payment_delivery_pair.delivery_method.delivery_plugin_id = delivery_plugin_id
    delivery_plugin = DeliveryMethodPlugin.query.filter_by(id=delivery_plugin_id).first()
    if delivery_plugin:
        lot_entry.payment_delivery_method_pair.delivery_method.delivery_plugin = delivery_plugin
        lot_entry.payment_delivery_method_pair.delivery_method.name = delivery_plugin.name

    if event:
        lot_entry.lot.event = event #lot_entry
    if performance:
        lot_entry.lot.event = performance.event #lot_entry
    return lot_entry

def create_fake_elected_wish(request, performance=None):
    ## must not save models 
    elected_wish = FakeObject("ElectedWish")
    if performance:
        elected_wish.performance = performance
    return elected_wish
