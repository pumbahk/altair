from pyramid.exceptions import ConfigurationError
from .interfaces import IS3ConnectionFactory
from .s3.connection import DefaultS3ConnectionFactory

CONFIG_PREFIXES = ('altair.s3', 's3',)

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

def includeme(config):
    factory = newDefaultS3ConnectionFactory(config)
    if factory is not None:
        config.registry.registerUtility(
            factory,
            IS3ConnectionFactory)
