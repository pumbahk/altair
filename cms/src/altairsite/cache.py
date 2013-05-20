from zope.interface import Interface
from zope.interface import provider
from dogpile.cache.api import CacheBackend, NO_VALUE
import logging
logger = logging.getLogger()

class NullCacheBackend(CacheBackend):
    def __init__(self, arguments):
        pass

    def get(self, key):
        logger.debug("*cache* get key={0}".format(key))
        return NO_VALUE

    def set(self, key, value):
        logger.debug("*cache* set key={0}, value={1}".format(key, value))
        pass

    def delete(self, key):
        logger.debug("*cache* delete key={0}".format(key))
        pass

class ICacheRegion(Interface):
    def get(key, expiration_time=None, ignore_expiration=False):
        pass
    def get_or_create(key, creator, expiration_time=None, should_cache_fn=None):
        pass
    def set(key, value):
        pass
    def delete(key):
        pass
    def cache_on_arguments(namespace=None, expiration_time=None, should_cache_fn=None):
        pass


def set_cache_region(config, region, name=""):
    config.registry.registerUtility(provider(ICacheRegion)(region), ICacheRegion, name=name)

def get_cache_region(request, name=""):
    return request.registry.queryUtility(ICacheRegion, name=name)
