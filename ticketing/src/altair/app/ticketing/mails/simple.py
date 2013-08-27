import logging
logger = logging.getLogger(__name__)
from pyramid_mailer.message import Message

from collections import namedtuple
from .api import get_appropriate_message_part

MailData = namedtuple("MailData", "subject sender body recipients")

class SimpleMail(object):
    def __init__(self, request):
        self.request = request

    def build_message(self, sender, subject, body, recipients, bcc=None):
        mail_body = body
        return Message(
            subject=subject,
            recipients=recipients,
            bcc=bcc or [],
            body=get_appropriate_message_part(self.request, recipients[0] if recipients else None, mail_body),
            sender=sender)

