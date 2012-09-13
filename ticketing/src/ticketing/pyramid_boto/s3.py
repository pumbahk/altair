from zope.interface import implementer
from boto.s3.connection import S3Connection
from .interfaces import IS3ConnectionFactory

CONFIG_PREFIXES = ('s3_asset_resolver', 's3')

def newDefaultS3ConnectionFactory(config):
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
