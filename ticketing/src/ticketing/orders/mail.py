# -*- coding:utf-8 -*-
from ticketing.mails.api import get_mail_utility
from ticketing.core.models import MailTypeEnum
import logging

logger = logging.getLogger(__name__)

Cancel = MailTypeEnum.PurchaseCancelMail
def on_order_canceled(event):
    get_mail_utility(event.request, Cancel).send_mail(event.request, event.order)
