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
from pyramid.httpexceptions import HTTPFound
from altaircms.helpers.viewhelpers import FlashMessage

from .creation import LayoutCreator, get_layout_filesession
from collections import defaultdict


@view_config(route_name="layout_demo", renderer="altaircms:templates/layout/demo.mako")
def demo(request):
    layout = get_or_404(request.allowable(Layout), Layout.id==request.GET["id"])
    data = dict(layout_image=LayoutRender(layout).blocks_image())
    return data


@view_config(route_name="layout_preview", decorator="altaircms.lib.fanstatic_decorator.with_jquery", 
             renderer="dummy.mako")
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
    path = LayoutCreator(request, layout.organization).get_layout_filepath(layout)
    response = FileResponse(path)
    response.content_disposition = 'attachment; filename="%s"' % layout.template_filename
    return response



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

    @view_config(context=AfterInput, renderer="altaircms:templates/layout/create/input.mako")
    def _after_input(self):
        form = self.request._form
        return {"form": form, 
                "display_fields": getattr(form, "__display_fields__")}

    @view_config(match_param="action=create")
    def create(self):
        form = forms.LayoutCreateForm(self.request.POST)
        if not form.validate():
            self.request._form = form
            raise AfterInput

        layout_creator = LayoutCreator(self.request, self.request.organization)
        layout = layout_creator.create(form.data)
        FlashMessage.success("create layout %s" % layout.title, request=self.request)
        return HTTPFound(self.request.route_url("layout_list")) ##

@view_defaults(route_name="layout_update", 
               decorator="altaircms.lib.fanstatic_decorator.with_bootstrap")
class LayoutUpdateView(object):
    def __init__(self, request):
        self.request = request
        self.context = request.context

    @view_config(match_param="action=input")
    def input(self):
        layout = get_or_404(self.request.allowable(Layout), Layout.id==self.request.matchdict["id"])
        self.request._form = forms.LayoutUpdateForm(title=layout.title, 
                                                    blocks=layout.blocks, 
                                                    template_filename=layout.template_filename
                                                    )
        raise AfterInput

    @view_config(context=AfterInput, renderer="altaircms:templates/layout/update/input.mako")
    def _after_input(self):
        form = self.request._form
        return {"form": form, 
                "display_fields": getattr(form, "__display_fields__")}

    @view_config(match_param="action=update")
    def update(self):
        layout = get_or_404(self.request.allowable(Layout), Layout.id==self.request.matchdict["id"])
        form = forms.LayoutUpdateForm(self.request.POST)
        if not form.validate():
            self.request._form = form
            raise AfterInput

        layout_creator = LayoutCreator(self.request, self.request.organization)
        layout = layout_creator.update(layout, form.data)
        FlashMessage.success("update layout %s" % layout.title, request=self.request)
        return HTTPFound(self.request.route_url("layout_list")) ##
