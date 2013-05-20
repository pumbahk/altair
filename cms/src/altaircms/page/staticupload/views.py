#-*- coding:utf-8 -*-
import copy
import os
from pyramid.httpexceptions import HTTPFound, HTTPForbidden
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
from altaircms.viewlib import BaseView, download_response
from altaircms.datelib import get_now

@view_defaults(route_name="static_page_create", permission="authenticated")
class StaticPageCreateView(BaseView):
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
        return HTTPFound(self.context.endpoint(static_page))

@view_defaults(route_name="static_pageset", permission="authenticated")
class StaticPageSetView(BaseView):

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
                "current_page": static_pageset.current(), 
                "tree_renderer": StaticPageDirectoryRenderer(self.request, static_page, static_directory), 
                "now": get_now(self.request)}

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

@view_defaults(route_name="static_page", permission="authenticated")
class StaticPageView(BaseView):
    @view_config(match_param="action=shallow_copy")
    def shallow_copy(self):
        static_page = get_or_404(self.request.allowable(StaticPage), StaticPage.id==self.request.matchdict["child_id"])
        copied = copy.copy(static_page)
        copied.label += u"のコピー"
        DBSession.add(copied)
        DBSession.flush()
        static_directory = get_static_page_utility(self.request)
        static_directory.prepare(static_directory.get_rootname(copied))
        return HTTPFound(self.context.endpoint(static_page))


    @view_config(match_param="action=deep_copy")
    def deep_copy(self):
        static_page = get_or_404(self.request.allowable(StaticPage), StaticPage.id==self.request.matchdict["child_id"])
        copied = copy.copy(static_page)
        copied.label += u"のコピー"
        DBSession.add(copied)
        DBSession.flush()
        static_directory = get_static_page_utility(self.request)
        static_directory.copy(static_directory.get_rootname(static_page), 
                              static_directory.get_rootname(copied))
        return HTTPFound(self.context.endpoint(static_page))


    @view_config(match_param="action=toggle_publish")
    def toggle_publish(self):
        pk = self.request.matchdict["child_id"]
        static_page = get_or_404(self.request.allowable(StaticPage), StaticPage.id==pk)
        status = self.request.GET.get("status")
        if status == "publish":
            static_page.published = True
        elif status == "unpublish":
            static_page.published = False
        else:
            static_page.published = not static_page.published
        FlashMessage.success(u"このページを%sしました" % (u"公開" if static_page.published else u"非公開に"), request=self.request)
        return HTTPFound(self.context.endpoint(static_page))

    @view_config(match_param="action=delete", request_method="POST", renderer="json")
    def delete(self):
        pk = self.request.matchdict["child_id"]
        static_page = get_or_404(self.request.allowable(StaticPage), StaticPage.id==pk)
        deleter = self.context.creation(creation.StaticPageDelete)
        deleter.delete(static_page)
        FlashMessage.success(u"%sが削除されました" % static_page.name, request=self.request)
        return {"redirect_to": self.context.endpoint(static_page)}

    @view_config(match_param="action=download")
    def download(self):
        pk = self.request.matchdict["child_id"]
        static_page = get_or_404(self.request.allowable(StaticPage), StaticPage.id==pk)
        static_directory = get_static_page_utility(self.request)
        writename = static_directory.get_writename(static_page)
        with zipupload.current_directory(static_directory.get_rootname(static_page)):
            zipupload.create_zipfile_from_directory(".", writename)
        return download_response(path=writename,request=self.request, filename="{0}.zip".format(static_page.name)) 

@view_config(route_name="static_page_display", permission="authenticated")
def static_page_display_view(context, request):
    prefix = request.matchdict["path"].lstrip("/").split("/", 1)[0]
    static_page = get_or_404(request.allowable(StaticPage), StaticPage.name==prefix)
    static_directory = get_static_page_utility(request)
    try:
        path = os.path.join(static_directory.get_base_directory(), request.matchdict["path"])
        return as_static_page_response(request, static_page, path, force_original=request.GET.get("force_original"), 
                                       path=path, cache_max_age=0)
    except StaticPageNotFound as e:
        logger.info(e)
        raise HTTPForbidden()
