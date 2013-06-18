# -*- coding:utf-8 -*-
from ticketing.mails.api import get_mail_utility
from ticketing.core.models import MailTypeEnum
from pyramid_mailer import get_mailer
import logging

logger = logging.getLogger(__name__)

Cancel = MailTypeEnum.PurchaseCancelMail
def on_order_canceled(event):
    message = get_mail_utility(event.request, Cancel).build_message(event.request, event.order)
    if message:
        mailer = get_mailer(event.request)
        mailer.send(message)
        logger.info('send cancel mail to %s' % message.recipients)
