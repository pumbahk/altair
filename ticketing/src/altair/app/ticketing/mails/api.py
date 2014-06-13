# -*- coding:utf-8 -*-
import sys
import traceback
import logging
import cgi
import re
import unicodedata
from urlparse import urlparse
from datetime import datetime

from zope.interface import implementer, directlyProvides

from pyramid_mailer import get_mailer
from pyramid_mailer.message import Attachment

from altair.mobile.api import detect_from_email_address
from altair.mobile import carriers

from altair.app.ticketing.core.models import ExtraMailInfo
from altair.app.ticketing.core.api import get_default_contact_url

from .interfaces import (
    IMailUtility,
    ITraverserFactory,
    IMailSettingDefault,
    IMessagePartFactory,
    IFakeObjectFactory,
)
from .fake import FakeObject
from .fake import create_fake_order as _create_fake_order
from .traverser import EmailInfoTraverser

logger = logging.getLogger(__name__)

def get_mail_utility(request, mailtype):
    return request.registry.getUtility(IMailUtility, str(mailtype))

def get_cached_traverser(request, mtype, subject):
    trv = getattr(subject, "_cached_mail_traverser", None)
    if trv is None or not ITraverserFactory.providedBy(trv):
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
        textmessage = "bcc recipients => {0}".format(bcc)
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
        return (traverser.data["sender"] or organization.setting.default_mail_sender)

class ExtraMailInfoAccessor(object):
    def __init__(self, mtype, default):
        self.mtype = mtype
        self.default = default

    def __call__(self, data, k, default=None):
        try:
            result = data[self.mtype][k]
            ## this is not good. ad-hoc reply for collecting data from chaining candidates.
            ## {"use": True, "value": ""}. this value is found as falsy value(but bool(this) is True).
            if result and isinstance(result, basestring):
                return result
            elif result and not "value" in result:
                return result
            elif result and result.get("value"):
                return result
            else:
                return self.default
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

@implementer(ITraverserFactory)
class MailTraverserFromPointGrantHistoryEntry(object):
    def __init__(self, mtype, default=""):
        self.order_mail_traverser = MailTraverserFromOrder(mtype, default)

    @property
    def mtype(self):
        return self.order_mail_traverser.mtype

    @property
    def default(self):
        return self.order_mail_traverser.default

    @property
    def access(self):
        return self.order_mail_traverser.access

    def __call__(self, point_grant_history_entry):
        return self.order_mail_traverser(point_grant_history_entry.order)

@implementer(IMailUtility)
class MailUtility(object):
    def __init__(self, module, mtype, builder):
        self.module = module
        self.mtype = mtype
        self.builder = builder

    def get_mailtype_description(self):
        return self.module.get_mailtype_description()

    def get_subject_info_default(self):
        return self.module.get_subject_info_default()

    def create_or_update_mailinfo(self, request, data, organization=None, event=None, performance=None, kind=None):
        return self.module.create_or_update_mailinfo(request, data, organization, event, performance, kind)

    def create_fake_object(self, request, **kwargs):
        return request.registry.queryAdapter(self.builder, IFakeObjectFactory)(request, kwargs)

    def get_traverser(self, request, subject):
        if isinstance(subject, (list, tuple)):
            return get_cached_traverser(request, self.mtype, subject[0])
        return get_cached_traverser(request, self.mtype, subject)

    def build_message(self, request, subject):
        traverser = self.get_traverser(request, subject)
        message = self.builder.build_message(request, subject, traverser)
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
        traverser = self.get_traverser(request, subject)
        try:
            mail_body = self.builder.build_mail_body(request, subject, traverser)
        except:
            etype, value, tb = sys.exc_info()
            mail_body = u''.join(s.decode("utf-8", errors="replace") for s in traceback.format_exception(etype, value, tb, limit))

        message = self.builder.build_message_from_mail_body(request, subject, traverser, mail_body)
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

def stringize_message_body(body):
    if isinstance(body, Attachment):
        ct, ctparams = cgi.parse_header(body.content_type)
        charset = ctparams.get('charset', 'utf-8' if body.transfer_encoding == '8bit' else 'us-ascii')
        return body.data.decode(charset)
    else:
        return body

def preview_text_from_message(message):
    params = dict(subject=message.subject,
                  recipients=message.recipients,
                  bcc=message.bcc,
                  sender=message.sender,
                  body=stringize_message_body(message.body))
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
            message.subject = override["subject"]
        if "bcc" in override:
            bcc = override["bcc"]
            message.bcc = bcc if hasattr(bcc, "length") else [bcc]
    return message


def create_fake_order(request, organization, payment_method_id, delivery_method_id, event=None, performance=None):
    args = {
        "organization": organization,
        "payment_method_id": payment_method_id,
        "delivery_method_id": delivery_method_id,
        "event": event,
        "performance": performance,
        }
    return _create_fake_order(request, args)

@implementer(IMessagePartFactory)
class MessagePartFactory(object):
    def __init__(self, content_type, charset, encoding, encode_errors, filters, transfer_encoding):
        self.transfer_encoding = transfer_encoding or 'base64'

        _content_type, ctparams = cgi.parse_header(content_type)
        _charset = ctparams.get('charset')
        if charset is None:
            if _charset is not None:
                charset = _charset
            else:
                charset = 'utf-8' # XXX: hard-coded default

        ctparams['charset'] = charset

        if encoding is None:
            encoding = charset

        combined_content_type = _content_type + "".join("; %s=%s" % (key, re.sub(r'[\\"]', lambda g: "\\" + g.group(0), value)) for key, value in ctparams.items())

        self.content_type = combined_content_type
        self.encoding = encoding
        self.encode_errors = encode_errors
        self.filters = filters

    def __call__(self, request, text_body):
        if isinstance(text_body, unicode):
            for filter_ in self.filters:
                text_body = filter_(text_body)
            body = text_body.encode(self.encoding, self.encode_errors)
        return Attachment(
            data=body,
            content_type=self.content_type,
            transfer_encoding=self.transfer_encoding,
            disposition="inline"
            )

def is_nonmobile_recipient(request, email_address):
    carrier = detect_from_email_address(request.registry, email_address)
    return carrier.is_nonmobile

def get_message_part_factory(request, name):
    return request.registry.getUtility(IMessagePartFactory, name)

def get_appropriate_message_part_factory(request, primary_recipient, kind='plain'):
    if (not primary_recipient) or is_nonmobile_recipient(request, primary_recipient):
        type_ = 'nonmobile'
    else:
        type_ = 'mobile'
    return get_message_part_factory(request, '%s.%s' % (type_, kind))

def get_appropriate_message_part(request, primary_recipient, mail_body, kind='plain'):
    return get_appropriate_message_part_factory(request, primary_recipient, kind)(request, mail_body)

def get_default_contact_reference(request, organization, recipient):
    try:
        carrier = detect_from_email_address(request.registry, recipient)
    except ValueError:
        # デフォルトは non-mobile とする
        carrier = carriers.NonMobile
    contact_url = get_default_contact_url(request, organization, carrier)
    # 問い合わせ先が全く指定されていない場合は空文字を返す、でよいだろう
    if contact_url is None:
        return u''
    # mailto: で始まる場合は unquote して <%s> に変更する
    # mailto:a@example.com?body=xxx のようになっている場合は query を取り除く
    if contact_url.startswith(u'mailto:'):
        parsed_url = urlparse(contact_url)
        return u'<%s>' % parsed_url.path
    else:
        # その他の場合は URL そのまま
        return contact_url
