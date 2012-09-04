# -*- coding:utf-8 -*-
from .interfaces import (
    ICompleteMail, 
    IMailUtility
)
from .fake import FakeObject
from .traverser import EmailInfoTraverser
from pyramid.interfaces import IRequest
import logging
from ticketing.core.models import ExtraMailInfo, PaymentMethodPlugin, DeliveryMethodPlugin

logger = logging.getLogger(__name__)
def get_mail_utility(request, mailtype):
    return request.registry.getUtility(IMailUtility, str(mailtype))

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

def get_complete_mail(request):
    cls = request.registry.adapters.lookup([IRequest], ICompleteMail, "")
    return cls(request)

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
    order = FakeObject("T")
    order.ordered_from = organization
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
    payment_plugin = PaymentMethodPlugin.query.filter_by(id=payment_plugin_id).first()
    if payment_plugin:
        order.payment_delivery_pair.payment_method.payment_plugin = payment_plugin
    else:
        order.payment_delivery_pair.payment_method.payment_plugin_id = payment_plugin_id
    delivery_plugin = DeliveryMethodPlugin.query.filter_by(id=delivery_plugin_id).first()
    if delivery_plugin:
        order.payment_delivery_pair.delivery_method.delivery_plugin = delivery_plugin
    else:
        order.payment_delivery_pair.delivery_method.delivery_plugin_id = delivery_plugin_id
    if event:
        order.performance.event = event
    if performance:
        order.performance = performance
