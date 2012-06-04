# -*- coding:utf-8 -*-

from datetime import datetime
from datetime import date
import os
import itertools

from zope.interface import implements
from mako.template import Template

here = os.path.abspath(os.path.dirname(__file__))

from altaircms.interfaces import IRenderable
from altaircms.models import Performance
from renderable import CalendarOutput

def perf(id_, title, beg, end):
    p = Performance.from_dict(
        {"title": title, 
         "start_on": beg, 
         "end_on": end, 
         "event_id": 1, 
         "id": id_
         })
    return p
    
class RenderableAdaptor(object):
    implements(IRenderable)
    def __init__(self, fn, *args, **kwargs):
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def render(self):
        return self.fn(*self.args, **self.kwargs)

    __call__ = render


dummy_performances = [
    perf(1, "event1", datetime(2012, 2, 10, 10), datetime(2012, 2, 10, 12)), 
    perf(2, "event2", datetime(2012, 2, 13, 13), datetime(2012, 2, 13, 15)), 
    perf(3, "event3", datetime(2012, 2, 20, 20), datetime(2012, 2, 20, 12)), 
    perf(1, "event1", datetime(2012, 3, 10, 10), datetime(2012, 3, 10, 13)), 
    perf(3, "event3", datetime(2012, 3, 15, 15), datetime(2012, 3, 15, 15)), 
    perf(5, "event5", datetime(2012, 3, 20, 20), datetime(2012, 3, 20, 13)), 
    ]


def obi():
    template = Template(filename=os.path.join(here, "rakuten.calendar.mako"), 
                        input_encoding="utf-8")
    cal = CalendarOutput.from_performances(dummy_performances, template=template)
    return {
        "description":  u"""
一番初めの講演日と一番最後の講演日から縦長のカレンダーを作成。
""", 
        "renderable": RenderableAdaptor(cal.render,
                                        dummy_performances[0].start_on, 
                                        dummy_performances[-1].start_on), 
        }
    
def term():
    from forms import SelectTermForm
    template = Template(filename=os.path.join(here, "rakuten.calendar.mako"), 
                        input_encoding="utf-8")
    cal = CalendarOutput.from_performances(dummy_performances, template=template)
    return {
        "description":  u"""
開始日／終了日を指定してその範囲のカレンダを表示
(下の例は、開始＝2012-2-6、終了＝2012-3-18で設定したときの表示)
""", 
        "renderable": RenderableAdaptor(cal.render, 
                             date(2012, 2, 6),
                             date(2012, 3, 18)), 
        "form_class": SelectTermForm
        }

def _next_month_date(d):
    if d.month == 12:
        return date(d.year+1, 1, 1)
    else:
        return date(d.year, d.month+1, 1)

def tab():
    performances = [
        perf(1, "event1", datetime(2012, 2, 10, 10), datetime(2012, 2, 10, 12)), 
        perf(2, "event2", datetime(2012, 2, 13, 13), datetime(2012, 2, 13, 15)), 
        perf(3, "event3", datetime(2012, 4, 20, 20), datetime(2012, 4, 20, 12)), 
        perf(1, "event1", datetime(2012, 5, 10, 10), datetime(2012, 5, 10, 12)), 
        ]
    template = Template(filename=os.path.join(here, "rakuten.tab-calendar.mako"), 
                        input_encoding="utf-8")
    visibilities = itertools.chain([True], itertools.repeat(False))
    if len(set(p.start_on.year for p in performances)) == 1:
        months = sorted(set(p.start_on.month for p in performances))
    else:
        months = sorted(set((p.start_on.year, p.start_on.month) for p in performances))
    monthly_performances = itertools.groupby(performances, lambda p: (p.start_on.year, p.start_on.month))
    cals = (CalendarOutput.from_performances(perfs).each_rows(date(y, m, 1), _next_month_date(date(y, m, 1)))\
                for (y, m), perfs in monthly_performances)
    return {"description": u"""
パフォーマンスが存在する月のタブを付加したカレンダー。
""",
            "renderable": RenderableAdaptor(template.render, cals=cals, months=months, visibilities=visibilities)
            }

if __name__ == "__main__":
    # print term()["renderable"].render()
    # print obi()["renderable"].render()
    print tab()["renderable"].render()
