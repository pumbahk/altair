# -*- coding:utf-8 -*-

import json
import contextlib
import urllib2
import logging
from collections import defaultdict
from altaircms.plugins.interfaces import IExternalAPI
from zope.interface import implementer
logger = logging.getLogger(__file__)

"""
cms calendar:

status :: performance -> calendar-status
 """

def get_calendar_data_api(request):
    return request.registry.getUtility(IExternalAPI, name=CalendarDataAPI.__name__)

class CalendarStatus(object):
    circle = {"class": "circle", "string":u"○"}
    triangle = {"class": "triangle", "string":u"△"}
    cross = {"class": "cross", "string":u"×"}

class MaruBatsuSankaku(object):
    circle = {"class": "maru", "string":u"○"}
    triangle = {"class": "sankaku", "string":u"△"}
    cross = {"class": "batsu", "string":u"×"}

dummy_data = {"stocks": []}
def get_performance_status(request, widget, event, status_impl):
    """
    call api
    """
    try:
        data = get_calendar_data_api(request).fetch_stock_status(request, event, widget.salessegment)
        data = json.loads(data)
    except Exception, e:
        logger.warn("*calendar widget* api call is failed")
        # logger.exception(str(e))
        data =  dummy_data
    return _get_performance_status(request, CalcResult(rawdata=data, status_impl=status_impl))

def _get_performance_status(request, data):
    for stock in data.rawdata["stocks"]:
        data.add_stock(stock)
    return data

### 


@implementer(IExternalAPI)
class CalendarDataAPI(object):
    def __init__(self, url):
        self.external_url = url

    def fetch_stock_status(self, request, event, salessegment=None):
        fmt = self.external_url.rstrip("/")+"/api/events/%(event_id)s/stock_statuses"
        url = fmt % dict(event_id=event.backend_id)
        with contextlib.closing(urllib2.urlopen(url)) as res:
            data = res.read()
            return data 


class NotFoundMatchResultException(Exception):
    pass

## (find-file "api-dummy-data.json")
class CalcResult(object): #すごい決め打ち
    def __init__(self, rawdata=None, status_impl=CalendarStatus):
        self.status_impl = status_impl
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
                return self.status_impl.cross
            elif self.has_soldout.get(k) or (float(self.scores[k]) / self.counts[k]) <= 0.2:
                return self.status_impl.triangle
            else:
                return self.status_impl.circle
        except KeyError:
            logger.warn("performance [backend_id=%d] is not found" % performance.backend_id)
            return self.status_impl.cross
