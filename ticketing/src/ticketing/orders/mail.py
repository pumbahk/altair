# -*- coding:utf-8 -*-
from ticketing.mails.order_cancel import create_cancel_message
from pyramid_mailer import get_mailer
import logging

logger = logging.getLogger(__name__)

def on_order_canceled(event):
    message = create_cancel_message(event.request, event.order)
    mailer = get_mailer(event.request) ## todo.component化
    mailer.send(message)
    logger.info("send complete mail to %s" % message.recipients)
