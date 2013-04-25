from zope.interface import implementer
from boto.s3.connection import S3Connection
from ..interfaces import IS3ConnectionFactory
from ..interfaces import IS3ContentsUploader
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

@implementer(IS3ContentsUploader)
class DefaultS3Uploader(object):
    OPTIONS = ("public", )
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

    def _treat_options(self, k):
        options = {}
        if self.options.get("public", False):
            options["policy"] = "public-read"
        return options

    def _force_upload(self, content, name, setter):
        k = Key(self.bucket)
        k.key = name
        options = self._treat_options(k)
        return setter(k, content, options)

    def _upload(self, content, name, setter, overwrite=False):
        if overwrite:
            return self._force_upload(content, name, setter)
        else:
            logger.warn("DefaultS3Uploader.upload(overwrite=False) is not implemented")
            return self._force_upload(content, name, setter)

    def upload_string(self, content, name, overwrite=False):        
        return self._upload(content, name, lambda k, content, options: k.set_contents_from_string(content, **options))

    def upload_file(self, content, name, overwrite=False):        
        return self._upload(content, name, lambda k, content, options: k.set_contents_from_file(content, **options))
    upload = upload_file

    def delete(self, content, name):
        k = Key(self.bucket)
        k.key = name
        self.bucket.delete_key(k)

    def unpublish(self, name, check=True):
        k = Key(self.bucket)
        k.key = name
        if not check:
            k.set_canned_acl("private")
        elif k.exists():
            k.set_canned_acl("private")

