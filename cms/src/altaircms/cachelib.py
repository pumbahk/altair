# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from zope.interface import (
    Interface,
    implementer
)

from datetime import datetime
import contextlib
from beaker.cache import Cache

class ICacheStore(Interface):
    def get(k):
        pass

    def set(k, v):
        pass

    # not support dict interface.
    # because of get/set method catch Exception like a KeyError, internally.

class ICacheStoreRegistry(Interface):
    def add(k, cache):
        pass

    def lookup(request, k):
        pass

class IAtomic(Interface):
    def is_requesting(k):
        pass

    def atomic(k):
        pass

@implementer(ICacheStore)
class OnMemoryCacheStore(object):
    def __init__(self):
        self.cache = {}

    def get(self, k):
        return self.cache.get(k)

    def set(self, k, v):
        self.cache[k] = v

@implementer(ICacheStore)
class FileCacheStore(object):
    k = "data"
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def get_cache(self, k):
        return Cache._get_cache(k, self.kwargs)

    def get(self, k):
        try:
            cache = self.get_cache(k)
            return cache[self.k]
        except KeyError as e:
            logger.warn("cachelib {}:{}".format(repr(e), k))
            return None
        except (ValueError, EOFError) as e:
            logger.exception("cachelib {}:{}".format(repr(e), k))
            clear_cache(cache, self.k)
            return None

    def set(self, k, v):
        try:
            # logger.info("** set {}".format(k))
            cache = self.get_cache(k)
            cache[self.k] = v
        except (KeyError, ValueError, EOFError) as e:
            logger.exception("cachelib {}:{}".format(repr(e), k))
            clear_cache(cache, self.k)

def clear_cache(cache, k): #support file-cache only
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
        raise

# todo:rename
@implementer(IAtomic)
class DummyAtomic(object):
    def __init__(self, requesting=False):
        self.requesting = requesting
    def is_requesting(self, k):
        return self.requesting

    @contextlib.contextmanager
    def atomic(self, k):
        yield

@implementer(IAtomic)
class ForAtomic(object):
    k = "fetching"
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def get_cache(self, k):
        return Cache._get_cache(k, self.kwargs)

    def is_requesting(self, k):
        fetching = self.get_cache(k)
        return self.k in fetching

    def start_requesting(self, k):
        try:
            fetching = self.get_cache(k)
            fetching[self.k] = datetime.now()
        except (KeyError, ValueError, EOFError) as e:
            logger.warn(repr(e))
            clear_cache(fetching, self.k)

    def end_requesting(self, k):
        fetching = self.get_cache(k)
        clear_cache(fetching, self.k)

    @contextlib.contextmanager
    def atomic(self, k):
        try:
            self.start_requesting(k)
            yield
        finally:
            self.end_requesting(k)
