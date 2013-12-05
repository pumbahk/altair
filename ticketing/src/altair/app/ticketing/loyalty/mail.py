# -*- coding:utf-8 -*-
from altair.app.ticketing.mails.api import get_mail_utility
from altair.app.ticketing.core.models import MailTypeEnum
import logging

logger = logging.getLogger(__name__)

def on_point_granting_failed(event):
    organization = event.point_grant_history_entry.order.ordered_from
    if organization.setting.notify_point_granting_failure:
        try:
            get_mail_utility(event.request, MailTypeEnum.PointGrantingFailureMail).send_mail(event.request, event.point_grant_history_entry)
        except:
            logger.exception(u'point granting failure mail not sent')
