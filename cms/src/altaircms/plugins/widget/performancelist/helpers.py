#-*- coding:utf-8 -*-
from altaircms.helpers.event import WEEK
import logging
logger = logging.getLogger(__name__)
from altaircms.rowspanlib import RowSpanGrid
from .models import PerformancelistWidget
from altaircms.page.models import Page
from altair.viewhelpers.datetime_ import create_date_time_formatter, DateTimeHelper

def range_performance(performance):
    start_on = performance.start_on
    end_on = performance.end_on

    if end_on:
        if start_on.year == end_on.year and start_on.month == end_on.month and start_on.day == end_on.day:
            return False
        return True
    return False

def performance_describe_range_date(request, performance):
    dth = DateTimeHelper(create_date_time_formatter(request))
    return dth.term(
        performance.start_on and performance.start_on.date(),
        performance.end_on and performance.end_on.date(),
        with_weekday=True
        )

def performance_describe_date(performance):
    try:
        d = performance.start_on
        D = {"p_date": d.strftime(u"%Y年%m月%d日".encode("utf-8")).decode("utf-8"), 
             "p_week": unicode(WEEK[d.weekday()]), 
             }
        return u"%(p_date)s（%(p_week)s）" % D
    except Exception, e:
        logger.exception(str(e))
    
def performance_describe_time(performance):
    """ performanceからその公演が行われる時間を文字列で返す
    e.g. 
    公演日（曜日）　開場 XX:XX /開演 XX:XX　[購入ボタン]
    """
    try:
        if performance.open_on:
            p_time = u"開場 %s /開演 %s" % (performance.open_on.strftime("%H:%M"), 
                                            performance.start_on.strftime("%H:%M"))
        else:
            p_time = u"開演 %s" % (performance.start_on.strftime("%H:%M"))
        return p_time
    except Exception, e:
        logger.exception(str(e))

def venue_for_grid(data, k, changed):
    if changed:
        return k

def performance_for_grid(data, k, changed):
    return data

PerformanceGrid = RowSpanGrid()
PerformanceGrid.register("venue", mapping=venue_for_grid, keyfn=lambda data: data.venue)
PerformanceGrid.register("performance", mapping=performance_for_grid, keyfn=lambda data: data.id)
