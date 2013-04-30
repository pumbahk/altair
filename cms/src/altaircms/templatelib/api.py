from mako.util import LRUCache
import logging
from functools import partial
logger = logging.getLogger()
from . import create_adjusted_name

def refresh_template_cache(template):
    logger.warn("*debug *refresh template cache (last_modified={1}, uri={0})".format(template.uri, template.last_modified))
    lookup = template.lookup
    return refresh_template_cache_lookup(lookup)

def refresh_template_cache_lookup(lookup):
    if lookup is None:
        return
    collection_size = lookup.collection_size
    ## from mako.lookup.TemplateLookup.__init__
    lookup._mutex.acquire()
    if collection_size == -1:
        lookup._collection = {}
        lookup._uri_cache = {}
    else:
        lookup._collection = LRUCache(collection_size)
        lookup._uri_cache = LRUCache(collection_size)
    lookup._mutex.release()


def _del_cache(k, lookup):
    if k in lookup._collection:
        del lookup._collection[k]
        logger.warn("*debug del collection: {0}".format(k))
    if k in lookup._uri_cache:
        del lookup._uri_cache[k]
        logger.warn("*debug del uri_cache: {0}".format(k))

def refresh_template_cache_only_needs(template, target_uri):
    logger.warn("*debug *refresh template cache_only_needs (last_modified={1}, uri={0})".format(template.uri, template.last_modified))
    lookup = template.lookup
    return refresh_template_cache_only_needs_lookup(lookup, target_uri)
  
def refresh_template_cache_only_needs_lookup(lookup, target_uri):
    if lookup is None:
        return

    if not hasattr(lookup, "add_event"):
        logger.warn("lookup has not _events. lookup={0}".format(lookup))
        return 

    for k in target_uri:
        lookup.add_event(k, partial(_del_cache, create_adjusted_name(k)))
    logger.warn("*debug *refresh_template_cache,  target_uri={0}".format(target_uri))
