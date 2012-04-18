# -*- coding:utf-8 -*-
import logging

from altaircms.models import DBSession
from altaircms.page.models import Page
from altaircms.layout.models import Layout
import altaircms.widget.tree.genpage as gen
from altaircms.widget.tree.proxy import WidgetTreeProxy
import sqlalchemy.orm.exc as saexc
import pyramid.exceptions as pyrexc
from altaircms.security import RootFactory

class PageRenderingResource(RootFactory):
    def get_unpublished_page(self, page_id):
        page = Page.query.filter(Page.id==page_id).one()
        page.to_unpublished()
        return page

    def get_page_and_layout(self, url):
        try:
            return DBSession.query(Page, Layout).filter(Page.layout_id==Layout.id).filter_by(url=url).filter_by(hash_url=None).one()
        except saexc.NoResultFound:
            raise pyrexc.NotFound(u'レイアウトが設定されていません。')

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
        from altaircms.widget.tree.block_context import BlockContext
        context =  BlockContext.from_widget_tree(WidgetTreeProxy(page), scan=True)
        context.blocks["keywords"] = [page.keywords]
        context.blocks["description"] = [page.description]
        context.blocks["title"] = [page.title]
        return context

    def get_layout_template(self, layout, config):
        return gen.get_layout_template(str(layout.template_filename), config)

