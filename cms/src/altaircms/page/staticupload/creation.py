#-*- coding:utf-8 -*-
import uuid
import os
import shutil #todo:move
import logging
logger = logging.getLogger(__name__)

from ..models import StaticPage, StaticPageSet
from ...subscribers import notify_model_create
from ...models import DBSession
from ...filelib import get_adapts_filesession
from . import SESSION_NAME
from altaircms.helpers.viewhelpers import FlashMessage

class StaticPageEvent(object):
    def __init__(self, request, root, static_directory, static_page):
        self.request = request
        self.root = root
        self.static_page = static_page
        self.static_directory = static_directory

class AfterModelCreate(StaticPageEvent):
    pass

class AfterModelDelete(StaticPageEvent):
    pass

class AfterPartialDeleteFile(StaticPageEvent):
    pass
class AfterPartialUpdateFile(StaticPageEvent):
    pass
class AfterPartialCreateFile(StaticPageEvent):
    pass
class AfterPartialDeleteDirectory(StaticPageEvent):
    pass
class AfterPartialCreateDirectory(StaticPageEvent):
    pass

class AfterDeleteCompletely(object):
    def __init__(self, request, static_directory, static_pageset):
        self.request = request
        self.static_directory = static_directory
        self.static_pageset = static_pageset

    
def get_staticupload_filesession(request):
    return get_adapts_filesession(request, name=SESSION_NAME)

class StaticPageIntercept(object):
    def __init__(self, request, utility):
        self.request = request
        self.utility = utility

    def intercept(self, static_page):
        static_page.interceptive = not static_page.interceptive

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
        src = self.utility.get_rootname(static_page)
        self.request.registry.notify(AfterModelDelete(self.request, src, self.utility, static_page))
        try:
            ## snapshot取っておく
            self.utility.backup(src)
            ## 直接のsrcは空で保存できるようになっているはず。
            if os.path.lexists(src):
                raise Exception("%s exists. after delete" % src)
        except Exception, e:
            logger.exception(str(e))
            raise 

class StaticPageCreate(object):
    def __init__(self, request, utility, data):
        self.request = request
        self.utility = utility
        self.data = data
        self.rollback_functions = []

    def rollback(self):
        for f in self.rollback_functions:
            f()

    def create(self):
        static_page = self.create_model()
        self.create_underlying_something(static_page)
        return static_page

    def create_model(self):
        data = self.data
        pageset = StaticPageSet(url=data["name"], 
                                name=data["label"], 
                                hash=uuid.uuid4().hex)
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

        def rollback():
            DBSession.delete(DBSession.merge(static_page))
            DBSession.delete(DBSession.merge(pageset))
        self.rollback_functions.append(rollback)

        DBSession.flush()
        return static_page
    
    def create_underlying_something(self, static_page):
        filestorage = self.data["zipfile"]
        absroot = self.utility.get_rootname(static_page)
        if filestorage == u"":
            logger.info("zip file is not found.")
            os.makedirs(absroot)
            return

        def rollback():
            self.utility.delete(os.path.dirname(absroot))
        self.rollback_functions.append(rollback)
        self.utility.create(absroot, filestorage.file) and self.request.registry.notify(AfterModelCreate(self.request, absroot, self.utility, static_page))


    def update_underlying_something(self, static_page):
        filestorage = self.data["zipfile"]
        absroot = self.utility.get_rootname(static_page)
        self.utility.update(absroot, filestorage.file) and self.request.registry.notify(AfterModelCreate(self.request, absroot, self.utility, static_page))

class PartialChange(object):
    def __init__(self, request, utility, data):
        self.request = request
        self.utility = utility
        self.data = data

    def delete_file(self, static_page):
        absroot = self.utility.get_rootname(static_page)
        name = self.data["name"].lstrip("/")
        path = os.path.join(absroot, name)
        os.remove(path)
        self.request.registry.notify(AfterPartialDeleteFile(self.request, path, self.utility, static_page))
        FlashMessage.success(u"ファイル:「%s」を削除しました" % name, request=self.request)

    def create_file(self, static_page):
        filename = self.request.matchdict["path"].replace("%2F", "/").lstrip("/")
        absroot = self.utility.get_rootname(static_page)
        path = os.path.join(absroot, filename, self.data["name"])
        dirname = os.path.dirname(path)
        if not os.path.lexists(dirname):
            os.makedirs(dirname)
        with open(path, "wb") as wf:
            shutil.copyfileobj(self.data["file"].file, wf)
        self.request.registry.notify(AfterPartialCreateFile(self.request, path, self.utility, static_page))
        FlashMessage.success(u"ファイル:「%s」を追加しました" % os.path.join(filename, self.data["name"]), request=self.request)

    def update_file(self, static_page):
        name = self.data["name"]
        absroot = self.utility.get_rootname(static_page)
        path = os.path.join(absroot, name)
        dirname = os.path.dirname(path)
        if not os.path.lexists(dirname):
            os.makedirs(dirname)
        with open(path, "wb") as wf:
            shutil.copyfileobj(self.data["file"].file, wf)
        self.request.registry.notify(AfterPartialUpdateFile(self.request, path, self.utility, static_page))
        FlashMessage.success(u"ファイル:「%s」を更新しました" % name, request=self.request)

    def create_directory(self, static_page):
        absroot = self.utility.get_rootname(static_page)
        filename = self.request.matchdict["path"].replace("%2F", "/").lstrip("/")
        path = os.path.join(absroot, filename, self.data["name"])
        os.makedirs(path)
        self.request.registry.notify(AfterPartialCreateDirectory(self.request, path, self.utility, static_page))
        FlashMessage.success(u"ディレクトリ:「%s」を追加しました" % os.path.join(filename, self.data["name"]), request=self.request)

    def delete_directory(self, static_page):
        absroot = self.utility.get_rootname(static_page)
        name = self.data["name"]
        path = os.path.join(absroot, name)
        shutil.rmtree(path)
        self.request.registry.notify(AfterPartialDeleteDirectory(self.request, path, self.utility, static_page))
        FlashMessage.success(u"ディレクトリ:「%s」を削除しました" % name, request=self.request)
