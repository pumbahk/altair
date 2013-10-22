# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__file__)
from datetime import datetime
from altaircms.datelib import get_now

from . import api 
from ..fetcher import get_current_page_fetcher
from altair.mobile.interfaces import ISmartphoneRequest

class PageRenderingResource(object):
    def __init__(self, request):
        self.request = request

    def pc_access_control(self):
        return AccessControlPC(self.request)

    def get_preview_date(self):
        if 'datetime' not in self.request.params:
            return get_now(self.request)
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

    def frontpage_discriptor(self, page):
        resolver = api.get_frontpage_discriptor_resolver(self.request)
        return resolver.resolve(self.request, page.layout, verbose=True)

    def frontpage_renderer(self):
        return api.get_frontpage_renderer(self.request)

    def can_access(self):
        if not self.access_ok:
            fmt = u"*front pc access* url is not found (%s). error=%s"
            mes = fmt % (self.request.url, self.error_message)
            logger.warn(mes.encode("utf-8"))
        return self.access_ok

    def _fetch_page_from_params(self, url, dt):
        return get_current_page_fetcher(self.request).front_page(self.request, url, dt)

    ## todo: refactoring
    def fetch_static_page_from_params(self, url,  dt):
        prefix = url.split("/", 1)[0]
        if prefix == url:
            prefix = ""
        fetcher = get_current_page_fetcher(self.request)
        if ISmartphoneRequest.providedBy(self.request) and not self.request.organization.use_only_one_static_page_type:
            return fetcher.smartphone_static_page(self.request, prefix, dt)
        else:
            return fetcher.pc_static_page(self.request, prefix, dt)

    def fetch_page_from_params(self, url, dt):
        page = self._fetch_page_from_params(url, dt)
        self.access_ok = True

        if page is None:
            self._error_message.append(u"*fetch page* url=%s page is not found" % url)
            self.access_ok = False
            return page
        
        try:
            page.valid_layout()
        except ValueError, e:
            self._error_message.append(str(e))
            self.access_ok = False
        return page
