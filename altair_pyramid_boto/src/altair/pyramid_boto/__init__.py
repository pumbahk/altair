from pyramid.exceptions import ConfigurationError
from .interfaces import IS3ConnectionFactory
from .s3.connection import newDefaultS3ConnectionFactory

def register_default_implementations(config):
    factory = newDefaultS3ConnectionFactory(config)
    if factory is not None:
        config.registry.registerUtility(
            factory,
            IS3ConnectionFactory)
