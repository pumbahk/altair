# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from altair.app.ticketing.core.models import MailTypeEnum
from altair.app.ticketing.mails.api import get_mail_utility

Complete = MailTypeEnum.PurchaseCompleteMail
def on_order_completed(order_completed):
    try:
        order = order_completed.order
        request = order_completed.request
        mutil = get_mail_utility(request, Complete)
        mutil.send_mail(request, order)
    except Exception:
        logger.error("*complete mail* send mail is failed. order id: %d" % order.id,  exc_info=1)
