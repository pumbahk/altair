from zope.interface import implementer
from boto.s3.connection import S3Connection
from ..interfaces import IS3ConnectionFactory
from ..interfaces import IS3ContentsUploader
from boto.exception import S3ResponseError
from pyramid.decorator import reify
from boto.s3.key import Key
import logging
logger = logging.getLogger(__name__)

CONFIG_PREFIXES = ('s3_asset_resolver', 's3')

def newDefaultS3ConnectionFactory(config):
    """
    use:
    s3_asset_resolver.access_key
    s3_asset_resolver.secret_key
    s3.access_key
    s3.secret_key
    """
    options = {}
    for prefix in CONFIG_PREFIXES:
        for key in ('access_key', 'secret_key'):
            value = config.registry.settings.get('%s.%s' % (prefix, key))
            if value is not None and key not in options:
                options[key] = value
    try:
        return DefaultS3ConnectionFactory(**options)
    except:
        return None

@implementer(IS3ConnectionFactory)
class DefaultS3ConnectionFactory(object):
    def __init__(self, access_key, secret_key, **options):
        self.access_key = access_key
        self.secret_key = secret_key

    def __call__(self):
        return S3Connection(self.access_key, self.secret_key) 

class InvalidOption(Exception):
    pass

marker = object()
class Choice(object):
    __slots__ = ("xs", )
    def __init__(self, xs):
        self.xs = xs

    def get(self, k, default=None):
        for x in self.xs:
            v = x.get(k, marker)
            if marker != v:
                return v
        return default

@implementer(IS3ContentsUploader)
class DefaultS3Uploader(object):
    OPTIONS = ("public", "overwrite")
    def __init__(self, connection_factory, bucket_name, **options):
        self.options = options
        for o in options.keys():
            if not o in self.OPTIONS:
                raise InvalidOption(o)
        self.connection_factory = connection_factory
        self.bucket_name = bucket_name

    @reify
    def connection(self):
        return self.connection_factory()

    @reify
    def bucket(self):
        return self.connection.get_bucket(self.bucket_name)

    def is_reacheable(self):
        """health check"""
        try:
           self.bucket
           return True
        except S3ResponseError as e:
            return False

    def _treat_options(self, options):
        result = {}
        if options.get("public", False):
            result["policy"] = "public-read"
        return result

    def _force_upload(self, content, name, setter):
        k = Key(self.bucket)
        k.key = name
        return setter(k, content)

    def _upload(self, content, name, setter, overwrite=True):
        if overwrite:
            return self._force_upload(content, name, setter)
        else:
            logger.info("DefaultS3Uploader.upload(overwrite=False) is not implemented")
            return self._force_upload(content, name, setter)

    def upload_string(self, content, name, options={}):
        options = self._treat_options(Choice([options, self.options]))
        return self._upload(content, name, lambda k, content: k.set_contents_from_string(content, **options), 
                            overwrite=options.get("overwrite", True))

    def upload_file(self, content, name, options={}):        
        options = self._treat_options(Choice([options, self.options]))
        return self._upload(content, name, lambda k, content: k.set_contents_from_file(content, **options), 
                            overwrite=options.get("overwrite", True))
    upload = upload_file

    def delete(self, name):
        self.bucket.delete_key(name)

    def delete_items(self, names):
        self.bucket.delete_keys(names)

    def unpublish(self, name, check=False):
        k = Key(self.bucket)
        k.key = name
        if not check:
            k.set_canned_acl("private")
        elif k.exists():
            k.set_canned_acl("private")

    def unpublish_items(self, names, check=False):
        for name in names:
            self.unpublish(name, check=check)

    def publish(self, name, check=False):
        k = Key(self.bucket)
        k.key = name
        if not check:
            k.set_canned_acl("public-read")
        elif k.exists():
            k.set_canned_acl("public-read")

    def copy_items(self, src, dst, recursive=False, src_bucket_name=None):
        src_bucket_name = src_bucket_name or self.bucket.name
        bucket = self.bucket
        if not recursive:
            return bucket.copy_key(dst, src_bucket_name, src, preserve_acl=True)
        for k in bucket.list(src):
            bucket.copy_key(k.name.replace(src, dst, 1), src_bucket_name, k.name, preserve_acl=True)
        
