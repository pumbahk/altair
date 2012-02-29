# -*- coding:utf-8 -*-

from zope.interface import implements
from altaircms.interfaces import IRenderable
import os

here = os.path.abspath(os.path.dirname(__file__))

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
    "a", 
    "a", 
    "a", 
    "a", 
    ]

def this_month():
    import calendar
    from datetime import date
    today = date.today()
    return {"description": u"""
pythonのcalendar.HTMLCalendarを使ったhtml
""", 
            "renderable": RenderableAdaptor(calendar.HTMLCalendar().formatmonth, today.year, today.month)
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
    from .renderable import CalendarOutput
    from datetime import date
    template = Template(filename=os.path.join(here, "rakuten.calendar.mako"), 
                        input_encoding="utf-8")
    return {
        "description":  u"""
現在の楽天チケットのカレンダー表示に合わせた表示形式のもの
""", 
        "renderable": RenderableAdaptor(CalendarOutput(template=template).render, 
                             date(2012, 2, 6),
                             date(2012, 3, 18))
        }
