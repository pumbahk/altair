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
        if v is None or not isinstance(v, dict):
            return None
        response = Response(
            body=v['body'],
            content_type=v['content_type'],
            charset=v['charset']
            )
        return self.mutator(request, response)

    def set(self, request, k, response):
        self.cache.set(k, dict(
            body=response.body,
            content_type=response.content_type,
            charset=response.charset
            ))

@implementer(ICacheKeyGenerator)
class CacheKeyGenerator(object):
    def __init__(self, prefix):
        self.prefix = prefix

    def __call__(self, request):
        return self.prefix+request.url

@provider(ICacheValueMutator)
def update_browser_id(request, response):
    gen = request.registry.getUtility(ITrackingImageGenerator)
    response.text = gen.replace(request, response.text)
    return response


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
        nocache = False
        if request.method != "GET":
            nocache = True
        else:
            try:
                nocache = "_nocache" in request.GET
            except UnicodeDecodeError:
                pass 

            if get_preview_request_condition(request):
                nocache = True

        if nocache:
            return handler(request)

        keygen = get_key_generator(request)
        k = keygen(request)
        cache = registry.getUtility(IFrontPageCache)

        if atomic.is_requesting(k):
            logger.warn("cache: requesting another process. '{k}'".format(k=k))
            return handler(request)

        response = cache.get(request, k)
        if response is not None:
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
                    cache.set(request, k, response)
                    if max_age:
                        response.cache_control.max_age = max_age
                return response
    return tween
