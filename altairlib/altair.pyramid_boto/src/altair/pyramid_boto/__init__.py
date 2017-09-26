from pyramid.exceptions import ConfigurationError
from .interfaces import IS3ConnectionFactory
from .s3.connection import DefaultS3ConnectionFactory

CONFIG_PREFIXES = ('altair.s3', 's3',)


def newDefaultS3ConnectionFactory(config):
    """
    use:
    altair.s3.access_key
    altair.s3.secret_key
    s3.access_key
    s3.secret_key
    """
    for prefix in CONFIG_PREFIXES:
        access_key = config.registry.settings.get('%s.access_key' % prefix)
        if access_key is not None:
            options = {'access_key': access_key}
            for key in ('secret_key', 'host', 'path'):
                value = config.registry.settings.get('%s.%s' % (prefix, key))
                if value is not None:
                    options[key] = value
            try:
                return DefaultS3ConnectionFactory(**options)
            except:
                pass
    return None


def includeme(config):
    factory = newDefaultS3ConnectionFactory(config)
    if factory is not None:
        config.registry.registerUtility(
            factory,
            IS3ConnectionFactory)
