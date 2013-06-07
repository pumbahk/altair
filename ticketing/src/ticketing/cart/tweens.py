# encoding: utf-8

import logging
from datetime import datetime
from time import mktime, time
from email.utils import formatdate
from sqlalchemy.orm import joinedload

logger = logging.getLogger(__name__)

class CartRequestProperties(object):
    def __init__(self, registry):
        self.registry = registry

    def get_hosts(self, request):
        from ticketing.core.models import Host, Organization
        hosts = Host.query \
            .options(joinedload(
                Host.organization,
                Organization.settings
                )) \
            .filter(Host.host_name==unicode(request.host)).all()
        return list(reversed(sorted(hosts, key=lambda h: h.path)))

    def get_host(self, request):
        # もしパスつきのHostドメインだったら
        hosts = self.get_hosts(request)
        host_chosen = None 
        for host in hosts:
            if not host.path:
                host_chosen = host
            else:
                # そのパスであるか request 判定して
                if request.path_info.startswith(host.path):
                    # script_nameにずらす
                    (script_name, path_info) = (request.script_name 
                                                + request.path_info[:len(host.path)], 
                                                request.path_info[len(host.path):])
                    logger.debug("{0} {1}".format(script_name, path_info))
                    request.script_name = script_name
                    request.path_info = path_info
                    host_chosen = host

        return host_chosen

    def get_organization(self, request):
        return request.altair_host and request.altair_host.organization

def altair_host_tween_factory(handler, registry):
    request_properties = CartRequestProperties(registry) 
    def tween(request):
        request.set_property(request_properties.get_host, 'altair_host', reify=True)
        request.set_property(request_properties.get_organization, 'organization', reify=True)
        return handler(request)
    return tween

def response_time_tween_factory(handler, registry):
    def _tween(request):
        start = time()
        try:
            return handler(request)
        finally:
            end = time()
            logger.info("request handled in %g sec" % (end - start))
    return _tween
