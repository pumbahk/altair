# -*- coding:utf-8 -*-
import sqlalchemy as sa
import urllib
from urlparse import ParseResult, urlparse
import hashlib
import logging
logger = logging.getLogger(__name__)

from zope.interface import implementer
from .interfaces import IURLBuilder
from altair.app.ticketing.core.models import Host
from altair.app.ticketing.payments.plugins import QR_DELIVERY_PLUGIN_ID
from altair.app.ticketing.skidata.utils import get_hash_from_barcode_data

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
    qs = qs.filter(sa.not_(Host.host_name.like("elbtest-%")))
    if "service" in url:
        host = qs.filter(Host.host_name.like("%.tstar.jp")).first()
    elif ".tstar.jp" in url:
        host = qs.filter(Host.host_name.like("%.tstar.jp")).first()
    elif "stg" in url:
        host = qs.filter(Host.host_name.like("%stg%")).first()
    elif "rta" in url:
        host = qs.filter(Host.host_name.like("%rta%")).first()
    elif "fmz" in url:
        host = qs.filter(Host.host_name.like("%fmz%")).first()
    elif "dev" in url:
        host = qs.filter(Host.host_name.like("%dev%")).first()
    else:
        host = qs.filter(Host.host_name.like("%stg%")).first()
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

    def build(self, request, cart_url, event_id=None):
        parsed = urlparse(cart_url)
        scheme = parsed.scheme
        hostname = self.build_hostname(parsed)
        path = self.path_prefix
        return _url_builder(scheme, hostname, path, {"redirect_to": cart_url, "backend_event_id": event_id})

@implementer(IURLBuilder)
class CartURLEventsBuilder(object):
    def __init__(self, path_prefix):
        self.path_prefix = path_prefix.rstrip("/")

    def build_path(self, event):
        suffix = unicode(event.id)
        return u"{0}/{1}".format(self.path_prefix, suffix.lstrip("/"))

    def build_hostname(self, request, organization):
        return guess_host_name_from_request(request, organization=organization)    

    def build_query(self, performance):
        query = {}
        if performance:
            query["performance"] = performance.id
        return query

    def build(self, request, event, performance=None, organization=None):
        organization = organization or request.context.organization
        scheme = _get_scheme_from_request(request)
        host_name = self.build_hostname(request, organization)
        path = self.build_path(event)
        query = self.build_query(performance)
        return _url_builder(scheme, host_name, path, query)

@implementer(IURLBuilder)
class CartURLPerformanceBuilder(object):
    def __init__(self, path_prefix):
        self.path_prefix = path_prefix.rstrip("/")

    def build_path(self, performance):
        suffix = unicode(performance.id)
        return u"{0}/{1}".format(self.path_prefix, suffix.lstrip("/"))

    def build_hostname(self, request, organization):
        return guess_host_name_from_request(request, organization=organization)

    def build(self, request, performance, organization=None):
        organization = organization or request.context.organization
        scheme = _get_scheme_from_request(request)
        host_name = self.build_hostname(request, organization)
        path = self.build_path(performance)
        return _url_builder(scheme, host_name, path, {})


@implementer(IURLBuilder)
class SpaCartURLPerformanceBuilder(object):
    def __init__(self, path_prefix):
        self.path_prefix = path_prefix.rstrip("/")

    def build_path(self, performance):
        suffix = unicode(performance.id)
        return u"{0}/{1}".format(self.path_prefix, suffix.lstrip("/"))

    def build_hostname(self, request, organization):
        return guess_host_name_from_request(request, organization=organization)

    def build(self, request, performance, organization=None):
        organization = organization or request.context.organization
        scheme = _get_scheme_from_request(request)
        host_name = self.build_hostname(request, organization)
        path = self.build_path(performance)
        return _url_builder(scheme, host_name, path, {})


@implementer(IURLBuilder)
class LotsCartURLBuilder(object):
    def __init__(self, path_prefix):
        self.path_prefix = path_prefix.rstrip("/")

    def build_path(self, event, lot):
        suffix = unicode(event.id)
        lot_id = unicode(lot.id)
        return u"{0}/{1}/entry/{2}".format(self.path_prefix, suffix.lstrip("/"), lot_id)

    def build_hostname(self, request, organization):
        return guess_host_name_from_request(request, organization=organization)

    def build_query(self, performance):
        query = {}
        if performance:
            query["performance"] = performance.id
        return query

    def build(self, request, event, lot, performance=None, organization=None):
        organization = organization or request.context.organization
        scheme = _get_scheme_from_request(request)
        host_name = self.build_hostname(request, organization)
        path = self.build_path(event, lot)
        query = self.build_query(performance)
        return _url_builder(scheme, host_name, path, query)

@implementer(IURLBuilder)
class AgreementCartURLBuilder(object):
    def __init__(self, path_prefix):
        self.path_prefix = path_prefix.rstrip("/")

    def build_path(self, event):
        suffix = unicode(event.id)
        return u"{0}/{1}/agreement".format(self.path_prefix, suffix.lstrip("/"))

    def build_hostname(self, request, organization):
        return guess_host_name_from_request(request, organization=organization)

    def build_query(self, performance):
        query = {}
        if performance:
            query["performance"] = performance.id
        return query

    def build(self, request, event, performance=None, organization=None):
        organization = organization or request.context.organization
        scheme = _get_scheme_from_request(request)
        host_name = self.build_hostname(request, organization)
        path = self.build_path(event)
        query = self.build_query(performance)
        return _url_builder(scheme, host_name, path, query)

@implementer(IURLBuilder)
class AgreementLotsCartURLBuilder(object):
    def __init__(self, path_prefix):
        self.path_prefix = path_prefix.rstrip("/")

    def build_path(self, event, lot):
        suffix = unicode(event.id)
        lot_id = unicode(lot.id)
        return u"{0}/{1}/entry/{2}/agreement".format(self.path_prefix, suffix.lstrip("/"), lot_id)

    def build_hostname(self, request, organization):
        return guess_host_name_from_request(request, organization=organization)

    def build_query(self, performance):
        query = {}
        if performance:
            query["performance"] = performance.id
        return query

    def build(self, request, event, lot, performance=None, organization=None):
        organization = organization or request.context.organization
        scheme = _get_scheme_from_request(request)
        host_name = self.build_hostname(request, organization)
        path = self.build_path(event, lot)
        query = self.build_query(performance)
        return _url_builder(scheme, host_name, path, query)

@implementer(IURLBuilder)
class OrderReviewQRURLBuilder(object):
    def __init__(self, path_prefix):
        self.path_prefix = path_prefix.rstrip("/")

    def build_path(self, ticket_id, sign, qr_type):
        if qr_type == QR_DELIVERY_PLUGIN_ID:
            return u"{0}/qr/{1}/{2}/".format(self.path_prefix, ticket_id, sign)
        else:
            return u"{0}/qr_aes/{1}/".format(self.path_prefix, sign)

    def build_hostname(self, request, organization):
        return guess_host_name_from_request(request, organization=organization)

    def build(self, request, ticket, organization=None, qr_type=QR_DELIVERY_PLUGIN_ID):
        organization = organization or request.context.organization
        scheme = _get_scheme_from_request(request)
        host_name = self.build_hostname(request, organization)
        path = self.build_path(ticket.id, ticket.sign, qr_type)
        return _url_builder(scheme, host_name, path, {})


@implementer(IURLBuilder)
class OrderReviewSkidataQRURLBuilder(object):
    def __init__(self, path_prefix):
        self.path_prefix = path_prefix.rstrip("/")

    def build_path(self, skidata_barcode):
        return u'{0}/qr_ticket/{1}/{2}'.format(self.path_prefix, skidata_barcode.id,
                                               get_hash_from_barcode_data(skidata_barcode.data))

    def build_hostname(self, request, organization):
        return guess_host_name_from_request(request, organization=organization)

    def build(self, request, skidata_barcode, organization=None):
        organization = organization or request.context.organization
        scheme = _get_scheme_from_request(request)
        host_name = self.build_hostname(request, organization)
        path = self.build_path(skidata_barcode)
        return _url_builder(scheme, host_name, path, {})
