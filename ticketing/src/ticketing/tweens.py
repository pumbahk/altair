# -*- coding:utf-8 -*-

import os
from datetime import datetime
from time import mktime
from email.utils import formatdate
import sqlahelper

def session_cleaner_factory(handler, registry):
    def tween(request):
        sqlahelper.get_session().remove()
        try:
            return handler(request)
        finally:
            sqlahelper.get_session().remove()
    return tween

class CacheControlTween(object):
    def __init__(self, handler, registry):
        self.handler = handler
        self.registry = registry

    def __call__(self, request):
        response = self.handler(request)
        if not response or not response.content_type:
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
