# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from datetime import datetime
import contextlib

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


def clear_cache(cache, k):
    try:
        cache.remove_value(k)
    except (ValueError, EOFError): #insecure string
        logger.warn("clear_cache: k={k} insecure string found. front page remove".format(k=k))
        handler = cache._get_value(k).namespace
        handler.do_remove()
    except Exception as e:
        logger.error(repr(e))
        logger.warn("clear_cache: k={k} insecure string found. remove".format(k=k))
        handler = cache._get_value(k).namespace
        handler.do_remove()

@implementer(IFrontPageCache)
class FrontPageCacher(object):
    k = "page"
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def get(self, request, k):
        try:
            cache = Cache._get_cache(k, self.kwargs)
            return cache[self.k]
        except KeyError as e:
            return None
        except (ValueError, EOFError) as e:
            logger.warn(repr(e))
            clear_cache(cache, self.k)
            return None

    def set(self, request, k, v):
        try:
            cache = Cache._get_cache(k, self.kwargs)
            cache[self.k] = v
        except (KeyError, ValueError, EOFError) as e:
            logger.warn(repr(e))
            clear_cache(cache, self.k)

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

# todo:rename
class DummyAtomic(object):
    def is_requesting(self, k):
        return False

    @contextlib.contextmanager
    def atomic(self, k):
        yield

class ForAtomic(object):
    k = "fetching"
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def is_requesting(self, k):
        fetching = Cache._get_cache(k, self.kwargs)
        return "fethcing" in fetching

    def start_requsting(self, k):
        try:
            fetching = Cache._get_cache(k, self.kwargs)
            fetching[self.k] = datetime.now()
        except (KeyError, ValueError, EOFError) as e:
            logger.warn(repr(e))
            clear_cache(fetching, self.k)

    def end_requesting(self, k):
        fetching = Cache._get_cache(k, self.kwargs)
        clear_cache(fetching, self.k)

    @contextlib.contextmanager
    def atomic(self, k):
        try:
            self.start_requsting(k)
            yield
        finally:
            self.end_requesting(k)


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
        ## getかpreviewリクエストの時はcacheしない
        if request.method != "GET":
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
                app_cands = ("application/json", "application/javascript", "application/xhtml+xml")
                if content_type.startswith("text/") or any(content_type == x for x in app_cands):
                    # logger.debug("cache:"+request.path)
                    cache.set(request, k, response.body)
                    if max_age:
                        response.cache_control.max_age = max_age
                return response
    return tween
