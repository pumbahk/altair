# -*- coding:utf-8 -*-
import logging
import json
import contextlib
import urllib2
from ..api import list_from_setting_value
from altaircms.plugins.api import get_widget_utility
from collections import defaultdict
from altaircms.plugins.interfaces import IExternalAPI
from zope.interface import implementer

logger = logging.getLogger(__name__)

def get_rendering_function_via_page(widget, bname, bsettings, type_=None):
    bsettings.need_extra_in_scan("request")
    bsettings.need_extra_in_scan("page")
    def closure():
        try:
            request = bsettings.extra["request"]
            page = bsettings.extra["page"]
            utility = get_widget_utility(request, page, type_ or widget.type)
            return utility.render_action(request, page, widget, bsettings)
        except Exception, e:
            logger.exception(str(e))
            _type = type_ or widget.type
            logger.warn("%s_merge_settings. info is empty" % _type)
            return u"%s widget: %s" % (_type, str(e))
    return closure

def safe_execute(name):
    def _safe_execute(fn):
        def wrapped(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except Exception, e:
                logger.exception(str(e))
                return u"%s widget: %s" % (name, str(e))
        return wrapped
    return _safe_execute



class DisplayTypeSelectRendering(object):
    def __init__(self, params, configparser):
        jnames = list_from_setting_value(params["jnames"].decode("utf-8"))
        self.names = names = list_from_setting_value(params["names"].decode("utf-8"))
        self.choices = zip(names, jnames)

        self.name_to_jname = dict(self.choices)
        self.jname_to_name = dict(zip(jnames, names))
        self.actions = {}

    def validation(self):
        return all(name in self.actions for name in self.names)

    def register(self, name, action):
        self.actions[name] = action

    def lookup(self, k, default=None):
        return self.actions.get(k, default)

from pyramid.interfaces import IRouter
class WrappedRequest(object):
    def __init__(self, o):
        self.o = o

    def __getattr__(self, k):
        return getattr(self.o, k)

    def __setattr__(self, k, v):
        self.__dict__[k] = v

class WidgetRegisterViewProxy(object):
    def __init__(self, request, request_method="POST"):
        self.request = request
        self.router = request.registry.getUtility(IRouter)
        self.request_method = request_method
        
    def _build_route_name(self, prefix, suffix):
        return u"{0}_{1}".format(prefix.rstrip("_"), suffix.lstrip("_"))

    def _create_request(self, route_name, params, matchdict=None):
        from pyramid.interfaces import IRequest
        matchdict = matchdict or {}
        request = WrappedRequest(self.request)
        request.json_body = params
        request.environ = request.environ.copy()
        request.environ["REQUEST_METHOD"] = self.request_method
        request.method = self.request_method
        request.request_iface = IRequest
        request.registry = request.registry

        logger.debug("route_Name: {0}".format(route_name))
        request.environ["PATH_INFO"] = request.route_path(route_name, **matchdict)
        logger.debug("PATH INFO: {0}".format(request.environ["PATH_INFO"] ))
        return request

    def _use_view(self, route_name, params, matchdict=None):
        request = self._create_request(route_name, params, matchdict=matchdict)
        return self.router.handle_request(request)

    def create(self, name, params, matchdict=None):
        route_name = self._build_route_name(name, "_widget_create")        
        return self._use_view(route_name, params, matchdict=matchdict)


"""
cms calendar:

status :: performance -> stock-status
 """

def get_stock_data_api(request):
    return request.registry.getUtility(IExternalAPI, name=StockDataAPI.__name__)

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

dummy_data = {"stocks": []}
def get_performance_status(request, widget, event, status_impl):
    """
    call api
    """
    data = dummy_data
    try:
        data = getattr(request, "_stock_data", None)
        if not data:
            data = get_stock_data_api(request).fetch_stock_status(request, event, widget.salessegment)
            data = json.loads(data)
            request._stock_data = data
    except urllib2.HTTPError, e:
        logger.warn("*calendar widget* api call is failed. url=%s" % e.url)
    except urllib2.URLError, e:
        logger.warn("*calendar widget* api call is failed (URLError)")
    except Exception, e:
        logger.warn("*calendar widget* api call is failed")
        logger.exception(str(e))
    return _get_performance_status(request, CalcResult(rawdata=data, status_impl=status_impl))

def _get_performance_status(request, data):
    for stock in data.rawdata["stocks"]:
        data.add_stock(stock)
    return data

###


@implementer(IExternalAPI)
class StockDataAPI(object):
    def __init__(self, url, apikey):
        self.external_url = url.rstrip("/")
        self.apikey = apikey

    def get_fetch_stock_status_api_url(self, event, salessegment_group):
        fmt = u"%(base)s/api/events/%(event_id)s/stock_statuses"
        return fmt % dict(base=self.external_url, event_id=event.backend_id)

    def fetch_stock_status(self, request, event, salessegment_group=None):
        url = self.get_fetch_stock_status_api_url(event, salessegment_group)
        req = urllib2.Request(url)
        req.add_header('X-Altair-Authorization', self.apikey)
        with contextlib.closing(urllib2.urlopen(req)) as res:
            data = res.read()
            logger.debug("*calendar widget api* returned value: %s" % data)
            return data


class NotFoundMatchResultException(Exception):
    pass

## (find-file "api-dummy-data.json")
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
        if stock["available"] <= 0:
            self.has_soldout[k] = True

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
