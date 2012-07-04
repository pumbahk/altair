# coding: utf-8
from pyramid.view import view_config

from altaircms.layout.models import Layout
from .renderable import LayoutRender
from altaircms.auth.api import get_or_404

@view_config(route_name="layout_demo", renderer="altaircms:templates/layout/demo.mako")
def demo(request):
    layout = get_or_404(request.allowable("Layout"), Layout.id==request.GET["id"])
    return dict(layout_image=LayoutRender(layout).blocks_image())
