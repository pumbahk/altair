# -*- coding:utf-8 -*-

class CacheControlTween(object):
    def __init__(self, handler, registry):
        self.handler = handler
        self.registry = registry

    def __call__(self, request):
        response = self.handler(request)
        if response.content_type.startswith("text/"):
            response.headers['Cache-Control'] = "no-cache"
        return response

