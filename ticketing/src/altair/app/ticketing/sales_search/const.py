# -*- coding:utf-8 -*-
from standardenum import StandardEnum


class SalesKindEnum(StandardEnum):
    SALES_START = u'sales_start'
    LOTS_ANNOUNCE_TIME = u'lots_announce_time'


class SalesTermEnum(StandardEnum):
    TODAY = u"today"
    TOMORROW = u"tomorrow"
    THIS_WEEK = u"this_week"
    THIS_WEEK_PLUS_MONDAY = u"this_week_plus_monday"
    NEXT_WEEK = u"next_week"
    NEXT_WEEK_PLUS_MONDAY = u"next_week_plus_monday"
    THIS_MONTH = u"this_month"
    TERM = u"term"
