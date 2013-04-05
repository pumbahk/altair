# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__file__)
from datetime import datetime
from altaircms.datelib import get_now
import sqlalchemy as sa
from altaircms.page.models import Page
from altaircms.page.models import PageSet
from altaircms.page.models import StaticPage

from . import api 

class PageRenderingResource(object):
    def __init__(self, request):
        self.request = request

    def pc_access_control(self):
        return AccessControlPC(self.request)

    def get_preview_date(self):
        if 'datetime' not in self.request.params:
            return get_now()
        else:
            dt = self.request.params['datetime']
            return datetime.strptime(dt, '%Y%m%d%H%M%S')


"""
access controll object

レンダリング過程が複雑になったらここでrendererのdispatchする.
(今はresourceが持っている。)
"""


class AccessControlPC(object):
    def __init__(self, request):
        self.request = request
        self.access_ok = False
        self._error_message = []

    @property
    def error_message(self):
        return u"\n".join(self._error_message)

    def frontpage_template(self, page):
        lookup = api.get_frontpage_template_lookup(self.request)
        return lookup.get_renderable_template(self.request, page.layout, verbose=True)

    def frontpage_renderer(self):
        return api.get_frontpage_renderer(self.request)

    def can_access(self):
        if not self.access_ok:
            fmt = u"*front pc access* url is not found (%s). error=%s"
            mes = fmt % (self.request.referer, self.error_message)
            logger.warn(mes.encode("utf-8"))
        return self.access_ok

    def _fetch_page_from_params(self, url, dt):
        qs = self.request.allowable(Page).filter(PageSet.id==Page.pageset_id)
        qs = qs.filter(PageSet.url==url)
        qs = qs.filter(Page.in_term(dt))
        qs = qs.filter(Page.published==True)
        return qs.order_by(sa.desc("page.publish_begin"), "page.publish_end").first()

    def fetch_static_page_from_params(self, url,  dt):
        prefix = url.split("/", 1)[0]
        static_page = self.request.allowable(StaticPage).filter(StaticPage.name==prefix, StaticPage.published==True, StaticPage.interceptive==True).first()
        return static_page

    def fetch_page_from_params(self, url, dt):
        page = self._fetch_page_from_params(url, dt)
        self.access_ok = True

        if page is None:
            self._error_message.append(u"*fetch page* url=%s page is not found" % url)
            self.access_ok = False
            return page

        if page.event and page.event.is_searchable == False:
            self._error_message.append(u"*fetch pageset* pageset(id=%s) event(id=%s) is not searcheable" % (page.id, page.event.id))
            self.access_ok = False
        
        try:
            page.valid_layout()
        except ValueError, e:
            self._error_message.append(str(e))
            self.access_ok = False
        return page
