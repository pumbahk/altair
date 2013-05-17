#-*- coding:utf-8 -*-
import os
import logging
logger = logging.getLogger(__name__)

from ..models import StaticPage, StaticPageSet
from ...subscribers import notify_model_create
from ...models import DBSession
from altaircms.filelib import zipupload

"""
memo: 
<basedir>/<static_page_id>/<name>

となるのでパスは重ならない。ファイル名の重複をチェックする必要はない
"""

def get_rootname(basedir, static_page):
    assert static_page.id
    return os.path.join(basedir,
                        unicode(static_page.id), 
                        static_page.name
                        )
    

class StaticPageCreate(object):
    def __init__(self, request, utility, data):
        self.request = request
        self.utility = utility
        self.data = data

    def create(self):
        static_page = self.create_model()
        self.create_underlying_something(static_page)
        return static_page

    def create_model(self):
        data = self.data
        pageset = StaticPageSet(url=data["name"], 
                          name=data["name"])
        static_page = StaticPage(name=data["name"],
                                 pageset=pageset, 
                                 layout=data["layout"],
                                 label=data["label"],
                                 publish_begin=data["publish_begin"],
                                 publish_end=data["publish_end"],
                                 interceptive=data["interceptive"]
                                 )
        DBSession.add(static_page)
        notify_model_create(self.request, static_page, data)
        DBSession.flush()
        return static_page

    
    def create_underlying_something(self, static_page):
        filestorage = self.data["zipfile"]
        absroot = get_rootname(self.utility.get_base_directory(), static_page)
        if filestorage == u"":
            logger.info("zip file is not found.")
            os.makedirs(absroot)
            return
        zipupload.replace_directory_from_zipfile(absroot, filestorage.file)
        self.request.registry.notify(zipupload.AfterZipUpload(self.request, absroot))
