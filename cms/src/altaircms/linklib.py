# -*- coding:utf-8 -*-
import logging
import urllib
from urlparse import ParseResult, urlparse, parse_qs

from zope.interface import implementer
from .interfaces import IGlobalLinkSettings
from altair.viewhelpers.structure import updated

from .api import get_hostname_from_request
from .interfaces import (
    ICMSPageURLAdapter,
    IBackendPageURLAdapter,
    ICartPageURLAdapter,
    ICMSMobilePageURLAdapter,
    ICMSSmartphonePageURLAdapter,
    ICMSPCPageURLAdapter,
    )

logger = logging.getLogger(__name__)

## todo:move
def quote(x):
    return urllib.quote(x.encode("utf-8"), safe="%/:=&?~#+!$,;'@()*[]").decode("utf-8") if x else None

def add_params_to_url(url, params_dict, parse_qs_opts=dict()):
    if not isinstance(url, ParseResult):
        url = urlparse(url)
    qs_dict = parse_qs(str(url.query), **parse_qs_opts)
    qs_dict.update(params_dict)
    return _url_builder(url.scheme, url.hostname, url.path, qs_dict)

def _url_builder(scheme, host_name, path, query_dict=None):
    if query_dict:
        query = urllib.urlencode(query_dict, True)
    else:
        query = ""
    url_builder = ParseResult(scheme=scheme, netloc=host_name, path=path, params="", query=query, fragment="")
    return url_builder.geturl()

def _get_scheme_from_request(request):
    return request.scheme

@implementer(ICMSPageURLAdapter)
class CMSPageURLAdapter(object): #don't use this, on cms app.
    def __init__(self, default_hostname="localhost:8001"):
        self.default_hostname = default_hostname

    def get_hostname(self):
        return self.default_hostname

    def event_page_url(self, request, event, hostname=None):
        scheme = _get_scheme_from_request(request)
        hostname = hostname or self.get_hostname()        
        return _url_builder(scheme, hostname, "/event/{event_id}".format(event_id=event.id))


@implementer(IBackendPageURLAdapter)
class BackendPageURLAdapter(object):
    def __init__(self, backend_url, default_hostname="localhost:8021"):
        self.backend_url = backend_url
        self.default_hostname = default_hostname

    def top_page_url(self, request):
        return self.backend_url

    def event_page_url(self, request, event, hostname=None):
        scheme, hostname = self.backend_url.split("://", 1)
        return _url_builder(scheme, hostname, "/events/show/{event_id}".format(event_id=event.backend_id))


@implementer(ICartPageURLAdapter)
class CartPageURLAdapter(object):
    def __init__(self, default_hostname="localhost:9001"):
        self.default_hostname = default_hostname

    def get_hostname(self, request):
        return get_hostname_from_request(request, default=self.default_hostname)

    def _get_scheme_hostname(self, request, hostname):
        if request.cart_domain:
            scheme, hostname = request.cart_domain.split("://", 1)
        else:
            scheme = _get_scheme_from_request(request)
            hostname = hostname or self.get_hostname(request)
        return scheme, hostname

    def whattime_login_url(self, request, event, hostname=None, _query=None):
        scheme, hostname = self._get_scheme_hostname(request, hostname)
        return _url_builder(scheme, hostname, "/whattime/login", updated({"event_id": unicode(event.id)}, _query))

    def whattime_form_url(self, request, event, hostname=None, _query=None):
        scheme, hostname = self._get_scheme_hostname(request, hostname)
        return _url_builder(scheme, hostname, "/whattime/form", updated({"event_id": unicode(event.id)}, _query))

    def cart_url(self, request, hevent, ostname=None):
        scheme, hostname = self._get_scheme_hostname(request, hostname)
        return _url_builder(scheme, hostname, "/cart/events/{event_id}".format(event.id))


@implementer(ICMSMobilePageURLAdapter)
class MobilePageURLAdapter(object):
    def __init__(self, default_hostname="localhost:9001"):
        self.default_hostname = default_hostname

    def get_hostname(self, request):
        return get_hostname_from_request(request, default=self.default_hostname)

    def event_page_url(self, request, event, hostname=None):
        scheme = _get_scheme_from_request(request)
        hostname = hostname or self.get_hostname(request)
        return _url_builder(scheme, hostname, "/mobile/eventdetail", {"event_id": unicode(event.id)})

@implementer(ICMSSmartphonePageURLAdapter)
class SmartphonePageURLAdapter(object):
    def __init__(self, default_hostname="localhost:9001"):
        self.default_hostname = default_hostname

    def get_hostname(self, request):
        return get_hostname_from_request(request, default=self.default_hostname)

    def event_page_url(self, request, event, hostname=None):
        scheme = _get_scheme_from_request(request)
        hostname = hostname or self.get_hostname(request)
        return _url_builder(scheme, hostname, "/smartphone/detail", {"event_id": unicode(event.id)})

@implementer(ICMSPCPageURLAdapter)
class UsersitePageURLAdapter(object):
    def __init__(self, default_hostname="localhost:9001"):
        self.default_hostname = default_hostname

    def get_hostname(self, request):
        return get_hostname_from_request(request, default=self.default_hostname)

    def top_page_url(self, request, hostname=None):
        scheme = _get_scheme_from_request(request)
        hostname = hostname or self.get_hostname(request)
        return _url_builder(scheme, hostname, "/")

    def front_page_url(self, request, pageset, hostname=None):
        scheme = _get_scheme_from_request(request)
        hostname = hostname or self.get_hostname(request)
        path = u"/{0}".format(pageset.url.lstrip("/"))
        return _url_builder(scheme, hostname, path)

    def feature_page_url(self, request, static_pageset, hostname=None):
        scheme = _get_scheme_from_request(request)
        hostname = hostname or self.get_hostname(request)
        path = u"/features/{0}".format(static_pageset.url.lstrip("/"))
        return _url_builder(scheme, hostname, path)

    def build(self, request, pageset, hostname=None):
        if is_pageset(pageset):
            return self.front_page_url(request, pageset, hostname=hostname)
        else:
            return self.feature_page_url(request, pageset, hostname=hostname)

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

def includeme(config):
    settings = config.registry.settings
    backend_url = settings.get('altaircms.backend.outer.url')
    if backend_url is None:
        logger.warning('altaircms.backend.outer.url is not given. using deprecated altaircms.backend.url instead')
        backend_url = settings.get('altaircms.backend.url')

    config.registry.registerUtility(
        CMSPageURLAdapter(),
        ICMSPageURLAdapter
        )
    config.registry.registerUtility(
        BackendPageURLAdapter(backend_url),
        IBackendPageURLAdapter
        )
    config.registry.registerUtility(
        CartPageURLAdapter(),
        ICartPageURLAdapter
        )
    config.registry.registerUtility(
        MobilePageURLAdapter(),
        ICMSMobilePageURLAdapter
        )
    config.registry.registerUtility(
        SmartphonePageURLAdapter(),
        ICMSSmartphonePageURLAdapter
        )
    config.registry.registerUtility(
        UsersitePageURLAdapter(),
        ICMSPCPageURLAdapter
        )

