# coding: utf-8
import os.path
from altairsite.front import helpers as fh
from pyramid.view import view_config

from altaircms.layout.models import Layout
from .renderable import LayoutRender
from altaircms.auth.api import get_or_404

from altaircms.lib.crud.views import AfterInput
from pyramid.view import view_defaults
from pyramid.response import FileResponse
from altaircms.slackoff import forms
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from altaircms.helpers.viewhelpers import FlashMessage

from .creation import LayoutCreator, get_layout_filesession
from collections import defaultdict
import altaircms.helpers as h
from ..slackoff.mappers import layout_mapper
from ..page.models import PageType

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

    qs = request.allowable(Layout).filter_by(pagetype_id=pagetype_id)
    layouts = h.paginate(request, qs, item_count=qs.count())

    form = forms.LayoutCreateForm()
    return {"layouts": layouts, 
            "pagetypes": pagetypes, 
            "current_pagetype": current_pagetype, 
            "form": form, 
            "mapper": layout_mapper, 
            "display_fields": ["title", "template_filename"]}


@view_defaults(route_name="layout_create", 
               decorator="altaircms.lib.fanstatic_decorator.with_bootstrap")
class LayoutCreateView(object):
    def __init__(self, request):
        self.request = request
        self.context = request.context

    @view_config(match_param="action=input")
    def input(self):
        # self.context.set_endpoint() ##
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

        layout_creator = LayoutCreator(self.request, self.request.organization)
        layout = layout_creator.create(form.data, pagetype_id)
        FlashMessage.success("create layout %s" % layout.title, request=self.request)

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

        layout_creator = LayoutCreator(self.request, self.request.organization)
        layout = layout_creator.update(layout, form.data, pagetype_id)
        FlashMessage.success("update layout %s" % layout.title, request=self.request)
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
    template_path = os.path.join(get_layout_filesession(request).assetspec, layout.prefixed_template_filename)
    request.override_renderer = template_path
    blocks = defaultdict(list)
    class Page(object):
        title = layout.title
        keywords = layout.title
        description = "layout preview"
    return {"display_blocks": blocks, "page": Page, "myhelper": fh}

@view_config(route_name="layout_download")
def download(request):
    layout = get_or_404(request.allowable(Layout), Layout.id==request.matchdict["layout_id"])
    filesession = get_layout_filesession(request)
    path = filesession.abspath(layout.prefixed_template_filename)
    response = FileResponse(path)
    response.content_disposition = 'attachment; filename="%s"' % layout.template_filename
    return response
