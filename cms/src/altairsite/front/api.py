# -*- coding:utf-8 -*-
from datetime import datetime
import sqlalchemy as sa
from altaircms.tag.models import HotWord

from pyramid.renderers import render_to_response
from .rendering import genpage as gen
from altaircms.widget.tree.proxy import WidgetTreeProxy
from .rendering.bsettings import BlockSettings
from . import helpers as h


def get_current_hotwords(request, _nowday=datetime.now):
    today = _nowday()
    qs =  HotWord.query.filter(HotWord.term_begin <= today).filter(today <= HotWord.term_end)
    qs = qs.filter_by(enablep=True).order_by(sa.asc("orderno"), sa.asc("term_end"))
    return qs

def get_frontpage_render(request):
    return FrontPageRenderer(request)


"""
todo: 複数の種類に分ける
"""
class FrontPageRenderer(object):
    def __init__(self, request):
        self.request = request

    def render(self, page):
        bsettings = self.get_bsettings(page)
        tmpl = self.get_layout_template()
        params = self.build_render_params(page)
        params.update(page=page, display_blocks=bsettings.blocks)
        return render_to_response(tmpl, params, self.request)

    def get_bsettings(self, page):
        bsettings = BlockSettings.from_widget_tree(WidgetTreeProxy(page))
        bsettings.blocks["description"] = [page.description]
        bsettings.blocks["title"] = [page.title]

        event = page.event
        performances=h.get_performances(event)
        bsettings.scan(self.request, page=page, performances=performances, event=event)
        return bsettings

    def get_layout_template(self, page):
        layout = page.layout
        config = gen.get_config(self.request)
        return gen.get_layout_template(str(layout.template_filename), config)

    def build_render_params(self, page):
        params = h.get_navigation_categories(self.request)
        params.update(sub_categories=h.get_subcategories_from_page(self.request, page))
        return params
