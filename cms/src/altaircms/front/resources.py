# -*- coding:utf-8 -*-

import sqlalchemy as sa
import logging
logger = logging.getLogger(__file__)

from . import api
from altaircms.datelib import get_now
from altaircms.security import get_acl_candidates
from altaircms.page.models import Page
from altaircms.page.models import PageSet
from altaircms.auth.api import set_request_organization
from altaircms.auth.accesskey.api import get_page_access_key_control

class PageRenderingResource(object):
    def __init__(self, request):
        self.request = request

    @property
    def __acl__(self):
        return get_acl_candidates()

    def access_control(self):
        return AccessControl(self.request)


class AccessControl(object):
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
            logger.info("*cms front preview* url is not found (%s)" % self.request.url)
            logger.info("*cms front preview* error=%s" % self.error_message)
        return self.access_ok

    def _check_page_is_accessable(self, page, access_key):
        if page is None:
            self._error_message.append("*fetch page* page is not found")
            self.access_ok = False
            return page

        ## accesskeyが存在していれば
        control = get_page_access_key_control(self.request, page)
        access_key = control.get_access_key(access_key)
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
        elif not control.can_private_access(key=access_key, now=get_now(self.request)):
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

    def _retry_page(self, pageset, published):
        if published:
            return None
        return self.request.allowable(Page).filter(Page.pageset_id==pageset.id).order_by(sa.desc(Page.updated_at)).first()

    def fetch_page_from_pagesetid(self, pageset_id, published=True):
        ## pagesetはクライアントから確認しない。allowableが正しい。
        pageset = self.request.allowable(PageSet).filter_by(id=pageset_id).first()
        self.access_ok = True

        if pageset is None:
            self._error_message.append("*fetch pageset* pagset(id=%s) is not found" % pageset_id)
            self.access_ok = False
            return pageset

        page = pageset.current(published=published, dt=get_now(self.request))

        if page is None:
            page = self._retry_page(pageset, published)
            if page is None:
                self.access_ok = False
                self._error_message.append("*fetch page* pageset(id=%s) has not accessable children" % pageset.id)
                return None

        try:
            page.valid_layout()
        except ValueError, e:
            self._error_message.append(str(e))
            self.access_ok = False
        self._check_page_is_accessable(page, None)
        return page
