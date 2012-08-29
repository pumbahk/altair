# -*- coding:utf-8 -*-
from pyramid_mailer import get_mailer
from . import logger
from ticketing.mails.api import get_complete_mail
from ..models import DBSession
## dummy mailer

def on_order_completed(order_completed):
    try:
        order = order_completed.order
        request = order_completed.request
        message = create_message(request, order)
        mailer = get_mailer(request) ## todo.component化
        mailer.send(message)
        logger.info("send mail to %s" % message.recipients)
    except Exception, e:
        ## id見れないと困る
        DBSession.flush(order)
        logger.error("*complete mail* send mail is failed. order id: %d" % order.id,  exc_info=1)

def create_message(request, order):
    complete_mail = get_complete_mail(request)
    return complete_mail.build_message(order)
