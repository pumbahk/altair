# -*-coding:utf-8 -*-
from zope.interface import provider
from .interfaces import IS3UtilityFactory
from altair.pyramid_boto.s3.connection import DefaultS3ConnectionFactory
from altair.pyramid_boto.s3.connection import DefaultS3Uploader
from boto.s3.key import Key
from pyramid.exceptions import ConfigurationError

import logging
logger = logging.getLogger(__name__)

def add_s3utility(config, factory):
    config.registry.registerUtility(factory, IS3UtilityFactory)
    if hasattr(factory, "setup"):
        factory.setup(config)

def get_s3_utility_factory(request):
    return request.registry.queryUtility(IS3UtilityFactory)

def s3load_as_string(request, uri):
    return s3load(request, uri).get_contents_as_string()

def s3load_to_filename(request, uri, filename):
    return s3load(request, uri).get_contents_to_filename(filename)

def s3load(request, uri):
    bucket = get_s3_utility_factory(request).uploader.bucket #xxx:
    k = Key(bucket)
    k.key = uri
    return k


class S3Event(object):
    def __init__(self, request, session, files, uploader, extra_args):
        self.request = request
        self.session = session
        self.files = files
        self.uploader = uploader
        self.extra_args = extra_args

class BeforeS3Upload(S3Event):
    pass

class BeforeS3Delete(S3Event):
    pass

class AfterS3Upload(S3Event):
    pass

class AfterS3Delete(S3Event):
    pass

@provider(IS3UtilityFactory)
class S3ConnectionFactory(object):
    def __init__(self, uploader):
        self.uploader = uploader

    @property
    def bucket_name(self):
        return self.uploader.bucket_name

    @property
    def bucket(self):
        return self.uploader.bucket

    @classmethod
    def from_settings(cls, settings):
        access_key, secret_key = settings["s3.access_key"], settings["s3.secret_key"]
        bucket_name = settings["s3.bucket_name"]
        connection_factory = DefaultS3ConnectionFactory(access_key, secret_key)
        return cls(DefaultS3Uploader(connection_factory, bucket_name, public=True))

    def setup(self, config):
        config.add_subscriber(self.sync_s3_after_commit, "altaircms.filelib.adapts.AfterCommit")
        ## too-heavie
        # self.validate()

    def validate(self):
        if not self.uploader.is_reacheable():
            raise ConfigurationError("S3 access is unreacheable. bucket={0}, access_key={1}".format(self.uploader.bucket_name, self.uploader.connection.aws_access_key_id))

    def sync_s3_after_commit(self, event):
        request = event.request
        result = event.result #{"create": [], "delete": [], "extra_args": []}
        session = event.session
        options = event.options

        uploaded_files = []
        deleted_files = []
        notify = request.registry.notify
        #upload
        files = result.get("create", [])
        if files:
            before_upload_event = BeforeS3Upload(request, session, files, self.uploader, result.get("extra_args", []))
            notify(before_upload_event)
            for f, realpath in before_upload_event.files:
                self.upload(f, realpath, options=options)
                uploaded_files.append(f)
        if uploaded_files:
            notify(AfterS3Upload(request, session, uploaded_files, self.uploader, result.get("extra_args", [])))

        #delete
        files = result.get("delete", [])
        if files:
            before_delete_event = BeforeS3Delete(request, session, files, self.uploader, result.get("extra_args", []))
            notify(before_delete_event)
            for f, realpath in before_delete_event.files:
                self.delete(f, realpath, options=options)
                deleted_files.append(f)
        if deleted_files:
            notify(AfterS3Delete(request, session, deleted_files, self.uploader, result.get("extra_args", [])))

    def upload(self, f, realpath, options=None):
        logger.info("*debug upload: bucket={0} name={1}".format(self.uploader.bucket_name, f.name))
        with open(realpath) as rf:
            self.uploader.upload(rf, f.name, options)

    def delete(self, f, realpath, options=None):
        logger.info("*debug delete: bucket={0} name={1}".format(self.uploader.bucket_name, f.name))
        ## uploadしたファイルは残す.
        # self.uploader.delete(f.name, options)

@provider(IS3UtilityFactory)
class NullConnectionFactory(object):
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name

    @classmethod
    def from_settings(cls, settings):
        bucket_name = settings.get("s3.bucket_name", ":bucket-name:")
        return cls(bucket_name)
    
    def setup(self, config):
        config.add_subscriber(self.logging_message, "altaircms.filelib.adapts.AfterCommit")
        config.add_subscriber("altaircms.asset.subscribers.refresh_file_url_when_null_connection", "altaircms.filelib.adapts.AfterCommit")

    def logging_message(self, event):
        result = event.result #{"create": [], "delete": [], "extra_args": []}
        logger.info("*debug after upload. result={0}".format(result))

from .core import DummyFile

class Renamer(object):
    def __init__(self, request, event):
        self.request = request
        self.event = event

    def rename(self, rename_fn):
        updated = []
        for f, realpath in self.event.files:
            name = f.name
            updated_name = rename_fn(self.request, name)
            updated.append((DummyFile(name=updated_name), realpath))
            logger.info("*debug rename_for_s3_upload: change name {0} -> {1}".format(name, updated_name))
        self.event.files = updated


def includeme(config):
    config.add_directive("add_s3utility", add_s3utility)
