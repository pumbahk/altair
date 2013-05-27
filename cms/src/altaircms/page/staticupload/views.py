#-*- coding:utf-8 -*-
import copy
import shutil
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
from altaircms.page.models import StaticPageSet, StaticPage, PageType
from . import forms
from . import creation
from .renderable import static_page_directory_renderer
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
        pagetype = get_or_404(self.request.allowable(PageType), PageType.name==self.request.matchdict["pagetype"])
        static_page = creator.create()

        try:
            static_page.pageset.pagetype = pagetype
            FlashMessage.success(u"%sが作成されました" % static_page.label, request=self.request)
            return HTTPFound(self.context.endpoint(static_page))
        except Exception as e:
            logger.exception(e)
            FlashMessage.error(str(e), request=self.request)
            creator.rollback()
            return {"form": form}

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
                "pagetype": static_pageset.pagetype, 
                "static_directory": static_directory, 
                "current_page": static_pageset.current(), 
                "tree_renderer": static_page_directory_renderer(self.request, static_page, static_directory, self.request.GET.get("management")), 
                "now": get_now(self.request)}


@view_defaults(route_name="static_page_part_file", permission="authenticated")
class StaticPagePartFileView(BaseView):
    @view_config(match_param="action=delete", request_method="GET", renderer="altaircms:templates/page/static_page_part_input.html", 
                 decorator=with_bootstrap)
    def delete_file_input(self):
        path = self.request.matchdict["path"].lstrip("/")
        form = forms.StaticFileDeleteForm(name=path)
        return {"title": u"ファイルの削除", 
                "form": form, 
                "fields": ["name"], 
                "message": u"ファイル「{0}」を削除します".format(path), 
                "submit_message": u"ファイルを削除"
                }

    @view_config(match_param="action=delete", request_method="POST", renderer="altaircms:templates/page/static_page_part_input.html", 
                 decorator=with_bootstrap)
    def delete_file(self):
        path = self.request.matchdict["path"]
        form = forms.StaticFileDeleteForm(self.request.POST)
        static_page = get_or_404(self.request.allowable(StaticPage), StaticPage.id==self.request.matchdict["child_id"])
        def _retry(message=None):
            if message:
                form.errors["name"] = [message]
            return {"title": u"ファイルの削除", 
                    "form": form, 
                    "fields": ["name"], 
                    "message": u"ファイル「{0}」を削除します".format(path), 
                    "submit_message": u"ファイルを削除"
                    }
        try:
            if not form.validate():
                return _retry()
            changer = self.context.creation(creation.PartialChange, form.data)
            changer.delete_file(static_page)
            self.context.touch(static_page)
            return HTTPFound(self.context.endpoint(static_page))
        except Exception as e:
            logger.exception(str(e))
            return _retry(unicode(e))

    @view_config(match_param="action=create", request_method="GET", renderer="altaircms:templates/page/static_page_part_input.html", 
                 decorator=with_bootstrap)
    def add_file_input(self):
        form = forms.StaticFileAddForm()
        return {"title": u"ファイルの追加", 
                "form": form, 
                "fields": ["name","file"], 
                "submit_message": u"ファイルを追加"
                }

    @view_config(match_param="action=create", request_method="POST", renderer="altaircms:templates/page/static_page_part_input.html", 
                 decorator=with_bootstrap)
    def add_file(self):
        form = forms.StaticFileAddForm(self.request.POST)
        static_page = get_or_404(self.request.allowable(StaticPage), StaticPage.id==self.request.matchdict["child_id"])
        def _retry(message=None):
            if message:
                form.errors["file"] = [message]
            return {"title": u"ファイルの追加", 
                    "form": form, 
                    "fields": ["name","file"], 
                    "submit_message": u"ファイルを追加"
                    }
        try:
            if not form.validate():
                return _retry()
            changer = self.context.creation(creation.PartialChange, form.data)
            changer.create_file(static_page)
            self.context.touch(static_page)
            return HTTPFound(self.context.endpoint(static_page))
        except Exception as e:
            logger.exception(str(e))
            return _retry(unicode(e))

    @view_config(match_param="action=update", request_method="GET", renderer="altaircms:templates/page/static_page_part_input.html", 
                 decorator=with_bootstrap)
    def update_file_input(self):
        form = forms.StaticFileUpdateForm(name=self.request.matchdict["path"].lstrip("/"))
        return {"title": u"ファイルの更新", 
                "form": form, 
                "fields": ["name", "file"], 
                "submit_message": u"ファイルを更新"
                }

    @view_config(match_param="action=update", request_method="POST", renderer="altaircms:templates/page/static_page_part_input.html", 
                 decorator=with_bootstrap)
    def update_file(self):
        form = forms.StaticFileUpdateForm(self.request.POST)
        static_page = get_or_404(self.request.allowable(StaticPage), StaticPage.id==self.request.matchdict["child_id"])
        def _retry(message=None):
            if message:
                form.errors["name", "file"] = [message]
            return {"title": u"ファイルの更新", 
                    "form": form, 
                    "fields": ["file"], 
                    "submit_message": u"ファイルを更新"
                    }
        try:
            if not form.validate():
                return _retry()
            changer = self.context.creation(creation.PartialChange, form.data)
            changer.update_file(static_page)
            self.context.touch(static_page)
            return HTTPFound(self.context.endpoint(static_page))
        except Exception as e:
            logger.exception(str(e))
            return _retry(unicode(e))


@view_defaults(route_name="static_page_part_directory", permission="authenticated")
class StaticPagePartDirectoryView(BaseView):
    @view_config(match_param="action=create", request_method="GET", renderer="altaircms:templates/page/static_page_part_input.html", 
                 decorator=with_bootstrap)
    def add_directory_input(self):
        form = forms.StaticDirectoryAddForm()
        return {"title": u"ディレクトリの追加", 
                "form": form, 
                "fields": ["name"], 
                "submit_message": u"ディレクトリを追加"
                }

    @view_config(match_param="action=create", request_method="POST", renderer="altaircms:templates/page/static_page_part_input.html", 
                 decorator=with_bootstrap)
    def add_directory(self):
        form = forms.StaticDirectoryAddForm(self.request.POST)
        static_page = get_or_404(self.request.allowable(StaticPage), StaticPage.id==self.request.matchdict["child_id"])
        def _retry(message=None):
            if message:
                form.errors["name"] = [message]
            return {"title": u"ディレクトリの追加", 
                    "form": form, 
                    "fields": ["name"], 
                    "submit_message": u"ディレクトリを追加"
                    }
        try:
            if not form.validate():
                return _retry()
            changer = self.context.creation(creation.PartialChange, form.data)
            changer.create_directory(static_page)
            self.context.touch(static_page)
            return HTTPFound(self.context.endpoint(static_page))
        except Exception as e:
            logger.exception(str(e))
            return _retry(unicode(e))

    @view_config(match_param="action=delete", request_method="GET", renderer="altaircms:templates/page/static_page_part_input.html", 
                 decorator=with_bootstrap)
    def delete_directory_input(self):
        path = self.request.matchdict["path"].lstrip("/")
        form = forms.StaticDirectoryDeleteForm(name=path)
        return {"title": u"ディレクトリの削除", 
                "form": form, 
                "fields": ["name"], 
                "message": u"ディレクトリ「{0}」を削除します".format(path), 
                "submit_message": u"ディレクトリを削除"
                }

    @view_config(match_param="action=delete", request_method="POST", renderer="altaircms:templates/page/static_page_part_input.html", 
                 decorator=with_bootstrap)
    def delete_directory(self):
        path = self.request.matchdict["path"]
        form = forms.StaticDirectoryDeleteForm(self.request.POST)
        static_page = get_or_404(self.request.allowable(StaticPage), StaticPage.id==self.request.matchdict["child_id"])
        def _retry(message=None):
            if message:
                form.errors["file"] = [message]
            return {"title": u"ディレクトリの削除", 
                    "form": form, 
                    "fields": ["name"], 
                    "message": u"ディレクトリ「{0}」を削除します".format(path), 
                    "submit_message": u"ディレクトリを削除"
                    }
        try:
            if not form.validate():
                return _retry()
            changer = self.context.creation(creation.PartialChange, form.data)
            changer.delete_directory(static_page)
            self.context.touch(static_page)
            return HTTPFound(self.context.endpoint(static_page))
        except Exception as e:
            logger.exception(str(e))
            return _retry(unicode(e))


@view_defaults(route_name="static_page", permission="authenticated")
class StaticPageView(BaseView):
    @view_config(match_param="action=shallow_copy")
    def shallow_copy(self):
        static_page = get_or_404(self.request.allowable(StaticPage), StaticPage.id==self.request.matchdict["child_id"])
        copied = self.context.touch(copy.copy(static_page))
        copied.label += u"のコピー"
        DBSession.flush()
        static_directory = get_static_page_utility(self.request)
        static_directory.prepare(static_directory.get_rootname(copied))
        FlashMessage.success(u"ページをコピーしました", request=self.request)
        return HTTPFound(self.context.endpoint(static_page))


    @view_config(match_param="action=deep_copy")
    def deep_copy(self):
        static_page = get_or_404(self.request.allowable(StaticPage), StaticPage.id==self.request.matchdict["child_id"])
        copied = self.context.touch(copy.copy(static_page))
        copied.label += u"のコピー"
        DBSession.add(copied)
        DBSession.flush()
        static_directory = get_static_page_utility(self.request)
        static_directory.copy(static_directory.get_rootname(static_page), 
                              static_directory.get_rootname(copied))

        static_directory = get_static_page_utility(self.request)
        absroot = static_directory.get_rootname(copied)
        self.request.registry.notify(creation.AfterModelCreate(self.request, absroot, static_directory, copied))
        FlashMessage.success(u"ページを再帰的にコピーしました", request=self.request)
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
        FlashMessage.success(u"%sが削除されました" % static_page.prefix, request=self.request)
        return {"redirect_to": self.context.endpoint(static_page)}

    @view_config(match_param="action=download")
    def download(self):
        pk = self.request.matchdict["child_id"]
        static_page = get_or_404(self.request.allowable(StaticPage), StaticPage.id==pk)
        static_directory = get_static_page_utility(self.request)
        writename = static_directory.get_writename(static_page)
        with zipupload.current_directory(static_directory.get_rootname(static_page)):
            zipupload.create_zipfile_from_directory(".", writename)
        return download_response(path=writename,request=self.request, filename="{0}.zip".format(static_page.prefix)) 

    @view_config(match_param="action=upload", request_param="zipfile", request_method="POST")
    def upload(self):
        pk = self.request.matchdict["child_id"]
        static_page = get_or_404(self.request.allowable(StaticPage), StaticPage.id==pk)
        form = self.context.form(forms.StaticUploadOnlyForm, self.request.POST)
        if not form.validate():
            FlashMessage.error(form.errors["zipfile"][0], request=self.request)
            raise HTTPFound(self.context.endpoint(static_page))

        creator = self.context.creation(creation.StaticPageCreate, form.data)
        try:
            creator.update_underlying_something(static_page)
        except:
            FlashMessage.error(u"更新に失敗しました", request=self.request)
            raise HTTPFound(self.context.endpoint(static_page))

        self.context.touch(static_page)
        FlashMessage.success(u"%sが更新されました" % static_page.prefix, request=self.request)
        return HTTPFound(self.context.endpoint(static_page))


@view_config(route_name="static_page_display", permission="authenticated")
def static_page_display_view(context, request):
    static_page = get_or_404(request.allowable(StaticPage), StaticPage.id==request.matchdict["child_id"])
    static_directory = get_static_page_utility(request)
    try:
        path = os.path.join(static_directory.get_base_directory(), request.matchdict["path"])
        return as_static_page_response(request, static_page, path, force_original=request.GET.get("force_original"), 
                                       path=path, cache_max_age=0)
    except StaticPageNotFound as e:
        logger.info(e)
        raise HTTPForbidden()
