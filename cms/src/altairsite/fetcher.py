# -*- coding:utf-8 -*-
from zope.interface import Interface
from zope.interface import implementer
from zope.interface import providedBy

import logging
logger = logging.getLogger(__name__)
import sqlalchemy as sa
from pyramid.httpexceptions import HTTPNotFound
from altaircms.page.models import (
    PageType, 
    Page, 
    PageSet, 
    StaticPage, 
    StaticPageSet
 )

class ICurrentPageFetcher(Interface):
    def front_page(request, url, dt):
        pass

    def static_page(request, url, dt, pagetype):
        pass

class PageQueryControl(object):
    def __init__(self,
                 pc_pagetype, 
                 mobile_pagetype, 
                 smartphone_pagetype
                 ):
        self.pc_pagetype = pc_pagetype
        self.mobile_pagetype = mobile_pagetype
        self.smartphone_pagetype = smartphone_pagetype

    def widget_pageset_query(self, request, url, dt):
        qs = request.allowable(Page).filter(PageSet.id==Page.pageset_id)
        qs = qs.filter(PageSet.url==url)
        qs = qs.filter(Page.in_term(dt))
        qs = qs.filter(Page.published==True)
        qs = qs.order_by(sa.desc("page.publish_begin"), "page.publish_end")
        return qs

    def static_pageset_query(self, request, url, dt, pagetype):
        qs = request.allowable(StaticPage).filter(StaticPageSet.id==StaticPage.pageset_id)
        qs = qs.filter(StaticPageSet.pagetype_id==PageType.id, PageType.name==pagetype)
        qs = qs.filter(StaticPageSet.url==url)
        qs = qs.filter(StaticPage.in_term(dt))
        qs = qs.filter(StaticPage.published==True)
        qs = qs.order_by(sa.desc("static_pages.publish_begin"), "static_pages.publish_end")
        return qs

@implementer(ICurrentPageFetcher)
class PageFetcherForPC(object):
    def __init__(self, control):
        self.control = control

    def front_page(self, request, url, dt):
        return self.control.widget_pageset_query(request, url, dt).first()
 
    def static_page(self, request, url, dt):
        control = self.control
        page_type = control.pc_pagetype
        return control.static_pageset_query(request, url, dt, page_type).first()

@implementer(ICurrentPageFetcher)
class PageFetcherForSmartphone(object):
    def __init__(self, control):
        self.control = control

    def front_page(self, request, url, dt):
        return self.control.widget_pageset_query(request, url, dt).first()
 
    def static_page(self, request, url, dt):
        control = self.control
        if request.organization.use_only_one_static_page_type:
            page_type = control.pc_pagetype
        else:
            page_type = control.smartphone_pagetype
        return control.static_pageset_query(request, url, dt, page_type).first()

@implementer(ICurrentPageFetcher)
class PageFetcherForMobile(object):
    exc_clacss = HTTPNotFound
    def __init__(self, control):
        self.control = control

    def front_page(self, request, url, dt):
        return self.control.widget_pageset_query(request, url, dt).first()

    ## mobileアクセスは常にstaticpage(name="mobile")を見る
    def static_page(self, request, url, dt):
        control = self.control
        page_type = control.mobile_pagetype

        page = control.static_pageset_query(request, url, dt, page_type).first()
        if page is None:
            raise self.exc_clacss("mobile page static page is not found. raise Exception, immedieately.")
        return page


## api
def get_current_page_fetcher(request):
    adapters = request.registry.adapters
    fetcher = adapters.lookup([providedBy(request)], ICurrentPageFetcher)
    if fetcher:
        return fetcher
    raise Exception("ICurrentPageFetcher is not found")

