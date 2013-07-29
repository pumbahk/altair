# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
import urllib
from urlparse import ParseResult, urlparse

from zope.interface import implementer
from .interfaces import IGlobalLinkSettings
from altaircms.auth.models import Host

## todo:move
def quote(x):
    return urllib.quote(x.encode("utf-8"), safe="%/:=&?~#+!$,;'@()*[]").decode("utf-8") if x else None

def _url_builder(scheme, host_name, path, query_dict=None):
    if query_dict:
        query = urllib.urlencode(query_dict, True)
    else:
        query = ""
    url_builder = ParseResult(scheme=scheme, netloc=host_name, path=path, params="", query=query, fragment="")
    return url_builder.geturl()

def _get_scheme_from_request(request):
    return "https" if request.url.startswith("https") else "http"

def get_hostname_from_request(request, qs=None, stage=None, default=None, preview=False):
    if stage is None:
        condition = get_host_filterling_condition(request)
    else:
        condition = get_host_filterling_condition_from_stage(stage, preview=preview)
    qs = qs or request.allowable(Host)
    if condition is not None:
        qs = qs.filter(condition)
    host = qs.first()
    if host:
        return host.host_name
    else:
        return default

@implementer(IGlobalLinkSettings)
class GlobalLink(object):
    def __init__(self, stage, backend_url, usersite_url):
        self.stage = stage
        self.usersite_url = usersite_url
        self.backend_url = backend_url

    @classmethod
    def from_settings(cls, settings, prefix="altaircms."):
        backend_parsed = urlparse(settings[prefix+"logout.external.url"]) #xxx:
        return cls(
            settings[prefix+"stage"], 
            "{scheme}://{netloc}".format(scheme=backend_parsed.scheme, netloc=backend_parsed.netloc), 
            settings[prefix+"usersite.url"], 
            )

def get_global_link_settings(request):
    return request.registry.queryUtility(IGlobalLinkSettings)

def get_usersite_url_builder(request):
    global_link  = get_global_link_settings(request)
    return UsersitePageURLAdapter(request, global_link)

def get_mobile_url_builder(request):
    global_link  = get_global_link_settings(request)
    return MobilePageURLAdapter(request, global_link)

def get_smartphone_url_builder(request):
    global_link  = get_global_link_settings(request)
    return SmartphonePageURLAdapter(request, global_link)

def get_backend_url_builder(request):
    global_link  = get_global_link_settings(request)
    return BackendPageURLAdapter(request, global_link)

def get_cms_url_builder(request):
    global_link  = get_global_link_settings(request)
    return CMSPageURLAdapter(request, global_link)

def get_cart_url_builder(request):
    global_link  = get_global_link_settings(request)
    return CartPageURLAdapter(request, global_link)

class CMSPageURLAdapter(object): #don't use this, on cms app.
    def __init__(self, request, global_link):
        self.request = request
        self.global_link = global_link
        self.default_hostname = "localhost:8001"

    def get_hostname(self):
        ## this is ad-hoc
        stage = self.global_link.stage
        if not Stage.contains(stage):
            return self.default_hostname
        elif Stage.production == stage:
            return "cms-service.ticketstar.jp"
        elif Stage.staging == stage:
            return "cms.stg2.rt.ticketstar.jp"
        elif Stage.develop == stage:
            return "cms.dev.ticketstar.jp"
        elif Stage.demo == stage:
            return "cms.demo.ticketstar.jp"
        else:
            logger.warn("invalid stage")
            return self.default_hostname

    def event_page_url(self, event, hostname=None):
        scheme = _get_scheme_from_request(self.request)
        hostname = hostname or self.get_hostname()        
        return _url_builder(scheme, hostname, "/event/{event_id}".format(event_id=event.id))


class BackendPageURLAdapter(object):
    def __init__(self, request, global_link):
        self.request = request
        self.global_link = global_link
        self.default_hostname = "localhost:8021"

    def event_page_url(self, event, hostname=None):
        scheme, hostname = self.global_link.backend_url.split("://", 1)
        return _url_builder(scheme, hostname, "/events/show/{event_id}".format(event_id=event.backend_id))


class CartPageURLAdapter(object):
    def __init__(self, request, global_link):
        self.request = request
        self.global_link = global_link
        self.default_hostname = "localhost:9001"

    def get_hostname(self):
        return get_hostname_from_request(self.request, default=self.default_hostname)

    def _get_scheme_hostname(self, hostname):
        if self.request.cart_domain:
            scheme, hostname = self.request.cart_domain.split("://", 1)
        else:
            scheme = _get_scheme_from_request(self.request)
            hostname = hostname or self.get_hostname()        
        return scheme, hostname

    def whattime_login_url(self, event, hostname=None):
        scheme, hostname = self._get_scheme_hostname(hostname)
        return _url_builder(scheme, hostname, "/whattime/login", {"event_id": unicode(event.id)})

    def whattime_form_url(self, event, hostname=None):
        scheme, hostname = self._get_scheme_hostname(hostname)
        return _url_builder(scheme, hostname, "/whattime/form", {"event_id": unicode(event.id)})

    def cart_url(self, event, hostname=None):
        scheme, hostname = self._get_scheme_hostname(hostname)
        return _url_builder(scheme, hostname, "/cart/events/{event_id}".format(event.id))



class MobilePageURLAdapter(object):
    def __init__(self, request, global_link):
        self.request = request
        self.global_link = global_link
        self.default_hostname = "localhost:9001"

    def get_hostname(self):
        return get_hostname_from_request(self.request, default=self.default_hostname)

    def event_page_url(self, event, hostname=None):
        scheme = _get_scheme_from_request(self.request)
        hostname = hostname or self.get_hostname()        
        return _url_builder(scheme, hostname, "/mobile/eventdetail", {"event_id": unicode(event.id)})

class SmartphonePageURLAdapter(object):
    def __init__(self, request, global_link):
        self.request = request
        self.global_link = global_link
        self.default_hostname = "localhost:9001"

    def get_hostname(self):
        return get_hostname_from_request(self.request, default=self.default_hostname)

    def event_page_url(self, event, hostname=None):
        scheme = _get_scheme_from_request(self.request)
        hostname = hostname or self.get_hostname()        
        return _url_builder(scheme, hostname, "/smartphone/detail", {"event_id": unicode(event.id)})

class UsersitePageURLAdapter(object):
    def __init__(self, request, global_link):
        self.request = request
        self.global_link = global_link
        self.default_hostname = "localhost:9001"

    def get_hostname(self):
        return get_hostname_from_request(self.request, default=self.default_hostname)

    def top_page_url(self, request, hostname=None):
        scheme = _get_scheme_from_request(self.request)
        hostname = hostname or self.get_hostname()
        return _url_builder(scheme, hostname, "/")

    def front_page_url(self, pageset, hostname=None):
        scheme = _get_scheme_from_request(self.request)
        hostname = hostname or self.get_hostname()
        path = u"/{0}".format(pageset.url.lstrip("/"))
        return _url_builder(scheme, hostname, path)

    def feature_page_url(self, static_pageset, hostname=None):
        scheme = _get_scheme_from_request(self.request)
        hostname = hostname or self.get_hostname()
        path = u"/features/{0}".format(static_pageset.url.lstrip("/"))
        return _url_builder(scheme, hostname, path)

    def build(self, pageset, hostname=None):
        if is_pageset(pageset):
            return self.front_page_url(pageset, hostname=hostname)
        else:
            return self.feature_page_url(pageset, hostname=hostname)

def is_pageset(pageset):
    return hasattr(pageset, "event_id") or getattr(pageset, "interceptive", None) is not None

def is_event_pageset(pageset):
    return  getattr(pageset, "event_id", None) is not None


def make_candidate_symbols(name, kwargs):
    assert "contains" not in kwargs
    assert "_candidates" not in kwargs
    @classmethod
    def contains(cls, k):
        return k in cls._candidates

    kwargs["contains"] = contains
    kwargs["_candidates"] = kwargs.values()
    return type(name, (object, ), kwargs)

Stage = make_candidate_symbols("Stage", 
                               dict(develop = "dev",
                                    staging = "staging",
                                    production = "production"))

def get_host_filterling_condition(request):
    url = request.url
    if "ticket.rakuten.co.jp" in url:
        return Host.host_name.like("%ticket.rakuten.co.jp")
    elif "service" in url:
        return Host.host_name.like("%tstar.jp")
    elif "stg2" in url:
        return Host.host_name.like("%stg2%")
    elif "dev" in url:
        return Host.host_name.like("%dev%")
    elif "demo" in url:
        return Host.host_name.like("%demo%")
    elif "localhost" in url:
        return Host.host_name.like("%localhost%")
    else:
        return None

def get_host_filterling_condition_from_stage(stage, preview=False):
    if not Stage.contains(stage):
        return None
    elif Stage.production == stage:
        if preview:
            return Host.host_name.like("%tstar.jp")
        else:
            return Host.host_name.like("%ticket.rakuten.co.jp")
    elif Stage.staging == stage:
        return Host.host_name.like("%stg2%")        
    elif Stage.develop == stage:
        return Host.host_name.like("%dev%")
    else:
        logger.warn("invalid stage")
        return None

def includeme(config):
    pass
