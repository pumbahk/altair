from .interfaces import ICompleteMail
from .traverser import EmailInfoTraverser
from pyramid.interfaces import IRequest
import logging
from ticketing.core.models import ExtraMailInfo

logger = logging.getLogger(__name__)
def get_mailinfo_traverser(request, order, access=None, default=None):
    trv = getattr(order, "_mailinfo_traverser", None)
    if trv is None:
        organization = order.ordered_from
        trv = order._mailinfo_traverser = EmailInfoTraverser(access=access, default=default).visit(organization)
    return trv

def create_mailinfo(target, data, organization, event, kind):
    if kind:
        data = {kind: data}
    target.extra_mailinfo = ExtraMailInfo(data=data)
    if target == event:
        target.event = event
    if target == organization:
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

def create_or_update_mailinfo(request, data, organization=None, event=None, kind=None):
    target = event or organization
    assert target
    if target.extra_mailinfo is None:
        return create_mailinfo(target, data, organization, event, kind)
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
