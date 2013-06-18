# -*- coding:utf-8 -*-
import logging
from ..api import list_from_setting_value
from altaircms.plugins.api import get_widget_utility


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

