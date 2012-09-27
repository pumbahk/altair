# -*- coding:utf-8 -*-
import logging

logger = logging.getLogger(__name__)

def japanese_date(date):
    return u"%d年%d月%d日(%s)" % (date.year, date.month, date.day, u"月火水木金土日"[date.weekday()])

def japanese_time(time):
    return u"%d時%d分" % (time.hour, time.minute)

def japanese_datetime(dt):
    try:
        return japanese_date(dt)+japanese_time(dt)
    except:
        logger.error("dt is None")
        return ""
