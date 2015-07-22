# -*- coding:utf-8 -*-
from pyramid.view import view_config
from pyramid.view import view_defaults
from altaircms.auth.api import get_or_404
from altaircms.auth.api import require_login
from altaircms.page.models import Page
from altaircms.plugins.widget.freetext.models import FreetextWidget
from altaircms.plugins.widget.image.models import ImageWidget
from xml.sax.saxutils import escape
import json

"""
DBアクセス減らすために、loginだけ確認して, organizationの確認をしていない。
TODO:本当にこれで良いか考える。

## todo: move it
"""

@view_defaults(custom_predicates=(require_login,), xhr=True)
class StructureView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name="structure_create", renderer="json", request_method="POST")
    def create(self):
        raise "create must not occur"

    @view_config(route_name="structure_update", renderer="json", request_method="POST")
    def update(self):
        request = self.request
        pk = request.json_body["page"]
        # page = get_or_404(request.allowPage("Page"), Page.id==pk)
        page = get_or_404(Page.query, Page.id==pk)
        page.structure = json.dumps(request.json_body["structure"])
        request.context.add(page, flush=True) ## flush?
        return "ok"

    @view_config(route_name="structure_get", renderer="json", request_method="GET")
    def get(self):
        request = self.request
        pk = request.GET["page"]
        # page = get_or_404(request.allowPage("Page"), Page.id==pk)
        page = get_or_404(Page.query, Page.id==pk)
        if page.structure:
            structure_dict = self.create_widget_detail(json.loads(page.structure))
            return dict(loaded=structure_dict)
        else:
            return dict(loaded=None)

    def create_widget_detail(self, structure_dict):
        for block in structure_dict:
            for widget in structure_dict[block]:
                widget['detail'] = u""
                if widget['name'] == u'freetext':
                    target_widget = self.request.allowable(FreetextWidget).filter(FreetextWidget.id==widget['pk']).first()
                    if target_widget:
                        widget['detail'] = escape(target_widget.text[0:200])
        return structure_dict