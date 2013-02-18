# -*- coding:utf-8 -*-

import os
import logging
from datetime import datetime
from time import mktime
from email.utils import formatdate

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
        from ticketing.core.models import Host
        hosts = Host.query.filter(Host.host_name==unicode(request.host)).all()
        return list(reversed(sorted(hosts, key=lambda h: h.path)))

    def __call__(self, request):
        # もしパスつきのHostドメインだったら
        hosts = self.get_hosts(request)
        if not hosts:
            return self.handler(request)

        for host in hosts:
            if not host.path:
                return self.handler(request)

            # そのパスであるか request 判定して
            if request.path_info.startswith(host.path):

                # script_nameにずらす
                (script_name, path_info) = (request.script_name 
                                            + request.path_info[:len(host.path)], 
                                            request.path_info[len(host.path):])
                logger.debug("{0} {1}".format(script_name, path_info))
                request.script_name = script_name
                request.path_info = path_info
                request.organization = host.organization
                request.environ['ticketing.cart.organization_id'] = host.organization.id
                request.environ['ticketing.cart.organization_path'] = host.path
                return self.handler(request)
        return self.handler(request)
        #raise Exception("%s %s" % (request.path_info, hosts))
