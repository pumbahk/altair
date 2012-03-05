# -*- coding:utf-8 -*-

from calendar_stream import PackedCalendarStream
from calendar_stream import CalendarStreamGenerator
from collections import defaultdict

__all__ = ["CalendarOutput", "performances_to_dict"]

def performances_to_dict(performances):
    D = defaultdict(list)
    for p in performances:
        dt = p.performance_open.date()
        D[(dt.year, dt.month, dt.day)].append(p)
    return D

YEAR, MONTH, DAY = [0, 1, 2]
FIRST, LAST = [0, -1]

class CalendarWeek(object):
    def __init__(self, r, performances, month_changed=False):
        self.month_changed = month_changed or r[FIRST][MONTH].value != r[LAST][MONTH].value
        self.month = r[LAST][MONTH].value
        self.year = r[LAST][YEAR].value
        self.r = r
        self.week = []
        self.performances = performances

    WDAYCLASS_MAP = [["first"], 
                     [],
                     [],
                     [],
                     [],
                     ["saturday"],
                     ["last", "holiday"]]

    def __iter__(self):
        for day_class_base, (y, m, d) in zip(self.WDAYCLASS_MAP, self.r):
            day_class = day_class_base[:]
            day_class.append("odd_month" if m.value % 2 == 1 else "even_month")
            yield {"day_class": " ".join(day_class),
                   "day": d.value, 
                   "day_performances": self.performances[(y.value, m.value, d.value)]
                   }
    """
    * start of week: first
    * end of week: last
    * in saturday: saturday
    * in holiday(include sunday): holiday
    
    odd month: odd_month
    even month: even_month
    
    if change month durning rendeering a row, putting special th element before rendering.
    """

class CalendarOutput(object):
    template = None

    @classmethod
    def from_performances(cls, performances, template=None):
        return cls(performances = performances_to_dict(performances),
                   template=template)

    def __init__(self, performances=None, template=None):
        self.template = template or self.template
        self.performances = performances or defaultdict(list)
        
    def each_rows(self, begin_date, end_date):
        gen = CalendarStreamGenerator(PackedCalendarStream, force_start_from_monday=True)
        stream = gen.start_from(begin_date.year, begin_date.month, begin_date.day)
        itr = stream.iterate_to(end_date.year, end_date.month, end_date.day)
        yield CalendarWeek(itr.next(), self.performances, month_changed=True)
        for r in itr:
            yield CalendarWeek(r, self.performances)

    def render(self, begin_date, end_date):
        rows = self.each_rows(begin_date, end_date)
        return self.template.render_unicode(cal=rows)


### render function ##
# using these functioins in models.CalendarWidget.merge_settings() via getattr

import os
here = os.path.abspath(os.path.dirname(__file__))
from pyramid.renderers import render
from datetime import date

def _next_month_date(d):
    if d.month == 12:
        return date(d.year+1, 1, 1)
    else:
        return date(d.year, d.month+1, 1)

def this_month(widget, performances, request):
    """今月の内容を表示するカレンダー
    """
    template_name = os.path.join(here, "rakuten.calendar.mako")
    cal = CalendarOutput.from_performances(performances)
    ## fixme
    today = date.today()
    rows = cal.each_rows(date(today.year, today.month, 1), 
                         _next_month_date(today))
    return render(template_name, {"cal":rows}, request)

def term(widget, performances, request):
    """開始日／終了日を指定してその範囲のカレンダを表示
    """
    template_name = os.path.join(here, "rakuten.calendar.mako")
    cal = CalendarOutput.from_performances(performances)
    rows = cal.each_rows(widget.from_date, widget.to_date)
    return render(template_name, {"cal":rows}, request)

def listing(widget, performances, request): #fixme: rename
    """パフォーマンスを一覧表示するだけの内容
    """
    template_name = os.path.join(here, "simple.listing.mako")
    return render(template_name, {"performances": performances}, request)
