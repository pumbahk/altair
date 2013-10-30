# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

from zope.interface import (
    Interface,
    implementer,
    provider,
    providedBy
)
from beaker.cache import Cache
from pyramid.response import Response
from ..tracking import ITrackingImageGenerator
from altair.preview.api import get_preview_request_condition
from pyramid.interfaces import IDict

class ICacheTweensSetting(IDict):
    pass
    # expired_at = Attribute("expired")

class IFrontPageCache(Interface):
    def get(request, k):
        pass
    def set(request, k, v):
        pass

class ICacheKeyGenerator(Interface):
    def __call__(request):
        pass

class ICacheValueMutator(Interface):
    def __call__(request, v):
        pass


@implementer(IFrontPageCache)
class OnMemoryFrontPageCacher(object):
    def __init__(self):
        self.cache = {}

    def get(self, request, k):
        return self.cache.get(k)

    def set(self, request, k, v):
        self.cache[k] = v

@implementer(IFrontPageCache)
class FrontPageCacher(object):
    def __init__(self, kwargs):
        self.cache = Cache._get_cache("frontpage", kwargs)

    def clear_cache(self, k):
        try:
            self.cache.remove_value(k)
        except (ValueError, EOFError): #insecure string
            logger.warn("clear_cache: k={k} insecure string found. front page remove".format(k=k))
            handler = self.cache._get_value(k).namespace
            handler.do_remove()
        except Exception as e:
            logger.error(repr(e))
            logger.warn("clear_cache: k={k} insecure string found. remove".format(k=k))
            handler = self.cache._get_value(k).namespace
            handler.do_remove()
 
    def get(self, request, k):
        try:
            return self.cache[k]
        except KeyError as e:
            return None
        except (ValueError, EOFError) as e:
            logger.warn(repr(e))
            self.clear_cache(k)
            return None

    def set(self, request, k, v):
        try:
            self.cache[k] = v
        except (KeyError, ValueError, EOFError) as e:
            logger.warn(repr(e))
            self.clear_cache(k)

@implementer(IFrontPageCache)
class WrappedFrontPageCache(object):
    def __init__(self, cache, mutator):
        self.cache = cache
        self.mutator = mutator

    def get(self, request, k):
        v = self.cache.get(request, k)
        if v is None:
            return None
        return self.mutator(request, v)

    def set(self, request, k, v):
        self.cache.set(request, k, v)

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

def get_key_generator(request):
    return request.registry.adapters.lookup([providedBy(request)], ICacheKeyGenerator)
import logging
logger = logging.getLogger(__name__)

def cached_view_tween(handler, registry):
    local_settings = registry.queryUtility(ICacheTweensSetting)
    max_age = None
    if local_settings is None:
        logger.warn("ICacheTweensSettings is not found")
    else:
        max_age = local_settings.get("expire")

    def tween(request):
        ## getかpreviewリクエストの時はcacheしない
        if request.method != "GET":
            return handler(request)

        # logger.debug("req:"+request.path)
        if get_preview_request_condition(request):
            return handler(request)

        keygen = get_key_generator(request)
        k = keygen(request)
        cache = registry.getUtility(IFrontPageCache)
        v = cache.get(request, k)
        if v:
            response = Response(v)
            if max_age:
                response.cache_control.max_age = max_age
            return response
        else:
            ## cacheするのはhtmlだけ(テキストだけ)
            response = handler(request)
            content_type = response.content_type
            app_cands = ("application/json", "application/javascript", "application/xhtml+xml")
            if content_type.startswith("text/") or any(content_type == x for x in app_cands):
                # logger.debug("cache:"+request.path)
                cache.set(request, k, response.body)
                if max_age:
                    response.cache_control.max_age = max_age
            return response
    return tween
