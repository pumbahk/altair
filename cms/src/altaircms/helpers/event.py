# -*- coding:utf-8 -*-
from webhelpers.number import format_number as _format_number
from .base import jdate
import json

WEEK =[u"月", u"火", u"水", u"木", u"金", u"土", u"日"]

def _to_term(p):
    r = []
    if p.open_on:
        r.append(u"%s開場" % p.open_on.strftime("%H:%M"))
    if p.start_on:
        r.append(u"%s開演" % p.start_on.strftime("%H:%M"))
    if p.end_on:
        r.append(u"%s終了" % p.end_on.strftime("%H:%M"))
    return u"／".join(r)

def _to_where(p):
    return p.venue

# def performance_name(performance):
#     return u"%s (%s)" % (performance.title, _to_term(performance))

def performance_name(performance):
    return u"%s(日時:%s, 場所:%s)" % (performance.title, performance.start_on, performance.venue)

def performance_describe(performance):
    """ performanceから公演場所や日時を表示する文字列を返す
    """
    return u"　".join([jdate(performance.open_on), 
                       u"〜", 
                       jdate(performance.end_on), 
                       _to_where(performance), 
                       ])

def performance_description(performance):
    """ performanceから公演場所や日時を表示する文字列を返す(old)
    e.g.
    2012年6月3日（日）　16:30開場／17:00開演　岸和田市立浪切ホール　大ホール
    """
    return u"　".join([jdate(performance.open_on), _to_term(performance) , _to_where(performance)])

def performance_time(performance):
    """ performanceからその公演が行われる時間を文字列で返す
    e.g. 
    2012年6月3日(日) 17:00
    """
    d = performance.open_on
    datestr = d.strftime(u"%Y年%m月%d日".encode("utf-8")).decode("utf-8")
    timestr = d.strftime("%H:%M")
    return u"%s（%s）%s" % (datestr, unicode(WEEK[d.weekday()]),  timestr)


def event_time(event):
    open = event.event_open
    close = event.event_close
    open_datestr = open.strftime(u"%Y年%m月%d日".encode("utf-8")).decode("utf-8")
    if open == close:
        return u"{}({})".format(open_datestr, unicode(WEEK[open.weekday()]))
    close_datestr = close.strftime(u"%Y年%m月%d日".encode("utf-8")).decode("utf-8")
    return u"{}({}) 〜 {}({})".format(open_datestr, unicode(WEEK[open.weekday()]), close_datestr,
                                     unicode(WEEK[close.weekday()]))


def get_venues(event):
    venues = [performance.venue for performance in event.performances]
    venues = sorted(set(venues), key=venues.index) # 重複削除
    return u"<br/>".join(venues)


def get_second_image_from_pagesets(request, pageset):
    # 登録されている2つ目の画像を取得する
    import altaircms.helpers as helpers
    from altaircms.plugins.widget.image.models import ImageWidget
    current_page = pageset.current(published=True)
    structures = json.loads(current_page.structure).items()
    images = []
    for structure in structures:
        for widget in structure[1]:
            if widget['name'] == u'image':
                images.append(widget)
            if len(images) == 2:
                break
    if images:
        # 2個目のImageWidgetを使用する。なければ、1個目のImageWidgetを使用する
        widget = images[len(images) - 1]
        image_widget = ImageWidget.query.filter(ImageWidget.id == widget['pk']).first()
        if image_widget:
            return helpers.asset.rendering_object(request, image_widget.asset).filepath
    return ""


def format_number(num, thousands=","):
    return _format_number(int(num), thousands)
price_format = format_number #deprecated

def format_currency(num, thousands=","):
    return u"￥" + format_number(num, thousands)

from zope.deprecation import deprecation
@deprecation.deprecate("this is deprecation method. dont use it")
def detect_performance_status(performance):
    """ circle, triangle, cross
    """
    import warnings
    warnings.warn("it is not implemented, yet, that detect performance status logic")
    return "circle"

@deprecation.deprecate("this is deprecation method. dont use it")
def content_string_from_performance_status(status):
    return {"circle": u"○", 
            "triangle": u"△", 
            "cross": u"×"}.get(status, u"?")
