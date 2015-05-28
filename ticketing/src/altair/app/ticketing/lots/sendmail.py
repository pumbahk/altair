# -*- coding:utf-8 -*-

from altair.app.ticketing.core.models import MailTypeEnum
from altair.app.ticketing.mails.api import get_mail_utility


def includeme(config):
    config.include('altair.app.ticketing.mails')


def send_accepted_mail(request, lot_entry):
    """ 申し込み完了メール
    """
    mutil = get_mail_utility(request, MailTypeEnum.LotsAcceptedMail)
    return mutil.send_mail(request, (lot_entry, None))


def send_elected_mail(request, lot_entry, elected_wish):
    """ 当選通知メール
    """
    mutil = get_mail_utility(request, MailTypeEnum.LotsElectedMail)
    return mutil.send_mail(request, (lot_entry, elected_wish))


def send_rejected_mail(request, rejected_entry):
    """ 落選通知メール
    """
    mutil = get_mail_utility(request, MailTypeEnum.LotsRejectedMail)
    return mutil.send_mail(request, (rejected_entry, None))
