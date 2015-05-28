# -*- coding:utf-8 -*-
import os.path
from altairsite.front import helpers as fh
from pyramid.view import view_config
from pyramid.decorator import reify

from altaircms.layout.models import Layout
from .renderable import LayoutRender
from altaircms.auth.api import get_or_404, set_request_organization

from pyramid.view import view_defaults
from pyramid.response import FileResponse
from altaircms.slackoff import forms
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from altaircms.helpers.viewhelpers import FlashMessage

from .creation import LayoutCreator, LayoutUpdater, get_layout_filesession
from collections import defaultdict
import altaircms.helpers as h
from ..slackoff.mappers import layout_mapper
from ..page.models import PageType
from ..front.api import get_frontpage_discriptor_resolver
from ..front.api import get_frontpage_renderer
from altaircms.helpers.viewhelpers import get_endpoint
import logging
logger = logging.getLogger(__name__)

class AfterInput(Exception):
    def __init__(self, form=None, context=None):
        self.form = form
        self.context = context

@view_config(route_name="layout_detail", renderer="altaircms:templates/layout/detail.html", 
             decorator="altaircms.lib.fanstatic_decorator.with_bootstrap")
def layout_detail(context, request):
    obj = get_or_404(request.allowable(Layout), Layout.id==request.matchdict["layout_id"])
    return {"obj": obj}

from altaircms.models import DBSession
from altaircms.datelib import get_now

@view_config(route_name="layout_sync", renderer="altaircms:templates/layout/sync.html", 
             decorator="altaircms.lib.fanstatic_decorator.with_bootstrap")
def layout_sync(context, request):
    obj = get_or_404(request.allowable(Layout), Layout.id==request.matchdict["layout_id"])
    obj.synced_at = get_now(request)
    DBSession.add(obj)
    FlashMessage.success("sync layout id=%s synced_at=%s" % (obj.id, obj.synced_at), request=request)
    return HTTPFound(get_endpoint(request) or request.route_path("layout_list"))

@view_config(route_name="layout_list")
def layout_list(context, request):
    pagetype = request.allowable(PageType).first()
    if pagetype is None:
        raise HTTPNotFound
    return HTTPFound(request.route_path("layout_list_with_pagetype", pagetype_id=pagetype.id))

@view_config(route_name="layout_list_with_pagetype", renderer="altaircms:templates/layout/list.html", 
             decorator="altaircms.lib.fanstatic_decorator.with_bootstrap")
def layout_list_with_pagetype(context, request):
    pagetype_id = request.matchdict["pagetype_id"]
    pagetypes = request.allowable(PageType)
    current_pagetype = get_or_404(request.allowable(PageType), PageType.id==pagetype_id)
    qs = request.allowable(Layout).with_transformation(Layout.get_in_order(pagetype_id))
    layouts = h.paginate(request, qs, item_count=qs.count())

    form = forms.LayoutListForm()
    return {"layouts": layouts, 
            "pagetypes": pagetypes, 
            "current_pagetype": current_pagetype, 
            "form": form, 
            "mapper": layout_mapper, 
            "display_fields": ["title", "template_filename", "blocks", "updated_at", "synced_at", "display_order"]}


@view_defaults(route_name="layout_create", 
               decorator="altaircms.lib.fanstatic_decorator.with_bootstrap")
class LayoutCreateView(object):
    def __init__(self, request):
        self.request = request
        self.context = request.context

    @view_config(match_param="action=input")
    def input(self):
        self.request._form = forms.LayoutCreateForm()
        raise AfterInput

    @view_config(context=AfterInput, renderer="altaircms:templates/layout/create/input.html")
    def _after_input(self):
        form = self.request._form
        pagetype_id = self.request.matchdict["pagetype_id"]
        current_pagetype = get_or_404(self.request.allowable(PageType), PageType.id==pagetype_id)
        return {"form": form, 
                "current_pagetype": current_pagetype, 
                "display_fields": getattr(form, "__display_fields__")}

    @view_config(match_param="action=create")
    def create(self):
        form = forms.LayoutCreateForm(self.request.POST)
        pagetype_id=self.request.matchdict["pagetype_id"]
        if not form.validate():
            self.request._form = form
            raise AfterInput

        try:
            layout_creator = LayoutCreator(self.request, self.request.organization)
            layout = layout_creator.create(form.data, pagetype_id)
        except Exception, e:
            logger.error(str(e))
            FlashMessage.error(str(e), request=self.request)            
            self.request._form = form
            raise AfterInput

        url = self.request.route_path("layout_detail", layout_id=layout.id)
        mes = u'%sを作成しました <a href="%s">新しく作成されたデータを編集</a>' % (u"レイアウト", url)
        FlashMessage.success(mes, request=self.request)
        return HTTPFound(self.request.route_url("layout_list_with_pagetype", pagetype_id=pagetype_id)) ##

@view_defaults(route_name="layout_update", 
               decorator="altaircms.lib.fanstatic_decorator.with_bootstrap")
class LayoutUpdateView(object):
    def __init__(self, request):
        self.request = request
        self.context = request.context

    @view_config(match_param="action=input")
    def input(self):
        pagetype_id=self.request.matchdict["pagetype_id"]
        layout = get_or_404(self.request.allowable(Layout), Layout.id==self.request.matchdict["id"])
        self.request._form = forms.LayoutUpdateForm(title=layout.title, 
                                                    blocks=layout.blocks, 
                                                    template_filename=layout.template_filename,
                                                    display_order=layout.display_order,
                                                    pagetype_id=pagetype_id
                                                    )
        raise AfterInput

    @view_config(context=AfterInput, renderer="altaircms:templates/layout/update/input.html")
    def _after_input(self):
        form = self.request._form
        pagetype_id = self.request.matchdict["pagetype_id"]
        current_pagetype = get_or_404(self.request.allowable(PageType), PageType.id==pagetype_id)
        return {"form": form, 
                "current_pagetype": current_pagetype, 
                "display_fields": getattr(form, "__display_fields__")}

    @view_config(match_param="action=update")
    def update(self):
        form = forms.LayoutUpdateForm(self.request.POST)
        layout = get_or_404(self.request.allowable(Layout), Layout.id==self.request.matchdict["id"])
        pagetype_id=self.request.matchdict["pagetype_id"]
        if not form.validate():
            self.request._form = form
            raise AfterInput
        try:
            layout_updater = LayoutUpdater(self.request, self.request.organization)
            layout = layout_updater.update(layout, form.data, pagetype_id)
        except Exception, e:
            logger.error(str(e))
            FlashMessage.error(str(e), request=self.request)            
            self.request._form = form
            raise AfterInput
            
        url = self.request.route_path("layout_detail", layout_id=layout.id)
        mes = u'%sを編集しました <a href="%s">変更されたデータを編集</a>' % (u"レイアウト", url)
        FlashMessage.success(mes, request=self.request)
        return HTTPFound(self.request.route_url("layout_list_with_pagetype", pagetype_id=pagetype_id)) ##


@view_config(route_name="layout_demo", renderer="altaircms:templates/layout/demo.html")
def demo(request):
    layout = get_or_404(request.allowable(Layout), Layout.id==request.GET["id"])
    data = dict(layout_image=LayoutRender(layout).blocks_image())
    return data


@view_config(route_name="layout_preview", decorator="altaircms.lib.fanstatic_decorator.with_jquery", 
             renderer="dummy.html")
def preview(context, request):
    layout = get_or_404(request.allowable(Layout), Layout.id==request.matchdict["layout_id"])
    set_request_organization(request, layout.organization_id)
    real_layout_file = RealLayoutFile(request, layout)
    real_layout_file.abspath() #xxx:

    resolver = get_frontpage_discriptor_resolver(request)
    discriptor = resolver.resolve(request, layout, verbose=True)
    if not discriptor.exists():
        raise HTTPNotFound("template file %s is not found" % discriptor.abspath()) 

    blocks = defaultdict(list)
    class Page(object):
        title = layout.title
        keywords = layout.title
        description = "layout preview"
    renderer = get_frontpage_renderer(request)
    params = {"display_blocks": blocks, "page": Page, "myhelper": fh}
    return renderer._render(discriptor.absspec(), layout, params)

@view_config(route_name="layout_download")
def download(request):
    layout = get_or_404(request.allowable(Layout), Layout.id==request.matchdict["layout_id"])
    real_layout_file = RealLayoutFile(request, layout)
    response = FileResponse(real_layout_file.abspath())
    response.content_disposition = 'attachment; filename="%s"' % layout.template_filename
    return response

from . import SESSION_NAME
from altaircms.filelib.s3 import s3load_to_filename

def s3download_layout(request, layout, abspath):
    uri = "{}/{}".format(SESSION_NAME, layout.prefixed_template_filename)
    s3load_to_filename(request, uri, abspath)

class RealLayoutFile(object):
    def __init__(self, request, layout, download=s3download_layout):
        self.request = request
        self.layout = layout
        self.download = download

    @reify
    def filesession(self):
        return get_layout_filesession(self.request)

    def _abspath(self):
        return self.filesession.abspath(self.layout.prefixed_template_filename)

    def abspath(self):
        abspath = self._abspath()
        if not os.path.exists(abspath):
            logger.info("*layout* layout does not exists. download it. (file:{})".format(abspath))
            dirpath = os.path.dirname(abspath)
            if not os.path.exists(dirpath):
                os.makedirs(dirpath)
            self.download(self.request, self.layout, abspath)
        return abspath
