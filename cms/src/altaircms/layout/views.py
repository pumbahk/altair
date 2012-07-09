# coding: utf-8
from pyramid.view import view_config

from altaircms.layout.models import Layout
from .renderable import LayoutRender
from altaircms.auth.api import get_or_404


from altaircms.lib.crud.views import AfterInput
from pyramid.view import view_defaults
from altaircms.slackoff import forms
from . import subscribers 

@view_config(route_name="layout_demo", renderer="altaircms:templates/layout/demo.mako")
def demo(request):
    layout = get_or_404(request.allowable(Layout), Layout.id==request.GET["id"])
    return dict(layout_image=LayoutRender(layout).blocks_image())

@view_defaults(route_name="layout_create", 
               decorator="altaircms.lib.fanstatic_decorator.with_bootstrap")
class LayoutCreateView(object):
    def __init__(self, request):
        self.request = request
        self.context = request.context

    # @view_config(match_param="action=input")
    # def input(self):
    #     # self.context.set_endpoint() ##
    #     form = forms.LayoutCreateForm()
    #     raise AfterInput(form=form, context=self.request.context)

    # @view_config(context=AfterInput, renderer="altaircms:lib/layout/create/input.mako")
    # def _after_input(self):
    #     form = self.request.context.form
    #     return {"master_env": self.context.context, 
    #             "form": form, 
    #             "display_fields": getattr(form, "__display_fields__")}

    @view_config(match_param="action=input", renderer="altaircms:templates/layout/create/input.mako")
    def input(self):
        # self.context.set_endpoint() ##
        form = forms.LayoutCreateForm()
        return {"master_env": self.context, 
                "form": form, 
                "display_fields": getattr(form, "__display_fields__")}

    @view_config(match_param="action=create", renderer="altaircms:templates/layout/create/input.mako")
    def create(self):
        form = forms.LayoutCreateForm(self.request.POST)

        if not form.validate():
            return {"master_env": self.context, 
                    "form": form, 
                    "display_fields": getattr(form, "__display_fields__")}
        else:
            subscribers.notify_layout_create(self.request, form.data)
            from pyramid.httpexceptions import HTTPFound
            return HTTPFound("/") ##
        

