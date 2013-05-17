# -*- coding:utf-8 -*-
import os
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

    def get_rootname(self, static_page):
        assert static_page.id
        return os.path.join(self.get_base_directory(), 
                            unicode(static_page.id), 
                            static_page.name
                            )

    def rename(self, src, dst):
        logger.info("rename static pages: %s -> %s" % (src, dst))
        return os.rename(os.path.join(self.get_base_directory(), src), 
                         os.path.join(self.get_base_directory(), dst))
