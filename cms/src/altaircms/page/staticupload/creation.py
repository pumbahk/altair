#-*- coding:utf-8 -*-
import os
import logging
logger = logging.getLogger(__name__)

from ..models import StaticPage, StaticPageSet
from ...subscribers import notify_model_create
from ...models import DBSession
from altaircms.filelib.zipupload import AfterZipUpload


class StaticPageDelete(object):
    def __init__(self, request, utility):
        self.request = request
        self.utility = utility

    def delete(self, static_page):
        self.delete_model(static_page)
        self.delete_underlying_something(static_page)

    def delete_model(self, static_page):
        DBSession.delete(static_page)

    def delete_underlying_something(self, static_page):
        try:
            ## snapshot取っておく
            src = self.utility.get_rootname(static_page)
            self.utility.backup(src)

            ## 直接のsrcは空で保存できるようになっているはず。
            if os.path.exists(src):
                raise Exception("%s exists. after delete" % src)
        except Exception, e:
            logger.exception(str(e))
            raise 
        
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
                                 )
        DBSession.add(static_page)
        notify_model_create(self.request, static_page, data)
        notify_model_create(self.request, pageset, data)
        DBSession.flush()
        return static_page
    
    def create_underlying_something(self, static_page):
        filestorage = self.data["zipfile"]
        absroot = self.utility.get_rootname(static_page)
        if filestorage == u"":
            logger.info("zip file is not found.")
            os.makedirs(absroot)
            return
        self.utility.create(absroot, filestorage.file) and self.request.registry.notify(AfterZipUpload(self.request, absroot))

    def update_underlying_something(self, static_page):
        filestorage = self.data["zipfile"]
        absroot = self.utility.get_rootname(static_page)
        self.utility.update(absroot, filestorage.file) and self.request.registry.notify(AfterZipUpload(self.request, absroot))
