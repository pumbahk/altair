import functools
from pyramid_mailer import get_mailer
import logging
logger = logging.getLogger(__name__)
from pyramid_mailer.message import Message
from . import PURCHASE_MAILS
from .api import get_purchaseinfo_mail
from .api import preview_text_from_message

from collections import namedtuple
get_simple_mail = functools.partial(get_purchaseinfo_mail, name=PURCHASE_MAILS["simple"])

MailData = namedtuple("MailData", "subject sender body recipients")

def build_message(request, data, bcc=None):
    simple_mail = get_simple_mail(request)
    message = simple_mail.build_message(data.sender, data.subject, data.body, data.recipients, bcc=bcc)
    return message

def send_mail(request, data, override=None):
    mailer = get_mailer(request)
    message = build_message(request, data)
    mailer.send(message)
    logger.info("send simple mail to %s" % message.recipients)

def preview_text(request, data):
    message = build_message(request, data)
    return preview_text_from_message(message)

class SimpleMail(object):
    def __init__(self, request):
        self.request = request

    def build_message(self, sender, subject, body, recipients, bcc=None):
        mail_body = body
        return Message(
            subject=subject,
            recipients=recipients,
            bcc=bcc or [],
            body=mail_body,
            sender=sender)

