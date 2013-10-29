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

def cached_view_tween(handler, registry):
    def tween(request):
        if request.method != "GET":
            return handler(request)

        keygen = get_key_generator(request)
        k = keygen(request)
        cache = registry.getUtility(IFrontPageCache)
        v = cache.get(request, k)
        if v:
            return Response(v)
        else:
            response = handler(request)
            cache.set(request, k, response.text)
            return response
    return tween
