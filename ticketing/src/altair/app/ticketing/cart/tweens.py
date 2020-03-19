# -*- coding:utf-8 -*-

import os
import logging
from datetime import datetime
from time import mktime, time
from email.utils import formatdate
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.session import make_transient
from pyramid.httpexceptions import HTTPFound
from altair.sqlahelper import get_db_session
from altair.app.ticketing.payments.exceptions import PaymentPluginException
from .exceptions import PaymentError

logger = logging.getLogger(__name__)

class CacheControlTween(object):
    def __init__(self, handler, registry):
        self.handler = handler
        self.registry = registry

    def __call__(self, request):
        response = self.handler(request)
        if not response.content_type:
            return response

        if (response.content_type.startswith("text/") or \
            response.content_type.startswith("application/xhtml+xml") or \
            response.content_type.startswith("application/json")) and \
           not (response.content_type.startswith("application/javascript") or
                response.content_type.startswith("text/css")) and \
           'Cache-Control' not in response.headers and \
           'Expires' not in response.headers:
            response.headers['Pragma'] = "no-cache"
            response.headers['Cache-Control'] = "no-cache,no-store"
            response.headers['Expires'] = formatdate(mktime(datetime.now().timetuple()), localtime=False)

        return response

class OrganizationPathTween(object):
    def __init__(self, handler, registry):
        self.handler = handler
        self.registry = registry

    def get_hosts(self, request):
        from altair.app.ticketing.core.models import Host, Organization
        session = get_db_session(request, 'slave')
        hosts = session.query(Host) \
            .options(
                joinedload(Host.organization),
                joinedload(Host.organization,
                           Organization.settings)) \
            .filter(Host.host_name==unicode(request.host)).all()
        return list(reversed(sorted(hosts, key=lambda h: h.path)))

    def __call__(self, request):
        from .request import ENV_ORGANIZATION_ID_KEY, ENV_ORGANIZATION_PATH_KEY
        # もしパスつきのHostドメインだったら
        hosts = self.get_hosts(request)
        if not hosts:
            return self.handler(request)

        try:
            for host in hosts:
                # そのパスであるか request 判定して
                if host.path is not None and request.path_info.startswith(host.path):
                    # script_nameにずらす
                    (script_name, path_info) = (request.script_name 
                                                + request.path_info[:len(host.path)], 
                                                request.path_info[len(host.path):])
                    request.script_name = script_name
                    request.path_info = path_info
                    break

            make_transient(host)
            make_transient(host.organization)
            request.altair_host_info = host
            request._resolved_organization = host.organization
            request.environ[ENV_ORGANIZATION_ID_KEY] = host.organization.id
            request.environ[ENV_ORGANIZATION_PATH_KEY] = host.path
        except:
            logger.exception('oops')
            raise
        return self.handler(request)

def response_time_tween_factory(handler, registry):
    def _tween(request):
        start = time()
        try:
            return handler(request)
        finally:
            end = time()
            logger.info("request handled in %g sec" % (end - start))
    return _tween

class PaymentPluginErrorConverterTween(object):
    def __init__(self, handler, registry):
        self.handler = handler
        self.registry = registry

    def __call__(self, request):
        try:
            return self.handler(request)
        except PaymentPluginException as e:
            if not e.ignorable:
                try:
                    logger.exception(u"PaymentPluginErrorConverterTween: {0}".format(unicode(e)))
                except (UnicodeDecodeError, UnicodeEncodeError):
                    logger.exception("oops")
            if e.back_url:
                return HTTPFound(location=e.back_url) 
            else:
                payment_error = PaymentError.from_resource(request.context, request, cause=e)
                # PGWレスポンスのerror_code
                payment_error.pgw_error_code = getattr(e, 'pgw_error_code', None)
                raise payment_error
