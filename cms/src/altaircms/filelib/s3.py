from zope.interface import provider
from .interfaces import IS3UtilityFactory
from altair.pyramid_boto.s3.connection import DefaultS3ConnectionFactory
from altair.pyramid_boto.s3.connection import DefaultS3Uploader


def add_s3utility(config, factory):
    config.registry.registerUtility(factory, IS3UtilityFactory)

@provider(IS3UtilityFactory)
class S3ConnectionFactory(object):
    @classmethod
    def from_settings(cls, settings):
        access_key, secret_key = settings["s3.access_key"], settings["s3.secret_key"]
        bucket_name = settings["s3.bucket_name"]
        connection_factory = DefaultS3ConnectionFactory(access_key, secret_key)
        return DefaultS3Uploader(connection_factory, bucket_name)

@provider(IS3UtilityFactory)
class NullConnectionFactory(object):
    @classmethod
    def from_settings(cls, settings):
        return cls()
    
def includeme(config):
    config.add_directive("add_s3utility", add_s3utility)
