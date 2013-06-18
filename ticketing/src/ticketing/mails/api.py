# -*- coding:utf-8 -*-
import traceback 
from .interfaces import (
    IMailUtility
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

@implementer(IMailUtility)
class MailUtility(object):
    def __init__(self, module, factory):
        self.module = module
        self.factory = factory

    def build_message(self, request, order):
        mail = self.factory(request)
        message = mail.build_message(order)
        return message

    def send_mail(self, request, order, override=None):
        mailer = get_mailer(self, request)
        message = self.build_message(request, order)
        if message is None:
            logger.warn("message is None: %s", traceback.format_stack(limit=3))
        message_settings_override(message, override)
        mailer.send(message)
        logger.info("send complete mail to %s" % message.recipients)

    def preview_text(self, request, order):
        message = self.build_message(request, order)
        return preview_text_from_message(message)

    def __getattr__(self, k, default=None):
        return getattr(self.module, k)

def get_mailinfo_traverser(request, order, access=None, default=None):
    trv = getattr(order, "_mailinfo_traverser", None)
    if trv is None:
        # organization = order.ordered_from
        performance = order.performance
        trv = order._mailinfo_traverser = EmailInfoTraverser(access=access, default=default).visit(performance)
    return trv

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
def create_fake_order(request, organization, payment_plugin_id, delivery_plugin_id, event=None, performance=None):
    ## must not save models 
    now = datetime.now()
    order = FakeObject("T")
    order.ordered_from = organization
    order.created_at = now
    order._mailinfo_traverser = None
    _fake_order_add_settings(order, payment_plugin_id, delivery_plugin_id, event, performance)
    _fake_order_add_fake_chain(order, organization, event, performance)
    return order

def _fake_order_add_fake_chain(fake_order, organization, event, performance):
    if performance:
        return
    elif event:
        fake_order.performance._fake_root = event
    else:
        fake_order.performance._fake_root = organization

def _fake_order_add_settings(order, payment_plugin_id, delivery_plugin_id, event, performance):
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
