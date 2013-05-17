#-*- coding:utf-8 -*-
import copy
import os
from pyramid.httpexceptions import HTTPFound, HTTPForbidden
from pyramid.response import FileResponse
from altaircms.filelib import zipupload
from pyramid.view import view_config
from pyramid.view import view_defaults
from altaircms.lib.fanstatic_decorator import with_bootstrap

from altaircms.helpers.viewhelpers import FlashMessage
from altaircms.auth.api import get_or_404
from .. import StaticPageNotFound
from .api import get_static_page_utility
from .api import as_static_page_response
from altaircms.models import DBSession
from altaircms.page.models import StaticPageSet, StaticPage
from . import forms
from . import creation
from .renderable import StaticPageDirectoryRenderer
import logging
logger = logging.getLogger(__name__)
from altaircms.helpers.viewhelpers import get_endpoint

@view_defaults(route_name="static_page_create", permission="authenticated")
class StaticPageCreateView(object):
    def __init__(self, context, request):
        self.request = request
        self.context = context
        
    @view_config(match_param="action=input", decorator=with_bootstrap,
                 renderer="altaircms:templates/page/static_page_add.html")
    def input(self):
        form = self.context.form(forms.StaticPageCreateForm)
        return {"form": form}

    @view_config(match_param="action=create", request_method="POST", 
                 decorator=with_bootstrap,
                 renderer="altaircms:templates/page/static_page_add.html")
    def create(self):
        form = self.context.form(forms.StaticPageCreateForm, self.request.POST)
        if not form.validate():
            return {"form": form}
        creator = self.context.creation(creation.StaticPageCreate, form.data)
        static_page = creator.create()
        FlashMessage.success(u"%sが作成されました" % static_page.label, request=self.request)
        return HTTPFound(self.request.route_url("static_pageset", action="detail", static_page_id=static_page.pageset.id))

@view_defaults(route_name="static_pageset", permission="authenticated")
class StaticPageSetView(object):
    def __init__(self, context, request):
        self.request = request
        self.context = context

    @view_config(match_param="action=toggle_publish")
    def toggle_publish(self):
        pk = self.request.matchdict["static_page_id"]
        static_page = get_or_404(self.request.allowable(StaticPage), StaticPage.id==pk)
        status = self.request.GET.get("status")
        if status == "publish":
            static_page.published = True
        elif status == "unpublish":
            static_page.published = False
        else:
            static_page.published = not static_page.published
        FlashMessage.success(u"このページを%sしました" % (u"公開" if static_page.published else u"非公開に"), request=self.request)
        return HTTPFound(get_endpoint(self.request) or self.request.route_url("static_pageset", action="detail", static_page_id=static_page.id))

    @view_config(match_param="action=detail", renderer="altaircms:templates/page/static_detail.html", 
                 decorator=with_bootstrap)
    def detail(self):
        pk = self.request.matchdict["static_page_id"]
        static_pageset = get_or_404(self.request.allowable(StaticPageSet), StaticPageSet.id==pk)
        static_directory = get_static_page_utility(self.request)
        static_page = StaticPage.query.filter_by(pageset=static_pageset, id=self.request.GET.get("child_id")).first()
        static_page = static_page or static_pageset.pages[0]
        return {"static_pageset": static_pageset, 
                "static_page": static_page,                 
                "static_directory": static_directory, 
                "tree_renderer": StaticPageDirectoryRenderer(self.request, static_page, static_directory)}

    @view_config(match_param="action=shallow_copy")
    def shallow_copy(self):
        static_pageset_id = self.request.matchdict["static_page_id"]
        static_page = get_or_404(self.request.allowable(StaticPage), StaticPage.id==self.request.params.get("child_id"))
        copied = copy.copy(static_page)
        copied.label += u"のコピー"
        DBSession.add(copied)
        DBSession.flush()
        static_directory = get_static_page_utility(self.request)
        static_directory.prepare(static_directory.get_rootname(copied))
        return HTTPFound(get_endpoint(self.request) or self.request.route_url("static_pageset", action="detail", static_page_id=static_pageset_id))

    @view_config(match_param="action=deep_copy")
    def deep_copy(self):
        static_pageset_id = self.request.matchdict["static_page_id"]
        static_page = get_or_404(self.request.allowable(StaticPage), StaticPage.id==self.request.params.get("child_id"))
        copied = copy.copy(static_page)
        copied.label += u"のコピー"
        DBSession.add(copied)
        DBSession.flush()
        static_directory = get_static_page_utility(self.request)
        static_directory.copy(static_directory.get_rootname(static_page), 
                              static_directory.get_rootname(copied))
        return HTTPFound(get_endpoint(self.request) or self.request.route_url("static_pageset", action="detail", static_page_id=static_pageset_id))

    

    @view_config(match_param="action=delete", request_method="POST", renderer="json")
    def delete(self):
        pk = self.request.matchdict["static_page_id"]
        static_page = get_or_404(self.request.allowable(StaticPage), StaticPage.id==pk)
        static_directory = get_static_page_utility(self.request)
        name = static_page.name

        try:
            self.context.delete_static_page(static_page)

            ## snapshot取っておく
            src = os.path.join(static_directory.get_base_directory(), static_page.name)
            zipupload.create_directory_snapshot(src)

            ## 直接のsrcは空で保存できるようになっているはず。
            if os.path.exists(src):
                raise Exception("%s exists. after delete" % src)
            FlashMessage.success(u"%sが削除されました" % name, request=self.request)
            return {"redirect_to": self.request.route_url("pageset_list", pagetype="static")}
        except Exception, e:
            logger.exception(str(e))
            raise 

    @view_config(match_param="action=download")
    def download(self):
        pk = self.request.matchdict["static_page_id"]
        static_page = get_or_404(self.request.allowable(StaticPage), StaticPage.id==pk)
        static_directory = get_static_page_utility(self.request)

        dirname = os.path.join(static_directory.get_base_directory(), static_page.name)
        writename = os.path.join(static_directory.tmpdir, static_page.name+".zip")
        with zipupload.current_directory(dirname):
            zipupload.create_zipfile_from_directory(".", writename)
        response = FileResponse(path=writename, request=self.request)
        response.content_disposition = 'attachment; filename="%s.zip"' % static_page.name
        return response

    @view_config(match_param="action=upload", request_param="zipfile", request_method="POST")
    def upload(self):
        pk = self.request.matchdict["static_page_id"]
        static_page = get_or_404(self.request.allowable(StaticPage), StaticPage.id==pk)
        static_directory = get_static_page_utility(self.request)

        filestorage = self.request.POST["zipfile"]
        if filestorage == u"":
            FlashMessage.error(u"投稿されたファイルは、zipファイルではありません", request=self.request)
            raise HTTPFound(self.request.route_url("static_pageset", action="detail", static_page_id=static_page.id))
        uploaded = filestorage.file
        if not zipupload.is_zipfile(uploaded):
            FlashMessage.error(u"投稿されたファイル%sは、zipファイルではありません" % filestorage.filename, request=self.request)
            raise HTTPFound(self.request.route_url("static_pageset", action="detail", static_page_id=static_page.id))

        src = os.path.join(static_directory.get_base_directory(), static_page.name)
        snapshot_path = zipupload.create_directory_snapshot(src)

        try:
            zipupload.replace_directory_from_zipfile(src, filestorage.file)
            self.context.touch_static_page(static_page)
        except:
            zipupload.snapshot_rollback(src, snapshot_path)

        FlashMessage.success(u"%sが更新されました" % filestorage.filename, request=self.request)
        return HTTPFound(self.request.route_url("static_pageset", action="detail", static_page_id=static_page.id))

@view_config(route_name="static_page_display", permission="authenticated")
def static_page_display_view(context, request):
    prefix = request.matchdict["path"].lstrip("/").split("/", 1)[0]
    static_page = get_or_404(request.allowable(StaticPage), StaticPage.name==prefix)
    try:
        if request.GET.get("force_original"):
            return as_static_page_response(request, static_page, request.matchdict["path"], force_original=True)
        return as_static_page_response(request, static_page, request.matchdict["path"])
    except StaticPageNotFound:
        raise HTTPForbidden()
