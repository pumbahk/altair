# -*- coding:utf-8 -*-
import urllib
from urlparse import ParseResult, urlparse
import logging
logger = logging.getLogger(__name__)

from zope.interface import implementer
from .interfaces import IURLBuilder
from ticketing.core.models import Host

def _url_builder(scheme, host_name, path, query_dict):
    query = urllib.urlencode(query_dict, True)
    url_builder = ParseResult(scheme=scheme, netloc=host_name, path=path, params="", query=query, fragment="")
    return url_builder.geturl()

def _get_scheme_from_request(request):
    return "https" if request.url.startswith("https") else "http"

def guess_host_name_from_request(request, organization=None):
    organization = organization or request.context.organization
    url = request.url
    ## too-addhoc
    qs = Host.query.filter(Host.organization_id==organization.id)
    if "service" in url:
        host = qs.filter(Host.host_name.like("%.tstar.jp")).first()
    elif "stg2" in url:
        host = qs.filter(Host.host_name.like("%stg2%")).first()
    elif "dev" in url:
        host = qs.filter(Host.host_name.like("%dev%")).first()
    else:
        host = qs.filter(Host.host_name.like("%stg2%")).first()
    if host is None:
        logger.warn("host is not found. organization={0}".format(organization))
        return ""
    return host.host_name

@implementer(IURLBuilder)
class CartNowURLBuilder(object):
    def __init__(self, path_prefix):
        self.path_prefix = path_prefix.rstrip("/")

    def build_hostname(self, parsed):
        return parsed.netloc

    def build(self, request, cart_url):
        parsed = urlparse(cart_url)
        scheme = parsed.scheme
        hostname = self.build_hostname(parsed)
        path = self.path_prefix
        return _url_builder(scheme, hostname, path, {"redirect_to": cart_url})

@implementer(IURLBuilder)
class CartURLBuilder(object):
    def __init__(self, path_prefix):
        self.path_prefix = path_prefix.rstrip("/")

    def build_path(self, event):
        suffix = unicode(event.id)
        return u"{0}/{1}".format(self.path_prefix, suffix.lstrip("/"))

    def build_hostname(self, request):
        organization = request.context.organization
        return guess_host_name_from_request(request, organization=organization)    

    def build_query(self, performance):
        query = {}
        if performance:
            query["performance"] = performance.id
        return query

    def build(self, request, event, performance=None):
        scheme = _get_scheme_from_request(request)
        host_name = self.build_hostname(request)
        path = self.build_path(event)
        query = self.build_query(performance)
        return _url_builder(scheme, host_name, path, query)
