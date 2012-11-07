# coding: utf-8
from pyramid.view import view_config

from altaircms.layout.models import Layout
from .renderable import LayoutRender
from altaircms.auth.api import get_or_404

from altaircms.lib.crud.views import AfterInput
from pyramid.view import view_defaults
from pyramid.response import FileResponse
from altaircms.slackoff import forms
from . import subscribers 
from . import api

@view_config(route_name="layout_demo", renderer="altaircms:templates/layout/demo.mako")
def demo(request):
    layout = get_or_404(request.allowable(Layout), Layout.id==request.GET["id"])
    return dict(layout_image=LayoutRender(layout).blocks_image())

from ..layout.api import get_layout_creator
import os
from collections import defaultdict

@view_config(route_name="layout_preview", decorator="altaircms.lib.fanstatic_decorator.with_jquery", 
             renderer="dummy.mako")
def preview(context, request):
    layout_creator = get_layout_creator(request) ##
    layout = get_or_404(request.allowable(Layout), Layout.id==request.matchdict["layout_id"])
    template = os.path.join(layout_creator.template_path_asset_spec, layout.template_filename)
    request.override_renderer = template
    blocks = defaultdict(list)
    class Page(object):
        title = layout.title
        keywords = layout.title
        description = "layout preview"
    from altairsite.front import helpers as fh
    return {"display_blocks": blocks, "page": Page, "myhelper": fh}

@view_config(route_name="layout_download")
def download(request):
    layout = get_or_404(request.allowable(Layout), Layout.id==request.matchdict["layout_id"])
    path = api.get_layout_creator(request).get_layout_filepath(layout)
    return FileResponse(path)

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

    # @view_config(match_param="action=confirm", renderer="altaircms:templates/layout/create/confirm.mako")
    # def confirm(self):
    #     form = forms.LayoutCreateForm(self.request.POST)
    #     if not form.validate():
    #         self.request._form = form
    #         raise AfterInput
    #     else:
    #         return {"form": form, 
    #                 "display_fields": getattr(form, "__display_fields__")}

    @view_config(match_param="action=create")
    def create(self):
        form = forms.LayoutCreateForm(self.request.POST)
        form = api.get_layout_creator(self.request).as_form_proxy(form)
        if not form.validate():
            self.request._form = form
            raise AfterInput
        else:
            subscribers.notify_layout_create(self.request, form.data)
            from pyramid.httpexceptions import HTTPFound
            return HTTPFound(self.request.route_url("layout_list")) ##
        

