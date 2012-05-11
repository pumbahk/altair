# -*- coding:utf-8 -*-
import logging
from datetime import datetime
import sqlalchemy.orm.exc as saexc
import pyramid.exceptions as pyrexc
import sqlalchemy as sa

from altaircms.layout.models import Layout
from altaircms.page.models import Page
from altaircms.widget.tree.proxy import WidgetTreeProxy
from altaircms.models import Category

from ..models import DBSession
from .rendering import genpage as gen
from .rendering.block_context import BlockContext

class PageRenderingResource(object):
    def __init__(self, request):
        self.request = request

    def get_preview_date(self):
        if 'datetime' not in self.request.params:
            return datetime.now()
        else:
            dt = self.request.params['datetime']
            return datetime.strptime(dt, '%Y%m%d%H%M%S')

    def get_unpublished_page(self, page_id):
        page = Page.query.filter(Page.id==page_id).one()
        page.to_unpublished()
        return page

    def get_page_and_layout(self, url, dt):
        try:
            page = Page.query.filter(Page.url==url).filter(Page.in_term(dt)).one()
            return page, page.layout
        except saexc.NoResultFound:
            raise pyrexc.NotFound(u'page, url=%s and publish datetime = %s, is not found' % (url, dt))

    def get_page_and_layout_preview(self, url):
        try:
            return DBSession.query(Page, Layout).filter(Page.layout_id==Layout.id).filter_by(hash_url=url).one()
        except saexc.NoResultFound:
            raise pyrexc.NotFound(u'レイアウトが設定されていません。')

    def get_render_config(self):
        return gen.get_config(self.request)

    def get_performances(self, page):
        return page.event.performances if page.event else []

    def get_tickets(self, page):
        return page.event.tickets if page.event else []

    def get_block_context(self, page):
        context =  BlockContext.from_widget_tree(WidgetTreeProxy(page), scan=True)
        context.blocks["keywords"] = [page.keywords]
        context.blocks["description"] = [page.description]
        context.blocks["title"] = [page.title]
        return context

    def get_layout_template(self, layout, config):
        return gen.get_layout_template(str(layout.template_filename), config)

    def get_categories(self, hierarchy=u"大"):
        return Category.get_toplevel_categories(hierarchy=hierarchy, request=self.request).order_by(sa.asc("orderno"))

