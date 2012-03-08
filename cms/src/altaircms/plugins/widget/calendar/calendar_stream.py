# -*- coding:utf-8 -*-
from datetime import date
from datetime import timedelta
from altaircms.itertools import group_by_n


"""
from calendar_stream import PackedCalendarStream
from calendar_stream import CalendarStreamGenerator
from datetime import date

gen = CalendarStreamGenerator(PackedCalendarStream, force_start_from_monday=True)
s = gen.start_from(2011, 7, 8)
ys = s.iterate_to(2012, 2, 2)
for r in ys:
    print [(y.value, m.value, d.value) for y, m, d in r]
"""

YEAR, MONTH, DAY = [0, 1, 2]

class CalendarStreamGenerator(dict):
    def __init__(self, stream_class=None, wdays=None, **kwargs):
        self.stream_class = stream_class or CalendarStream
        self.env = {}
        self.kwargs = kwargs

    def start_from(self, y, m, d):
        return self.stream_class(y, m, d, self.env, **self.kwargs)

class CalendarStream(object):
    def __init__(self, y, m, d, env=None):
        self.env = env or {}
        self.env["start_date"] = (y, m, d)

    def iterate_to(self, y, m, d):
        self.env["end_date"] = (y, m, d)
        return YearStream(self.env)

class Element(object):
    TYPE = "Element"
    def __repr__(self):
        return "[%s:%s]" % (self.TYPE, self.value)

class YearE(Element):
    TYPE = "Year"
    def __init__(self, y, env=None):
        self.value = y
        self.env = env
        self.is_start = y == env["start_date"][YEAR]
        self.is_end = y == env["end_date"][YEAR]

class YearStream(object):
    def __init__(self, env=None):
        self.env = env

    def __iter__(self):
        return (MonthStream(YearE(y, self.env)) \
                    for y in self.years())

    def years(self):
        by = self.env["start_date"][YEAR]
        ay = self.env["end_date"][YEAR]
        return range(by, ay+1)

class MonthE(Element):
    TYPE = "Month"
    def __init__(self, ye, m, env=None):
        self.ye = ye
        self.value = m
        self.env = env
        self.is_start = ye.is_start and m == self.env["start_date"][MONTH]
        self.is_end = ye.is_end and m == self.env["end_date"][MONTH]

class MonthStream(object):
    def __init__(self, ye):
        self.ye = ye
        
    def __iter__(self):
        return (DayStream(MonthE(self.ye, m, self.ye.env)) \
                                for m in self.months())

    def months(self):
        months = range(1, 13)
        if self.ye.is_start:
            _, m, _ = self.ye.env["start_date"]
            months = months[m-1:]
        if self.ye.is_end:
            _, m, _ = self.ye.env["end_date"]
            months = months[0:-(12-m)]
        return months

class DayE(Element):
    TYPE = "Day"
    def __init__(self, me, d, env=None):
        self.me = me
        self.value = d

class DayStream(object):
    def __init__(self, me):
        self.me = me

    def __iter__(self):
        return (DayE(self.me, d, self.me.env) \
                    for d in self.days())
                
    def _total_days(self):
        y = self.me.ye.value
        m = self.me.value
        next_month_date = _next_month_date(y, m, 1)
        return (next_month_date - date(y, m, 1)).days


    def days(self):
        if self.me.is_end:
            _, _, d = self.me.env["end_date"]
            return range(1, d+1)

        N = self._total_days()
        if self.me.is_start:
            _, _, d = self.me.env["start_date"]
            return range(d, N+1)
        else:
            return range(1, N+1)
        

def _next_month_date(y, m, d):
    if m == 12:
        return date(y+1, 1, d)
    else:
        return date(y, m+1, d)

def left_move_with_weekday(day):
    """ slide to monday
    """
    N = day.weekday()
    return day - timedelta(days=N)

def right_move_with_weekday(day):
    """ slide to friday
    """
    N = day.weekday()
    return day + timedelta(days=5-N)

class PackedCalendarStream(object):
    def __init__(self, y, m, d, env=None, wdays=None, force_start_from_monday=True):
        self.env = env or {}
        self.force_start_from_monday = force_start_from_monday
        self.env["original_start_date"] = (y, m, d)
        self.env["start_date"] = self._lmove_start_date_if_need(y, m, d)

    def _lmove_start_date_if_need(self, y, m, d):
        if self.force_start_from_monday:
            lmoved_day = left_move_with_weekday(date(y, m, d))
            y, m, d = lmoved_day.year, lmoved_day.month, lmoved_day.day
        return y, m, d

    def _rmove_end_date_if_need(self, y, m, d):
        if self.force_start_from_monday:
            rmoved_day = right_move_with_weekday(date(y, m, d))
            y, m, d = rmoved_day.year, rmoved_day.month, rmoved_day.day
        return y, m, d
                  

    def _iterate_to(self, y, m, d):
        self.env["original_end_date"] = (y, m, d)
        self.env["end_date"] = self._rmove_end_date_if_need(y, m, d)
        return YearStream(self.env)

    def iterate_to(self, y, m, d):
        st = self._iterate_to(y, m, d)
        return group_by_n(self._stream_consume(st), 7)
        
    def _stream_consume(self, st):
        for ms in st:
            for ds in ms:
                for d in ds:
                    yield ms.ye, ds.me, d

