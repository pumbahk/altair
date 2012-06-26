# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__file__)

from datetime import datetime
import sqlalchemy as sa
from altaircms.page.models import Page
from altaircms.page.models import PageSet
from .api import FrontPageRenderer

class PageRenderingResource(object):
    def __init__(self, request):
        self.request = request

    def frontpage_renderer(self):
        return FrontPageRenderer(self.request)

    def pc_access_control(self):
        return AccessControlPC(self.request)

    def mobile_access_control(self):
        return AccessControlMobile(self.request)

    def get_preview_date(self):
        if 'datetime' not in self.request.params:
            return datetime.now()
        else:
            dt = self.request.params['datetime']
            return datetime.strptime(dt, '%Y%m%d%H%M%S')


"""
access controll object

レンダリング過程が複雑になったらここでrendererのdispatchする.
(今はresourceが持っている。)
"""
class AccessControlMobile(object):
    def __init__(self, request):
        self.request = request
        self.access_ok = False
        self.error_message = u"this-object-is-not-used" 

    def can_access(self):
        if not self.access_ok:
            logger.info("*front mobile access* url is not found (%s)" % self.request.referer) ## referer?
        return self.access_ok

    def _fetch_pageset_from_params(self, url, dt):
        qs = PageSet.query.filter(PageSet.id==Page.pageset_id)
        qs = qs.filter(PageSet.url==url)
        qs = qs.filter(Page.in_term(dt))
        qs = qs.filter(Page.published==True)
        return qs.first()

    def fetch_pageset_from_params(self, url, dt):
        pageset = self._fetch_pageset_from_params(url, dt)
        self.access_ok = True

        if pageset is None:
            self.error_message = u"*fetch pageset* url=%s pageset is not found" % url
            self.access_ok = False
            return pageset

        if pageset.event and pageset.event.is_searchable == False:
            self.error_message = u"*fetch pageset* pageset(id=%s) event is disabled event(is_searchable==False)"
            self.access_ok = False
        return pageset


class AccessControlPC(object):
    def __init__(self, request):
        self.request = request
        self.access_ok = False
        self.error_message = u"this-object-is-not-used" 

    def can_access(self):
        if not self.access_ok:
            logger.info("*front pc access* url is not found (%s)" % self.request.referer) ## referer
        return self.access_ok

    def _fetch_page_from_params(self, url, dt):
        qs = Page.query.filter(PageSet.id==Page.pageset_id)
        qs = qs.filter(PageSet.url==url)
        qs = qs.filter(Page.in_term(dt))
        qs = qs.filter(Page.published==True)
        return qs.order_by(sa.desc("page.publish_begin")).first()

    def fetch_page_from_params(self, url, dt):
        page = self._fetch_page_from_params(url, dt)
        self.access_ok = True

        if page is None:
            self.error_message = u"*fetch page* url=%s page is not found" % url
            self.access_ok = False
            return page

        if page.event and page.event.is_searchable == False:
            self.error_message = u"*fetch pageset* pageset(id=%s) event is disabled event(is_searchable==False)"
            self.access_ok = False
        if page.layout is None:
            self.error_message = u"*fetch page* url=%s page(id=%s) has not rendering layout" % (url, page.id)
            self.access_ok = False
        if not page.layout.valid_block():
            self.error_message = u"*fetch page* url=%s page(id=%s) layout(id=%s) layout is broken" % (url, page.id, page.layout.id)
            self.access_ok = False
        return page
