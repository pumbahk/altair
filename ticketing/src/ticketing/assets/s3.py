from pyramid.interfaces import IAssetDescriptor
from pyramid.path import Resolver, AssetResolver
from boto.s3.connection import S3Connection
from boto.s3.key import Key as S3Key
from boto.s3.prefix import Prefix as S3Prefix
from zope.interface import Interface, implementer, directlyProvides
from zope.interface.verify import verifyObject
from cStringIO import StringIO
from urlparse import urlparse
import re
from .interfaces import IAssetResolver
from ..pyramid_boto.interfaces import IS3ConnectionFactory
from beaker.cache import Cache, CacheManager

def normalize_prefix(prefix, delimiter):
    return delimiter.join(c for c in prefix.split(delimiter) if c)

cache_manager = CacheManager()

class IS3RetrieverFactory(Interface):
    def __call__(bucket, delimiter):
        pass

@implementer(IS3RetrieverFactory)
class DefaultS3RetrieverFactory(object):
    def __init__(self, cache_region=None):
        if cache_region is not None:
            self.entry_cache = self.cache_manager.get_cache_region(__name__ + '.entry', cache_region)
            self.object_cache = self.cache_manager.get_cache_region(__name__ + '.object', cache_region)
        else:
            self.entry_cache = None
            self.object_cache = None

    def __call__(self, bucket, delimiter):
        return S3Retriever(bucket, delimiter,
            entry_cache=self.entry_cache, object_cache=self.object_cache)

def newDefaultS3RetrieverFactory(config):
    return DefaultS3RetrieverFactory(config.registry.settings.get(__name__ + '.cache_region'))

class S3Retriever(object):
    def __init__(self, bucket, delimiter, entry_cache=None, object_cache=None):
        self.bucket = bucket
        self.delimiter = delimiter
        self.key_cache = {}
        self.entry_cache = entry_cache or Cache(__name__ + '.entry', type='memory', expire=3600)
        self.object_cache = object_cache or Cache(__name__ + '.object', type='memory', expire=3600)

    def get_key(self, key_or_prefix):
        retval = self.key_cache.get(key_or_prefix)
        if retval is None:
            retval = S3Key(self.bucket)
            retval.key = key_or_prefix
            self.key_cache[key_or_prefix] = retval
        return retval

    def get_entry(self, key_or_prefix):
        return self.entry_cache.get(key_or_prefix, createfunc=lambda:self._fetch_entry(key_or_prefix))

    def _fetch_entry(self, key_or_prefix):
        everything_right_under_prefix = list(self.bucket.list(key_or_prefix, delimiter=self.delimiter))
        if len(everything_right_under_prefix) == 1 and \
                isinstance(everything_right_under_prefix[0], S3Prefix):
            canonicalized_key_or_prefix = key_or_prefix + self.delimiter
            everything_right_under_prefix = list(self.bucket.list(canonicalized_key_or_prefix, delimiter=self.delimiter))
        else:
            canonicalized_key_or_prefix = key_or_prefix
            if not everything_right_under_prefix:
                everything_right_under_prefix = None

        if everything_right_under_prefix is None:
            keys_under_prefix = None
        else:
            if len(everything_right_under_prefix) == 1 and \
                    everything_right_under_prefix[0].key == key_or_prefix:
                keys_under_prefix = False
            else:
                for key in everything_right_under_prefix:
                    self.key_cache.setdefault(key.key, key)
                keys_under_prefix = [
                    key.key.rpartition(self.delimiter)[2] \
                    for key in everything_right_under_prefix \
                    if key.key != canonicalized_key_or_prefix\
                    ]
        return {
            'key_or_prefix': key_or_prefix,
            'canonicalized_key_or_prefix': canonicalized_key_or_prefix,
            'keys_under_prefix': keys_under_prefix,
            }

    def _fetch_object(self, key):
        key_obj = self.get_key(key)
        return key_obj.get_contents_as_string()

    def get_object(self, key):
        return self.object_cache.get(key, createfunc=lambda:self._fetch_object(key))

@implementer(IAssetDescriptor)
class S3AssetDescriptor(object):
    def __init__(self, retriever, key_or_prefix):
        self.retriever = retriever
        self.key_or_prefix = key_or_prefix

    def absspec(self):
        raise NotImplementedError

    def abspath(self):
        return u's3://%s/%s' % (self.retriever.bucket, self.key_or_prefix.replace(self.delimiter, u'/'))

    def stream(self):
        return StringIO(self.retriever.get_object(self.key_or_prefix))

    def isdir(self):
        entry = self.retriever.get_entry(self.key_or_prefix)
        return bool(entry['keys_under_prefix'])

    def listdir(self):
        entry = self.retriever.get_entry(self.key_or_prefix)
        if entry['keys_under_prefix'] is None:
            raise OSError(2, 'No such prefix', entry['canonicalized_key_or_prefix'])
        elif entry['keys_under_prefix'] is False:
            raise OSError(20, 'Not a directory', entry['canonicalized_key_or_prefix'])
        return list(entry['keys_under_prefix'])

    def exists(self):
        entry = self.retriever.get_entry(self.key_or_prefix)
        return entry['keys_under_prefix'] is not None
 
@implementer(IAssetResolver)
class S3AssetResolver(object):
    def __init__(self, connection, retriever_factory, parent=None, delimiter=u'/'):
        if parent is None:
            parent = AssetResolver()
            directlyProvides(parent, IAssetResolver)
        assert isinstance(connection, S3Connection)
        assert verifyObject(IS3RetrieverFactory, retriever_factory)
        assert parent is None or verifyObject(IAssetResolver, parent)
        self.connection = connection
        self.retriever_factory = retriever_factory
        self.retr_cache = {}
        self.parent = parent
        self.delimiter = delimiter

    def get_retriever(self, bucket_name):
        retr = self.retr_cache.get(bucket_name)
        if retr is None:
            retr = self.retriever_factory(self.connection.get_bucket(bucket_name), self.delimiter)
            self.retr_cache[bucket_name] = retr
        return retr

    def resolve(self, spec):
        url = urlparse(spec)
        if url.scheme != u's3':
            if self.parent is not None:
                return self.parent.resolve(spec)
            else:
                return ValueError(spec)
        return S3AssetDescriptor(
            retriever=self.get_retriever(url.netloc),
            key_or_prefix=normalize_prefix(
                url.path[int(url.path[0:1] == u'/'):].replace(u'/', self.delimiter), self.delimiter)
            )

