# -*- coding:utf-8 -*-

from altaircms.models import DBSession
from altaircms.page.models import Page
from altaircms.layout.models import Layout
from . import generate as gen
from altaircms.widget.generate import WidgetTreeProxy
import sqlalchemy.orm.exc as saexc
import pyramid.exceptions as pyrexc


class PageRenderingResource(object):
    def __init__(self, request):
        self.request = request

    def get_page_and_layout(self, url):
        try:
            return DBSession.query(Page, Layout).filter(Page.layout_id==Layout.id).filter_by(url=url).one()
        except saexc.NoResultFound:
            raise pyrexc.NotFound(u'レイアウトが設定されていません。')

    def get_render_config(self):
        return gen.get_config(self.request)

    def get_render_tree(self, page):
        return gen.get_pagerender_tree(WidgetTreeProxy(page))

    def get_layout_template(self, layout, config):
        return gen.get_layout_template(str(layout.template_filename), config)

