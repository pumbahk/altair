# -*- coding:utf-8 -*-
import os
import shutil
from ...interfaces import IDirectoryResource
from zope.interface import implementer
from pyramid.path import AssetResolver

import logging
logger = logging.getLogger(__name__)

class StaticPageDirectoryFactory(object):
    def __init__(self, basedir, tmpdir="/tmp"):
        self.assetresolver = AssetResolver()
        self.assetspec = basedir
        self.basedir = self.assetresolver.resolve(basedir).abspath()
        self.tmpdir = self.assetresolver.resolve(tmpdir).abspath()

    def __call__(self, request):
        return StaticPageDirectory(request, self.assetspec, self.basedir, self.tmpdir)

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
        logger.info("prepare static pages: %s" % (src))
        os.makedirs(src)

    def copy(self, src, dst):
        logger.info("copy static pages: %s -> %s" % (src, dst))        
        shutil.copytree(src, dst)

    def rename(self, src, dst):
        logger.info("rename static pages: %s -> %s" % (src, dst))
        return os.rename(src, dst)
