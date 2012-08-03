# -*- coding:utf-8 -*-


import logging
logger = logging.getLogger(__file__)

from . import api
from altaircms.security import get_acl_candidates
from altaircms.page.models import Page
from altaircms.page.models import PageSet
from altaircms.auth.api import set_request_organization

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
        return u"\n".join(self._error_message)

    def can_access(self):
        if not self.access_ok:
            logger.info("*cms front preview* url is not found (%s)" % self.request.url)
            logger.warn("*cms front preview* error=%s" % self.error_message)
        return self.access_ok

    def can_rendering(self, template, page):
        try:
            return api.is_renderable_template(template, page)
        except Exception, e:
            self._error_message.append(str(e))
            return False

    def _check_page_is_accessable(self, page, access_key):
        if page is None:
            self._error_message.append("*fetch page* page is not found")
            self.access_ok = False
            return page

        ## accesskeyが存在していれば
        access_key = page.get_access_key(access_key)
        if not access_key:
            self.access_ok = False

            if self.request.organization is None:
                self._error_message.append("not loging user")
                return page

            ## 同じorganizatioに属しているオペレーターは全部見れる。
            if self.request.organization and self.request.organization.id == page.organization_id:
                self.access_ok = True
            else:
                fmt = "*fetch page* invalid organization page(%s) != operator(%s)" 
                self._error_message.append(fmt % (self.request.organization.id, page.organization_id))
                return page
        elif not page.can_private_access(key=access_key):
            self.access_ok = False
            self._error_message.append(u"invalid access key %s.\n 有効期限が切れているかもしれません. (有効期限:%s)" % (access_key.hashkey, access_key.expiredate))
            return page

        ## 未ログインの場合request._organizationがないので追加
        set_request_organization(self.request, page.organization_id)

        try:
            page.valid_layout()
        except ValueError, e:
            self._error_message.append(str(e))
            self.access_ok = False
        return page

    def fetch_page_from_pageid(self, page_id, access_key=None):
        page = Page.query.filter_by(id=page_id).first()
        self.access_ok = True
        return self._check_page_is_accessable(page, access_key)

    def fetch_page_from_pagesetid(self, pageset_id):
        ## pagesetはクライアントから確認しない。allowableが正しい。
        pageset = self.request.allowable(PageSet).filter_by(id=pageset_id).first()
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
