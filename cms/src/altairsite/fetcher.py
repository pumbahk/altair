# -*- coding:utf-8 -*-
from zope.interface import Interface
from zope.interface import implementer
import logging
logger = logging.getLogger(__name__)
import sqlalchemy as sa

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

    def pc_static_page(request, url, dt):
        pass

    def mobile_static_page(request, url, dt):
        pass

@implementer(ICurrentPageFetcher)
class CurrentPageFetcher(object):
    def __init__(self,
                 pc_pagetype, 
                 mobile_pagetype, 
                 smartphone_pagetype
                 ):
        self.pc_pagetype = pc_pagetype
        self.mobile_pagetype = mobile_pagetype
        self.smartphone_pagetype = smartphone_pagetype

    def front_page(self, request, url, dt):
        qs = request.allowable(Page).filter(PageSet.id==Page.pageset_id)
        qs = qs.filter(PageSet.url==url)
        qs = qs.filter(Page.in_term(dt))
        qs = qs.filter(Page.published==True)
        qs = qs.order_by(sa.desc("page.publish_begin"), "page.publish_end")
        return qs.first()

    ## todo: まとめる
    def pc_static_page(self, request, url, dt, pagetype=None):
        qs = request.allowable(StaticPage).filter(StaticPageSet.id==StaticPage.pageset_id)
        qs = qs.filter(StaticPageSet.pagetype_id==PageType.id, PageType.name==self.pc_pagetype)
        qs = qs.filter(StaticPageSet.url==url)
        qs = qs.filter(StaticPage.in_term(dt))
        qs = qs.filter(StaticPage.published==True)
        qs = qs.order_by(sa.desc("static_pages.publish_begin"), "static_pages.publish_end")
        return qs.first()

    def mobile_static_page(self, request, url, dt):
        qs = request.allowable(StaticPage).filter(StaticPageSet.id==StaticPage.pageset_id)
        qs = qs.filter(StaticPageSet.pagetype_id==PageType.id, PageType.name==self.mobile_pagetype)
        qs = qs.filter(StaticPageSet.url==url)
        qs = qs.filter(StaticPage.in_term(dt))
        qs = qs.filter(StaticPage.published==True)
        qs = qs.order_by(sa.desc("static_pages.publish_begin"), "static_pages.publish_end")
        return qs.first()

    def smartphone_static_page(self, request, url, dt):
        qs = request.allowable(StaticPage).filter(StaticPageSet.id==StaticPage.pageset_id)
        qs = qs.filter(StaticPageSet.pagetype_id==PageType.id, PageType.name==self.smartphone_pagetype)
        qs = qs.filter(StaticPageSet.url==url)
        qs = qs.filter(StaticPage.in_term(dt))
        qs = qs.filter(StaticPage.published==True)
        qs = qs.order_by(sa.desc("static_pages.publish_begin"), "static_pages.publish_end")
        return qs.first()

## api
def get_current_page_fetcher(request):
    return request.registry.getUtility(ICurrentPageFetcher)
