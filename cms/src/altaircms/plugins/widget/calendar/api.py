# -*- coding:utf-8 -*-

import json
import logging
from collections import defaultdict
logger = logging.getLogger(__file__)

"""
cms calendar:

status :: performance -> calendar-status
 """
class NotFoundMatchResultException(Exception):
    pass

class CalendarStatus(object):
    circle = u"○"
    triangle = u"△"
    cross = u"×"

## (find-file "api-dummy-data.json")
class CalcResult(object): #すごい決め打ち
    def __init__(self, rawdata=None):
        self.scores = defaultdict(int)
        self.counts = defaultdict(int)
        self.has_soldout = {}
        self.rawdata = rawdata

    def add_stock(self, stock):
        k = stock["performance_id"]
        self.scores[k] += stock["available"]
        self.counts[k] += stock["assigned"]
        if stock["available"] <= 0:
            self.has_soldout[k] = True

    def get_status(self, performance):
        k = performance.backend_id
        try:
            if self.scores[k] <= 0:
                return CalendarStatus.cross
            elif self.has_soldout.get(k) or (float(self.scores[k]) / self.counts[k]) <= 0.2:
                return CalendarStatus.triangle
            else:
                return CalendarStatus.circle
        except KeyError:
            logger.warn("performance [backend_id=%d] is not found" % performance.backend_id)
            return CalendarStatus.cross

def get_performance_status(request):
    """
    call api
    """
    data = json.loads(dummy_data)
    return _get_performance_status(request, CalendarStatus(rawdata=data))

def _get_performance_status(request, data):
    for stock in data.rawdata["stocks"]:
        data.add_stock(stock)
    return data
