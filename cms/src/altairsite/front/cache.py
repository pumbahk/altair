# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

from zope.interface import (
    Interface,
    implementer,
    provider,
    providedBy
)
from pyramid.response import Response
from ..tracking import ITrackingImageGenerator
from altaircms.cachelib import (
    ICacheStore,
    DummyAtomic,
    ForAtomic,
    clear_cache,
    FileCacheStore, 
    OnMemoryCacheStore
)
from altair.preview.api import get_preview_request_condition
from pyramid.interfaces import IDict

class IFrontPageCache(ICacheStore):
    def get(request, k):
        pass
    def set(request, k, v):
        pass

class ICacheTweensSetting(IDict):
    pass
    # expired_at = Attribute("expired")

class ICacheKeyGenerator(Interface):
    def __call__(request):
        pass

class ICacheValueMutator(Interface):
    def __call__(request, v):
        pass

@implementer(IFrontPageCache)
class WrappedFrontPageCache(object):
    def __init__(self, cache, mutator):
        self.cache = cache
        self.mutator = mutator

    def get(self, request, k):
        v = self.cache.get(k)
        if v is None:
            return None
        return self.mutator(request, v)

    def set(self, request, k, v):
        self.cache.set(k, v)

@implementer(ICacheKeyGenerator)
class CacheKeyGenerator(object):
    def __init__(self, prefix):
        self.prefix = prefix

    def __call__(self, request):
        return self.prefix+request.url

@provider(ICacheValueMutator)
def update_browser_id(request, text):
    gen = request.registry.getUtility(ITrackingImageGenerator)
    return gen.replace(request, text)


## api
def get_key_generator(request):
    return request.registry.adapters.lookup([providedBy(request)], ICacheKeyGenerator)

def cached_view_tween(handler, registry):
    local_settings = registry.queryUtility(ICacheTweensSetting)
    if local_settings is None:
        logger.warn("ICacheTweensSettings is not found")
        max_age = None
        atomic = DummyAtomic() #xxx:
    else:
        max_age = local_settings.get("expire")
        atomic = ForAtomic(local_settings.get("kwargs"))


    def tween(request):
        ## get以外かpreviewリクエストの時はcacheしない
        if request.method != "GET":
            return handler(request)

        if "_nocache" in request.GET:
            return handler(request)

        # logger.debug("req:"+request.path)
        if get_preview_request_condition(request):
            return handler(request)

        keygen = get_key_generator(request)
        k = keygen(request)
        cache = registry.getUtility(IFrontPageCache)

        if atomic.is_requesting(k):
            logger.warn("cache: requesting another process. '{k}'".format(k=k))
            return handler(request)

        v = cache.get(request, k)
        if v:
            response = Response(v)
            if max_age:
                response.cache_control.max_age = max_age
            return response
        else:
            ## cacheするのはhtmlだけ(テキストだけ)
            if atomic.is_requesting(k):
                logger.warn("cache: requesting another process. '{k}'".format(k=k))
                return handler(request)
            with atomic.atomic(k):
                response = handler(request)
                content_type = response.content_type
                if response.status_int in (301, 302, 404, 500, 503):
                    return response
                app_cands = ("application/json", "application/javascript", "application/xhtml+xml")
                if content_type.startswith("text/") or any(content_type == x for x in app_cands):
                    # logger.debug("cache:"+request.path)
                    cache.set(request, k, response.body)
                    if max_age:
                        response.cache_control.max_age = max_age
                return response
    return tween
