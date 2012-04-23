# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__file__)

from calendar_stream import PackedCalendarStream
from calendar_stream import CalendarStreamGenerator
from collections import defaultdict
from . import CalendarTemplatePathStore
import itertools

__all__ = ["CalendarOutput", "performances_to_dict"]

def performances_to_dict(performances):
    D = defaultdict(list)
    for p in performances:
        dt = p.start_on.date()
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

### todo:fix パフォーマンスリストと同期した形で連番を振る必要があるのでここで連番を振るのは良くない。(タブ表示で死)
class _Counter(object):
    def __init__(self, i):
        self.i = i

    def __call__(self):
        r = self.i
        self.i += 1
        return r

class CalendarOutput(object):
    template = None

    @classmethod
    def from_performances(cls, performances, template=None):
        return cls(performances = performances_to_dict(performances),
                   template=template)

    def __init__(self, performances=None, template=None):
        self.i = _Counter(1)
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
        return self.template.render_unicode(cal=rows, i=self.i)

def _collect_months(performances):
    """パフォーマンスリストから月毎のカレンダーを求める
    e.g. 2011-7-12, 2011-7-13, 2011-9-1
    => [((2011, 7), {"start":12, "end":12}), 
        ((2011, 9), {"start":1, "end":1})]
    """
    from iterools import group_by
    return group_by(performances, lambda p: (p.start_on.year, p.start_on.month))

### render function ##
# using these functioins in models.CalendarWidget.merge_settings() via getattr

from pyramid.renderers import render
from datetime import date

def _next_month_date(d):
    if d.month == 12:
        return date(d.year+1, 1, 1)
    else:
        return date(d.year, d.month+1, 1)

def obi(widget, performances, request):
    """講演の開始から終了までを縦に表示するカレンダー
    ※ performancesはstart_onでsortされているとする
    """
    template_name = CalendarTemplatePathStore.path("obi")
    logger.debug("calendar template: "+template_name)

    performances = list(performances)
    if performances:
        cal = CalendarOutput.from_performances(performances)
        rows = cal.each_rows(performances[0].start_on, performances[-1].start_on)
        return render(template_name, {"cal":rows, "i":cal.i}, request)
    else:
        return u"performance is not found"

def term(widget, performances, request):
    """開始日／終了日を指定してその範囲のカレンダーを表示
    """
    template_name = CalendarTemplatePathStore.path("term")
    logger.debug("calendar template: "+template_name)

    cal = CalendarOutput.from_performances(performances)
    rows = cal.each_rows(widget.from_date, widget.to_date)
    return render(template_name, {"cal":rows, "i":cal.i}, request)

def tab(widget, performances, request):
    """月毎のタブが存在するカレンダーを表示
    ※ performancesはstart_onでsortされているとする
    """
    template_name = CalendarTemplatePathStore.path("tab")
    logger.debug("calendar template: "+template_name)


    months = sorted(set((p.start_on.year, p.start_on.month) for p in performances))
    visibilities = itertools.chain([True], itertools.repeat(False))
    monthly_performances = itertools.groupby(performances, lambda p: (p.start_on.year, p.start_on.month))
    cals = (CalendarOutput.from_performances(perfs).each_rows(date(y, m, 1), _next_month_date(date(y, m, 1)))\
                for (y, m), perfs in monthly_performances)
    return render(template_name, {"cals":cals, "months":months, "visibilities": visibilities})
