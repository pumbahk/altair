import os
from mako.util import LRUCache
import logging
from functools import partial
logger = logging.getLogger()
from . import create_adjusted_name

def refresh_template_cache(template):
    logger.info("*debug *refresh template cache (last_modified={1}, uri={0})".format(template.uri, template.last_modified))
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

def logical_delete_file(fname):
    "foo/bar.txt -> foo/.bar.txt"
    d, b = os.path.split(fname)
    dst = os.path.join(d, "."+b)
    logger.info("logical delete file: {0} -> {1}".format(fname, dst))
    if os.path.exists(fname):
        return os.rename(fname, dst)

def del_cache(k, discriptor, uploaded_at, lookup, deletefn=logical_delete_file):
    if discriptor.exists() and uploaded_at > os.stat(discriptor.abspath()).st_mtime:
        try:
            deletefn(discriptor.abspath())
        except Exception, e:
            logger.exception(str(e))

    if k in lookup._collection:
        del lookup._collection[k]
        logger.info("*debug del collection: {0}".format(k))
    if k in lookup._uri_cache:
        del lookup._uri_cache[k]
        logger.info("*debug del uri_cache: {0}".format(k))

def refresh_template_cache_only_needs(template, discriptors, uploaded_at):
    logger.info("*debug *refresh template cache_only_needs (last_modified={1}, uri={0}, uploaded_at={2})".format(
            template.uri, template.last_modified, uploaded_at))
    lookup = template.lookup
    return refresh_template_cache_only_needs_lookup(lookup, discriptors, uploaded_at)
  
def refresh_template_cache_only_needs_lookup(lookup, discriptors, uploaded_at):
    if lookup is None:
        return

    if not hasattr(lookup, "add_event"):
        logger.warn("lookup has not _events. lookup={0}".format(lookup))
        return 

    for d in discriptors:
        lookup.add_event(d.absspec(), partial(del_cache, create_adjusted_name(d.absspec()), d, uploaded_at))
    logger.info("*debug *refresh_template_cache,  discriptors={0}".format(discriptors))
