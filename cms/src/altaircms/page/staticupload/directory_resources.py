# -*- coding:utf-8 -*-
import os
import shutil
from zope.interface import implementer
from pyramid.path import AssetResolver
from pyramid.exceptions import ConfigurationError
from pyramid.decorator import reify
from altaircms.filelib.s3 import get_s3_utility_factory
from ...interfaces import IDirectoryResource
from ...filelib import zipupload

import logging
logger = logging.getLogger(__name__)

class AfterCreate(object):
    def __init__(self, request, static_directory, root):
        self.request = request
        self.static_directory = static_directory
        self.root = root

class AfterChangeDirectory(object):
    def __init__(self, request, static_directory, src, dst):
        self.request = request
        self.static_directory = static_directory
        self.src = src
        self.dst = dst

class StaticPageDirectoryFactory(object):
    def __init__(self, basedir, tmpdir="/tmp"):
        self.assetresolver = AssetResolver()
        self.assetspec = basedir
        self.basedir = self.assetresolver.resolve(basedir).abspath()
        self.tmpdir = self.assetresolver.resolve(tmpdir).abspath()

    def __call__(self, request):
        return StaticPageDirectory(request, self.assetspec, self.basedir, self.tmpdir)

class S3StaticPageDirectoryFactory(StaticPageDirectoryFactory):
    def __call__(self, request):
        return S3StaticPageDirectory(request, self.assetspec, self.basedir, self.tmpdir)

    def setup(self, config):
        config.add_subscriber(".subscribers.refine_html_files_after_staticupload", ".directory_resources.AfterCreate")
        config.add_subscriber(".subscribers.s3rename_uploaded_files", ".directory_resources.AfterChangeDirectory")
        config.add_subscriber(".subscribers.s3clean_directory", ".creation.AfterModelDelete")  
        config.add_subscriber(".subscribers.s3upload_directory", ".creation.AfterModelCreate")  
        config.add_subscriber(".subscribers.s3delete_files_completely", ".creation.AfterDeleteCompletely")  
        config.add_subscriber(".subscribers.delete_completely_filesystem", ".creation.AfterDeleteCompletely")  
        config.add_subscriber(".subscribers.update_model_file_structure", ".creation.AfterModelCreate")

        config.add_subscriber(".subscribers.refine_html_file_after_staticupload", ".creation.AfterPartialCreateFile")
        config.add_subscriber(".subscribers.refine_html_file_after_staticupload", ".creation.AfterPartialUpdateFile")
        config.add_subscriber(".subscribers.s3update_file", ".creation.AfterPartialCreateFile")
        config.add_subscriber(".subscribers.s3update_file", ".creation.AfterPartialUpdateFile")
        config.add_subscriber(".subscribers.s3delete_file", ".creation.AfterPartialDeleteFile")
        config.add_subscriber(".subscribers.s3clean_directory", ".creation.AfterPartialDeleteDirectory")
        config.add_subscriber(".subscribers.update_model_file_structure", ".creation.AfterPartialCreateFile")
        config.add_subscriber(".subscribers.update_model_file_structure", ".creation.AfterPartialUpdateFile")
        config.add_subscriber(".subscribers.update_model_file_structure", ".creation.AfterPartialDeleteFile")
        config.add_subscriber(".subscribers.update_model_file_structure", ".creation.AfterPartialCreateDirectory")
        config.add_subscriber(".subscribers.update_model_file_structure", ".creation.AfterPartialDeleteDirectory")
        ## validation:

        if get_s3_utility_factory(config) is None:
            raise ConfigurationError("s3 utility is not found")

@implementer(IDirectoryResource)
class StaticPageDirectory(object):
    def __init__(self, request, assetspec, basedir, tmpdir):
        self.request = request
        self.assetspec = basedir
        self.basedir = basedir
        self.tmpdir = tmpdir

    def get_base_directory(self):
        return os.path.join(self.basedir, self.request.organization.short_name)

    def get_toplevelname(self, static_pageset, name=None):
        return os.path.join(self.get_base_directory(), 
                            name or static_pageset.hash, 
                            )

    def get_rootname(self, static_page, name=None):
        assert static_page.id
        return os.path.join(self.get_base_directory(), 
                            name or static_page.prefix, 
                            unicode(static_page.id), 
                            )

    def get_obsolute_rootname(self, static_page):
        return os.path.join(self.get_base_directory(), 
                            static_page.prefix, 
                            )

    def get_writename(self, static_page):
       return os.path.join(self.tmpdir, static_page.prefix+".zip")

    def prepare(self, src):
        logger.info("prepare src: %s" % (src))
        os.makedirs(src)

    def copy(self, src, dst):
        logger.info("copy src: %s -> %s" % (src, dst))        
        shutil.copytree(src, dst)
        self.request.registry.notify(AfterCreate(self.request, self, dst))

    def rename(self, src, dst):
        logger.info("rename src: %s -> %s" % (src, dst))
        os.rename(src, dst)
        self.request.registry.notify(AfterChangeDirectory(self.request, self, src, dst))

    def backup(self, src):
        logger.info("backup src: %s" % (src))        
        return zipupload.create_directory_snapshot(src)

    def delete(self, src):
        logger.warn("delete src: %s" % (src))        
        return shutil.rmtree(src)
        
    def create(self, src, io):
        logger.info("create src: %s" % (src))
        try:
            zipupload.extract_directory_from_zipfile(src, io)
            self.request.registry.notify(AfterCreate(self.request, self, src))
            return True
        except UnicodeDecodeError:
            logger.error("uploaded zip file is invalid")
            raise 

    def update(self, src, io):
        logger.info("update src: %s" % (src))                
        if not os.path.exists(src):
            logger.warn("directory_resource. src={0} is not found. just create.".format(src))
            return self.create(src, io)

        backup_path = self.backup(src)
        try:
            return self.create(src, io)
        except Exception as e:
            logger.exception(e)
            zipupload.snapshot_rollback(src, backup_path)
            raise 


## todo: split
@implementer(IDirectoryResource)
class S3StaticPageDirectory(StaticPageDirectory):
    prefix = "usersite/uploaded"
    @reify
    def s3utility(self):
        return get_s3_utility_factory(self.request)

    def get_base_url(self, dirname, filename):
        bucket_name = self.s3utility.bucket_name
        return "http://{0}.s3.amazonaws.com/{1}{2}/".format(bucket_name, self.prefix, dirname.replace(self.basedir, ""))

    def get_name(self, dirname, filename):
        return u"{0}{1}/{2}".format(self.prefix, dirname.replace(self.basedir, ""), filename)

    def get_url(self, path):
        return self._get_url(path.replace(self.basedir, ""))

    def _get_url(self, urlpart): ##xxxx: this is miss leading
        bucket_name = self.s3utility.bucket_name    
        return "http://{0}.s3.amazonaws.com/{1}{2}".format(bucket_name, self.prefix, urlpart)

    ## todo: move?
    def upload_file(self, root, f, uploader=None):
        uploader = uploader or self.s3utility.uploader
        with open(os.path.join(root, f), "r") as rf:
            keyname = self.get_name(root, f)
            logger.info("*debug upload file:{0}".format(keyname))
            uploader.upload_file(rf, keyname)
        
    def upload_directory(self, d):
        uploader = self.s3utility.uploader
        logger.info("upload_directory: {0}".format(d))
        for root, dirs, files in os.walk(d):
            for f in files:
                self.upload_file(root, f, uploader)

    def delete_file(self, root, f, uploader=None):
        uploader = uploader or self.s3utility.uploader        
        keyname = self.get_name(root, f)
        logger.info("*debug delete file:{0}".format(keyname))
        uploader.unpublish(keyname)

    def clean_directory(self, d):
        uploader = self.s3utility.uploader
        logger.info("clean_directory: {0}".format(d))
        r = []
        for root, dirs, files in os.walk(d):
            for f in files:
                r.append(self.get_name(root, f))
        uploader.unpublish_items(r)

    def copy_items(self, src, dst):
        logger.info("copy_items: {0} -> {1}".format(src, dst))
        uploader = self.s3utility.uploader
        try:
            uploader.copy_items(src, dst, recursive=True)
        except Exception as e:
            logger.exception(str(e))
        else:
            self.clean_items(self, src)

    def clean_items(self, src):
        logger.info("clean_items: src = {0}".format(src))
        uploader = self.s3utility.uploader
        uploader.unpublish_items(list(uploader.bucket.list(src)))
