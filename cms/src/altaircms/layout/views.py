# coding: utf-8
from pyramid.view import view_config

from altaircms.models import DBSession
from altaircms.layout.models import Layout
from .renderable import LayoutRender

@view_config(route_name="layout_demo", renderer="altaircms:templates/layout/demo.mako")
def demo(request):
    id_ = request.GET["id"]
    layout = DBSession.query(Layout).get(id_)
    return dict(layout_image=LayoutRender(layout).blocks_image())
