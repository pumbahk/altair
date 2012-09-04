# -*- coding:utf-8 -*-
from datetime import datetime
from time import mktime
from email.utils import formatdate

class CacheControlTween(object):
    def __init__(self, handler, registry):
        self.handler = handler
        self.registry = registry

    def __call__(self, request):
        response = self.handler(request)
        if response.content_type and (
                response.content_type.startswith("text/") or \
                response.content_type == "application/javascript"):
            response.headers['Pragma'] = "no-cache"
            response.headers['Cache-Control'] = "no-cache,no-store"
            response.headers['Expires'] = formatdate(mktime(datetime.now().timetuple()), localtime=False)

        return response

