from .s3 import IS3ConnectionFactory, newDefaultS3ConnectionFactory

def register_default_implementations(config):
    config.registry.registerUtility(
        newDefaultS3ConnectionFactory(config),
        IS3ConnectionFactory)

