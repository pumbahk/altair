#-*- coding:utf-8 -*-
import copy
import os
from pyramid.httpexceptions import HTTPFound, HTTPForbidden, HTTPNotFound
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
from .download import ZippedStaticFileManager, S3Downloader
from .renderable import static_page_directory_renderer
from .refine import refine_link_on_download_factory
import logging
logger = logging.getLogger(__name__)
from altaircms.viewlib import BaseView
from altaircms.datelib import get_now
from altaircms.modellib import first_or_nullmodel
from . import StaticUploadAssertionError

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
        try:
            static_page = creator.create()
            static_page.pageset.pagetype = pagetype
            FlashMessage.success(u"%sが作成されました" % static_page.label, request=self.request)
            return HTTPFound(self.context.endpoint(static_page))
        except StaticUploadAssertionError as e:
            FlashMessage.error(unicode(e.args[0]), request=self.request)
            creator.rollback()
            return {"form": form}
        except Exception as e:
            logger.exception(e)
            FlashMessage.error(u"作成に失敗しました。(ファイル名に日本語などのマルチバイト文字が含まれている時に失敗することがあります)", request=self.request)
            creator.rollback()
            return {"form": form}

@view_defaults(route_name="static_pageset", permission="authenticated")
class StaticPageSetView(BaseView):
    @view_config(match_param="action=detail", renderer="altaircms:templates/page/static_detail.html", 
                 decorator=with_bootstrap)
    def detail(self):
        pk = self.request.matchdict["static_page_id"]
        static_pageset = get_or_404(self.request.allowable(StaticPageSet), StaticPageSet.id==pk)
        static_pageset.pages.sort(key=lambda page: page.created_at, reverse=True)
        static_directory = get_static_page_utility(self.request)
        current_page = static_pageset.current(dt=get_now(self.request))
        if self.request.GET.get("child_id"):
            active_page = StaticPage.query.filter_by(pageset=static_pageset, id=self.request.GET.get("child_id")).first()
        # 表示中のページをactiveにする
        elif current_page:
            active_page = current_page
        # 非公開ページしかもっていない場合は、最も新しいページをactiveにする
        else:
            if len(static_pageset.pages):
                active_page = static_pageset.pages[0]

        return {"static_pageset": static_pageset,
                "pagetype": static_pageset.pagetype,
                "static_directory": static_directory,
                "current_page": current_page,
                "tree_renderer": static_page_directory_renderer(self.request, active_page, static_directory, self.request.GET.get("management")),
                "now": get_now(self.request),
                "active_page": active_page}

    @view_config(match_param="action=preview", request_param="path", decorator=with_bootstrap)
    def preview(self):
        pk = self.request.matchdict["static_page_id"]
        now = get_now(self.request)
        static_pageset = get_or_404(self.request.allowable(StaticPageSet), StaticPageSet.id==pk)
        static_page = static_pageset.current(published=True, dt=now)
        if static_page is None:
            from pyramid.response import Response
            return Response(u"公開期間外です: 現在時刻={0}".format(now))
        static_directory = get_static_page_utility(self.request)
        try:
            path = os.path.join(static_directory.get_rootname(static_page), 
                                self.request.params["path"])
            logger.info(u"*path: {0}".format(path))
            return as_static_page_response(self.request, static_page, path, force_original=False, 
                                           path=path, cache_max_age=0)
        except StaticPageNotFound as e:
            logger.info(e)
            raise HTTPForbidden()
        


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
        except StaticUploadAssertionError as e:
            return _retry(unicode(e.args[0]))
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
                form.errors["file"] = [message]
            return {"title": u"ファイルの更新", 
                    "form": form, 
                    "fields": ["name", "file"], 
                    "submit_message": u"ファイルを更新"
                    }
        try:
            if not form.validate():
                return _retry()
            changer = self.context.creation(creation.PartialChange, form.data)
            changer.update_file(static_page)
            self.context.touch(static_page)
            return HTTPFound(self.context.endpoint(static_page))

        except StaticUploadAssertionError as e:
            return _retry(unicode(e.args[0]))
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

    @view_config(match_param="action=intercept", request_method="POST", renderer="json")
    def intercept(self):
        pk = self.request.matchdict["child_id"]
        static_page = get_or_404(self.request.allowable(StaticPage), StaticPage.id==pk)
        interceptr = self.context.creation(creation.StaticPageIntercept)
        interceptr.intercept(static_page)
        if static_page.interceptive:
            FlashMessage.success(u"%sの横取りを有効にしました" % static_page.label, request=self.request)
        else:
            FlashMessage.success(u"%sの横取りを無効にしました" % static_page.label, request=self.request)
        return {"redirect_to": self.context.endpoint(static_page)}

    @view_config(match_param="action=delete", request_method="POST", renderer="json")
    def delete(self):
        pk = self.request.matchdict["child_id"]
        static_page = get_or_404(self.request.allowable(StaticPage), StaticPage.id==pk)
        deleter = self.context.creation(creation.StaticPageDelete)
        deleter.delete(static_page)
        FlashMessage.success(u"%sが削除されました" % static_page.label, request=self.request)
        return {"redirect_to": self.context.endpoint(static_page)}

    @view_config(match_param="action=download")
    def download(self):
        pk = self.request.matchdict["child_id"]
        static_page = get_or_404(self.request.allowable(StaticPage), StaticPage.id==pk)
        static_directory = get_static_page_utility(self.request)
        s3prefix = os.path.join(static_directory.prefix, self.request.organization.short_name, static_page.prefix, unicode(static_page.id))

        downloader = S3Downloader(self.request, static_page, prefix=s3prefix) ## xxx:
        downloader.add_filter(refine_link_on_download_factory(static_page, static_directory))
        zm = ZippedStaticFileManager(self.request, static_page, static_directory.tmpdir, downloader=downloader)

        return zm.download_response(static_directory.get_rootname(static_page))

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
        except StaticUploadAssertionError as e:
            FlashMessage.error(unicode(e.args[0]), request=self.request)
            raise HTTPFound(self.context.endpoint(static_page))
        except Exception as e:
            logger.error(str(e))
            FlashMessage.error(u"更新に失敗しました。(ファイル名に日本語などのマルチバイト文字が含まれている時に失敗することがあります)", request=self.request)
            raise HTTPFound(self.context.endpoint(static_page))

        if self.request.user.screen_name:
            static_page.last_editor = self.request.user.screen_name

        self.context.touch(static_page)
        FlashMessage.success(u"%sが更新されました" % static_page.label, request=self.request)
        return HTTPFound(self.context.endpoint(static_page))


@view_config(route_name="static_page_display", permission="authenticated")
def static_page_display_view(context, request):
    static_page = get_or_404(request.allowable(StaticPage), StaticPage.id==request.matchdict["child_id"])
    static_directory = get_static_page_utility(request)
    try:
        path = os.path.join(static_directory.get_base_directory(), request.matchdict["path"])
        logger.info(u"*path: {0}".format(path))
        return as_static_page_response(request, static_page, path, force_original=request.GET.get("force_original"), 
                                       path=path, cache_max_age=0)
    except StaticPageNotFound as e:
        logger.info(e)
        raise HTTPNotFound(str(e))
