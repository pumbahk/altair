# -*- coding:utf-8 -*-

import os
import logging
from datetime import datetime
from time import mktime
from email.utils import formatdate
from sqlalchemy.orm import joinedload
from altair.mobile.interfaces import IMobileRequest

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
                response.content_type.startswith("text/css")):
            response.headers['Pragma'] = "no-cache"
            response.headers['Cache-Control'] = "no-cache,no-store"
            response.headers['Expires'] = formatdate(mktime(datetime.now().timetuple()), localtime=False)

        return response

class OrganizationPathTween(object):
    def __init__(self, handler, registry):
        self.handler = handler
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

    def __call__(self, request):
        # もしパスつきのHostドメインだったら
        hosts = self.get_hosts(request)
        if not hosts:
            return self.handler(request)

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

        request.organization = host.organization
        request.altair_host = host_chosen
        return self.handler(request)
