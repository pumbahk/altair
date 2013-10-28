# -*- coding:utf-8 -*-
from zope.interface import Interface
from zope.interface import Attribute
from zope.interface import implementer
from beaker.cache import Cache
from pyramid.response import Response

class IFrontPageCache(Interface):
    cache = Attribute("cache")

@implementer(IFrontPageCache)
class FrontPageCacher(object):
    def __init__(self, kwargs):
        self.cache = Cache._get_cache("frontpage", kwargs)

    def __getitem__(self, k):
        try:
            return self.cache[k]
        except (KeyError, ValueError, EOFError):
            return None

    def __setitem__(self, k, v):
        self.cache[k] = v

def with_cached_view(prefix):
    def _with_cached_view(view):
        def wrapped(context, request):
            k = prefix+request.url
            cache = request.registry.getUtility(IFrontPageCache)
            v = cache[k]
            if v:
                return Response(v)
            else:
                response = view(context, request)
                cache[k] = response.text
                return response
        return wrapped
    return _with_cached_view

with_smartphone_cache = with_cached_view("S:")
with_mobile_cache = with_cached_view("M:")
with_pc_cache = with_cached_view("P:")
