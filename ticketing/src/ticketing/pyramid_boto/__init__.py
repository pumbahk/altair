from pyramid.exceptions import ConfigurationError
from .s3 import IS3ConnectionFactory, newDefaultS3ConnectionFactory

def register_default_implementations(config):
    factory = newDefaultS3ConnectionFactory(config)
    if factory is None:
        raise ConfigurationError
    config.registry.registerUtility(
        factory,
        IS3ConnectionFactory)

