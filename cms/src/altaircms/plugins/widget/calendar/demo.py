# -*- coding:utf-8 -*-

from zope.interface import implements
from altaircms.interfaces import IRenderable
import os

here = os.path.abspath(os.path.dirname(__file__))

from datetime import datetime
from altaircms.models import Performance
def perf(id_, title, beg, end):
    p = Performance.from_dict(
        {"title": title, 
         "performance_open": beg, 
         "performance_close": end, 
         "event_id": 1, 
         "id": id_
         })
    # p.title = title
    # p.performance_open = beg
    # p.performance_close = end
    # p.event_id = 1
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

# def this_month():
#     import calendar
#     from datetime import date
#     today = date.today()
#     return {"description": u"""
# pythonのcalendar.HTMLCalendarを使ったhtml
# """, 
#             "renderable": RenderableAdaptor(calendar.HTMLCalendar().formatmonth, today.year, today.month)
#             }

def this_month():
    from mako.template import Template
    from renderable import CalendarOutput
    from datetime import date
    template = Template(filename=os.path.join(here, "rakuten.calendar.mako"), 
                        input_encoding="utf-8")
    cal = CalendarOutput.from_performances(dummy_performances, template=template)
    return {
        "description":  u"""
今月の内容を表示するカレンダー
""", 
        "renderable": RenderableAdaptor(cal.render, 
                             date(2012, 2, 1),
                             date(2012, 2, 29))
        }

def list():
    from mako.template import Template
    template = Template(filename=os.path.join(here, "simple.listing.mako"), 
                        input_encoding="utf-8")
    return {
        "description": u"""
パフォーマンスを一覧表示するだけの内容
""", 
        "renderable": RenderableAdaptor(template.render, performances=dummy_performances)
        }


    
    
def term():
    from mako.template import Template
    from renderable import CalendarOutput
    from datetime import date
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

if __name__ == "__main__":
    print this_month()["renderable"].render()
    print list()["renderable"].render()
    print term()["renderable"].render()
