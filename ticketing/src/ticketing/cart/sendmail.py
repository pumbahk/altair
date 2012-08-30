# -*- coding:utf-8 -*-
from . import logger
from ..models import DBSession
import ticketing.mails.complete.api as api

def on_order_completed(order_completed):
    try:
        order = order_completed.order
        request = order_completed.request
        api.send_mail(request, order)
    except Exception:
        ## id見れないと困る
        DBSession.flush(order)
        logger.error("*complete mail* send mail is failed. order id: %d" % order.id,  exc_info=1)
