# encoding: utf-8

import logging
from sqlalchemy.orm.exc import NoResultFound
from .models import OrderNoSequence, ChannelEnum
from datetime import datetime
from altair.mobile.api import is_mobile

logger = logging.getLogger(__name__)

def get_next_order_no(name="order_no"):
    return OrderNoSequence.get_next_value(name)

def get_channel(channel=None, request=None):
    for c in ChannelEnum:
        if c.v == channel:
            return c

    if is_mobile(request):
        return ChannelEnum.Mobile
    else:
        return ChannelEnum.PC

def delete_event(event):
    # 既に販売されている場合は削除できない
    if event.sales_start_on and event.sales_start_on < datetime.now():
        raise Exception(u'既に販売開始日時を経過している為、削除できません')
    event.delete()

