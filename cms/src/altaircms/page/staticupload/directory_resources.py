# -*- coding:utf-8 -*-
import os
import shutil
from ...interfaces import IDirectoryResource
from ...filelib import zipupload
from zope.interface import implementer
from pyramid.path import AssetResolver

from altaircms.filelib.s3 import get_s3_utility_factory
from pyramid.decorator import reify

import logging
logger = logging.getLogger(__name__)

class AfterCreate(object):
    def __init__(self, request, static_directory, root):
        self.request = request
        self.static_directory = static_directory
        self.root = root


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
  
@implementer(IDirectoryResource)
class StaticPageDirectory(object):
    def __init__(self, request, assetspec, basedir, tmpdir):
        self.request = request
        self.assetspec = basedir
        self.basedir = basedir
        self.tmpdir = tmpdir

    def get_base_directory(self):
        return os.path.join(self.basedir, self.request.organization.short_name)

    def get_rootname(self, static_page, name=None):
        assert static_page.id
        return os.path.join(self.get_base_directory(), 
                            name or static_page.name, 
                            unicode(static_page.id), 
                            )

    def get_writename(self, static_page):
       return os.path.join(self.tmpdir, static_page.name+".zip")

    def prepare(self, src):
        logger.info("prepare src: %s" % (src))
        os.makedirs(src)

    def copy(self, src, dst):
        logger.info("copy src: %s -> %s" % (src, dst))        
        shutil.copytree(src, dst)

    def rename(self, src, dst):
        logger.info("rename src: %s -> %s" % (src, dst))
        return os.rename(src, dst)

    def backup(self, src):
        logger.info("backup src: %s" % (src))        
        return zipupload.create_directory_snapshot(src)

    def delete(self, src):
        logger.info("delete src: %s" % (src))        
        return shutil.rmtree(src)

    def create(self, src, io):
        logger.info("create src: %s" % (src))                
        zipupload.extract_directory_from_zipfile(src, io)
        self.request.registry.notify(AfterCreate(self.request, self, src))
        return True

    def update(self, src, io):
        backup_path = self.backup(src)
        try:
            self.create(src, io)
            return True
        except Exception as e:
            logger.exception(e)
            zipupload.snapshot_rollback(src, backup_path)
            raise 


@implementer(IDirectoryResource)
class S3StaticPageDirectory(StaticPageDirectory):
    prefix = "static/uploaded"
    @reify
    def s3utility(self):
        return get_s3_utility_factory(self.request)

    def get_base_url(self, dirname, filename):
        bucket_name = self.s3utility.bucket_name
        return "http://{0}.s3.amazonaws.com/{1}{2}/".format(bucket_name, self.prefix, dirname.replace(self.basedir, ""))
