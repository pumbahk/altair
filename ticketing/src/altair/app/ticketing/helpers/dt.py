# encoding: utf-8

from altair.app.ticketing.utils import todatetime, todate

import logging

logger = logging.getLogger(__name__)

def japanese_date(date):
    return u"%d年%d月%02d日(%s)" % (date.year, date.month, date.day, u"月火水木金土日"[date.weekday()])

def japanese_time(time):
    return u"%d時%02d分" % (time.hour, time.minute)

def japanese_datetime(dt):
    try:
        return japanese_date(dt) + ' ' + japanese_time(dt)
    except:
        logger.warn("dt is None")
        return ""