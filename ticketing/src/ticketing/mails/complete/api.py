from pyramid_mailer import get_mailer
from ..api import get_complete_mail, preview_text_from_message, update_mailinfo
import logging
logger = logging.getLogger(__name__)

def build_message(request, order):
    complete_mail = get_complete_mail(request)
    message = complete_mail.build_message(order)
    return message

def send_mail(request, order):
    mailer = get_mailer(request)
    message = build_message(request, order)
    mailer.send(message)
    logger.info("send complete mail to %s" % message.recipients)

def preview_text(request, order):
    message = build_message(request, order)
    return preview_text_from_message(message)

update_mailinfo = update_mailinfo
