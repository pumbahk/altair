# -*-coding:utf-8 -*-
from zope.interface import provider
from .interfaces import IS3UtilityFactory
from altair.pyramid_boto.s3.connection import DefaultS3ConnectionFactory
from altair.pyramid_boto.s3.connection import DefaultS3Uploader

import logging
logger = logging.getLogger(__name__)

def add_s3utility(config, factory):
    config.registry.registerUtility(factory, IS3UtilityFactory)
    if hasattr(factory, "setup"):
        factory.setup(config)

class S3Event(object):
    def __init__(self, request, session, files, uploader, extra_args):
        self.request = request
        self.session = session
        self.files = files
        self.uploader = uploader
        self.extra_args = extra_args

class AfterS3Upload(S3Event):
    pass

class AfterS3Delete(S3Event):
    pass



@provider(IS3UtilityFactory)
class S3ConnectionFactory(object):
    def __init__(self, uploader):
        self.uploader = uploader

    @classmethod
    def from_settings(cls, settings):
        access_key, secret_key = settings["s3.access_key"], settings["s3.secret_key"]
        bucket_name = settings["s3.bucket_name"]
        connection_factory = DefaultS3ConnectionFactory(access_key, secret_key)
        return cls(DefaultS3Uploader(connection_factory, bucket_name, public=True))

    def setup(self, config):
        config.add_subscriber(self.sync_s3_after_commit, "altaircms.filelib.adapts.AfterCommit")

    def sync_s3_after_commit(self, event):
        request = event.request
        result = event.result #{"create": [], "delete": [], "extra_args": []}
        session = event.session
        uploaded_files = []
        deleted_files = []
        for f, realpath in result.get("create", []):
            self.upload(f, realpath)
            uploaded_files.append(f)
        if uploaded_files:
            request.registry.notify(AfterS3Upload(request, session, uploaded_files, self.uploader, result.get("extra_args", [])))

        for f, realpath in result.get("delete", []):
            self.delete(f, realpath)
            deleted_files.append(f)
        if deleted_files:
            request.registry.notify(AfterS3Delete(request, session, deleted_files, self.uploader, result.get("extra_args", [])))

    def upload(self, f, realpath):
        logger.warn("*debug upload: bucket={0} name={1}".format(self.uploader.bucket_name, f.name))
        with open(realpath) as rf:
            self.uploader.upload(rf, f.name)

    def delete(self, f, realpath):
        logger.warn("*debug delete: bucket={0} name={1}".format(self.uploader.bucket_name, f.name))
        ## uploadしたファイルは残す.
        # self.uploader.delete(f, f.name)


@provider(IS3UtilityFactory)
class NullConnectionFactory(object):
    @classmethod
    def from_settings(cls, settings):
        return cls()
    
    def setup(self, config):
        config.add_subscriber(self.logging_message, "altaircms.filelib.adapts.AfterCommit")

    def logging_message(self, event):
        result = event.result #{"create": [], "delete": [], "extra_args": []}
        logger.warn("*debug after upload. result={0}".format(result))

def includeme(config):
    config.add_directive("add_s3utility", add_s3utility)
