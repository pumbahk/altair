# -*- coding:utf-8 -*-


import logging
logger = logging.getLogger(__file__)


from altaircms.page.models import PageSet
from altaircms.page.models import Page
from . import api
from altaircms.security import get_acl_candidates

class PageRenderingResource(object):
    def __init__(self, request):
        self.request = request

    @property
    def __acl__(self):
        return get_acl_candidates()

    def access_control(self):
        return AccessControl(self.request)

    def frontpage_renderer(self):
        return api.get_frontpage_render(self.request)

    def frontpage_template(self, page):
        filename = page.layout.template_filename
        return api.get_frontpage_template(self.request, filename)


class AccessControl(object):
    def __init__(self, request):
        self.request = request
        self.access_ok = False
        self._error_message = []

    @property
    def error_message(self):
        return "\n".join(self._error_message)

    def can_access(self):
        if not self.access_ok:
            logger.info("*cms front preview* url is not found (%s)" % self.request.referer) ## referer
        return self.access_ok

    def can_rendering(self, template, page):
        try:
            return api.is_renderable_template(template, page)
        except Exception, e:
            self.error_message = str(e)
            return False

    def fetch_page_from_pageid(self, page_id, access_key=None):
        page = Page.query.filter_by(id=page_id).first()
        self.access_ok = True

        if page is None:
            self._error_message.append("*fetch page* page is not found")
            self.access_ok = False
            return page


        ## 現状はloginしたuserは全部のページが見れる
        access_key = page.get_access_key(access_key)
        if not self.request.user:
            ## access_keyを持っていたとき、それが有効ならページが見れる。
            if not access_key:
                self._error_message.append("not loging user")
                self.access_ok = False
            elif not page.can_private_access(key=access_key):
                self.access_ok = False
                self._error_message.append(u"invalid access key %s.\n 有効期限が切れているかもしれません. (有効期限:%s)" % (access_key.hashkey, access_key.expiredate))
        try:
            page.valid_layout()
        except ValueError, e:
            self._error_message.append(str(e))
            self.access_ok = False
        return page
        
    def fetch_page_from_pagesetid(self, pageset_id):
        pageset = PageSet.query.filter_by(id=pageset_id).first()
        self.access_ok = True

        if pageset is None:
            self._error_message.append("*fetch pageset* pagset(id=%s) is not found" % pageset_id)
            self.access_ok = False
            return pageset

        page = pageset.current()
        if page is None:
            self.access_ok = False
            self._error_message.append("*fetch page* pageset(id=%s) has not accessable children" % pageset.id)
            return page

        try:
            page.valid_layout()
        except ValueError, e:
            self._error_message.append(str(e))
            self.access_ok = False
        return page


    
