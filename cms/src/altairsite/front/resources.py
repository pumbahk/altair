# -*- coding:utf-8 -*-
import logging
from datetime import datetime
import sqlalchemy.orm.exc as saexc
import pyramid.exceptions as pyrexc
import sqlalchemy as sa

from altaircms.layout.models import Layout
from altaircms.page.models import Page
from altaircms.page.models import PageSet
from altaircms.widget.tree.proxy import WidgetTreeProxy
from altaircms.models import Category

from ..models import DBSession
from .rendering import genpage as gen
from .rendering.bsettings import BlockSettings

class PageRenderingResource(object):
    def __init__(self, request):
        self.request = request

    def get_preview_date(self):
        if 'datetime' not in self.request.params:
            return datetime.now()
        else:
            dt = self.request.params['datetime']
            return datetime.strptime(dt, '%Y%m%d%H%M%S')

    def get_pageset_query_from_url(self, url, dt):
        return PageSet.query.filter(
            PageSet.url==url).filter(
            Page.pageset_id==PageSet.id).filter(
                Page.in_term(dt))

    def get_unpublished_page(self, page_id):
        page = Page.query.filter(Page.id==page_id).one()
        page.to_unpublished()
        return page

    def get_page_and_layout(self, url, dt):
        page = Page.query.filter(Page.url==url).filter(Page.in_term(dt)).order_by("page.publish_begin").first()
        if page is None:
            raise pyrexc.NotFound(u'page, url=%s and publish datetime = %s, is not found' % (url, dt))
        return page, page.layout

    def get_page_and_layout_preview(self, url, page_id):
        try:
            page = Page.query.filter(Page.hash_url==url, Page.id==page_id).one()
            return page, page.layout
        except saexc.NoResultFound:
            raise pyrexc.NotFound(u'page, url=%s and is not found' % (url))


    def get_render_config(self):
        return gen.get_config(self.request)

    def get_performances(self, page):
        return page.event.performances if page.event else []
    
    def get_bsettings(self, page):
        context =  BlockSettings.from_widget_tree(WidgetTreeProxy(page), scan=True)
        context.blocks["description"] = [page.description]
        context.blocks["title"] = [page.title]
        return context

    def get_layout_template(self, layout, config):
        return gen.get_layout_template(str(layout.template_filename), config)

    def get_categories(self, hierarchy=u"大"):
        return Category.get_toplevel_categories(hierarchy=hierarchy, request=self.request).order_by(sa.asc("orderno"))

