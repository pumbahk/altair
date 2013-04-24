from zope.interface import provider
from .interfaces import IS3UtilityFactory
from altair.pyramid_boto.s3.connection import DefaultS3ConnectionFactory
from altair.pyramid_boto.s3.connection import DefaultS3Uploader

import logging
logger = logging.getLogger(__name__)

def add_s3utility(config, factory):
    config.registry.registerUtility(factory, IS3UtilityFactory)
    if hasattr(factory, "add_subscribers"):
        factory.add_subscribers(config)

class AfterS3Upload(object):
    def __init__(self, request, session, files, uploader, extra_args):
        self.request = request
        self.session = session
        self.files = files
        self.uploader = uploader
        self.extra_args = extra_args

@provider(IS3UtilityFactory)
class S3ConnectionFactory(object):
    def __init__(self, uploader):
        self.uploader = uploader

    @classmethod
    def from_settings(cls, settings):
        access_key, secret_key = settings["s3.access_key"], settings["s3.secret_key"]
        bucket_name = settings["s3.bucket_name"]
        connection_factory = DefaultS3ConnectionFactory(access_key, secret_key)
        return cls(DefaultS3Uploader(connection_factory, bucket_name))

    def add_subscribers(self, config):
        config.add_subscriber(self.upload_s3_after_commit, "altaircms.filelib.adapts.AfterCommit")

    def upload_s3_after_commit(self, event):
        request = event.request
        result = event.result #{"create": [], "delete": [], "extra_args": []}
        session = event.session
        uploaded_files = []
        for f, realpath in result.get("create", []):
            with open(realpath) as rf:
                logger.warn("*debug upload: bucket={0} name={1}".format(self.uploader.bucket_name, f.name))
                self.uploader.upload(rf, f.name)
                uploaded_files.append(f)
        request.registry.notify(AfterS3Upload(request, session, uploaded_files, self.uploader, result.get("extra_args", [])))


@provider(IS3UtilityFactory)
class NullConnectionFactory(object):
    @classmethod
    def from_settings(cls, settings):
        return cls()
    
    def add_subscribers(self, config):
        config.add_subscriber(self.logging_message, "altaircms.filelib.adapts.AfterCommit")

    def logging_message(self, event):
        result = event.result #{"create": [], "delete": [], "extra_args": []}
        logger.warn("*debug after upload. result={0}".format(result))

def includeme(config):
    config.add_directive("add_s3utility", add_s3utility)
