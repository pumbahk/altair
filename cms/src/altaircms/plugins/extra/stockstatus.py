# -*- coding:utf-8 -*-
import json
import urllib2
from collections import defaultdict
from altaircms.plugins.interfaces import IExternalAPI
from zope.interface import implementer
import contextlib


import logging
logger = logging.getLogger(__name__)

dummy_data = {"stocks": []}
@implementer(IExternalAPI)
class StockDataAPI(object):
    def __init__(self, url, apikey):
        self.external_url = url.rstrip("/")
        self.apikey = apikey

    def get_fetch_stock_status_api_url(self, event):
        fmt = u"%(base)s/api/events/%(event_id)s/stock_statuses"
        return fmt % dict(base=self.external_url, event_id=event.backend_id)

    def fetch_stock_status(self, request, event):
        url = self.get_fetch_stock_status_api_url(event)
        req = urllib2.Request(url)
        req.add_header('X-Altair-Authorization', self.apikey)
        try:
            with contextlib.closing(urllib2.urlopen(req)) as res:
                data = res.read()
                logger.debug("*calendar widget api* returned value: %s" % data)
                data = json.loads(data)
                return data
        except urllib2.HTTPError, e:
            logger.warn("*calendar widget* api call is failed. url=%s" % e.url)
        except urllib2.URLError, e:
            logger.warn("*calendar widget* api call is failed (URLError)")
        except Exception, e:
            logger.warn("*calendar widget* api call is failed")
            logger.exception(str(e))
        return dummy_data


## (find-file "api-dummy-data.json")
class StockStatus(object):
    circle = {"class": "circle", "string":u"○"}
    triangle = {"class": "triangle", "string":u"△"}
    cross = {"class": "cross", "string":u"×"}
    unknown = {"class": "unknown", "string": u""}

class MaruBatsuSankaku(object):
    circle = {"class": "maru", "string":u"○"}
    triangle = {"class": "sankaku", "string":u"△"}
    cross = {"class": "batsu", "string":u"×"}
    unknown = {"class": "hatena", "string": u""}

class CalcResult(object): #すごい決め打ち
    def __init__(self, rawdata=None, status_impl=StockStatus):
        self.status_impl = status_impl
        self.scores = defaultdict(int)
        self.counts = defaultdict(int)
        self.has_soldout = {}
        self.rawdata = rawdata

    def add_stock(self, stock):
        k = stock["performance_id"]
        self.scores[k] += stock["available"]
        self.counts[k] += stock["assigned"]
        # if stock["available"] <= 0:
        #     self.has_soldout[k] = True

    def get_status(self, performance):
        if performance.purchase_link:
            return self.status_impl.unknown
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
