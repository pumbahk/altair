from mako.util import LRUCache
import logging
logger = logging.getLogger()

def refresh_template_cache(template):
    logger.warn("*debug *refresh template cache (last_modified={1}, uri={0})".format(template.uri, template.last_modified))
    lookup = template.lookup
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
