from .security import get_acl_candidates
from altaircms.page.models import PageSet

class PageRenderingResource(object):
    def __init__(self, request):
        self.request = request

    @property
    def __acl__(self):
        return get_acl_candidates()

    def access_controll_from_pageset(self, pageset):
        page = pageset.current()
        return AccessControl(self.request, page, self.request.user)

    def access_controll_from_page(self, page):
        return AccessControl(self.request, page, self.request.user)

    def current_page(self):
        pageset = PageSet.query.filter(PageSet.id==self.request.matchdict["pageset_id"]).one()
        return pageset.current()

    def frontpage_render(self):
        return "hey"

    def get_page_and_layout_preview(self, url, page_id):
        try:
            page = Page.query.filter(Page.hash_url==url, Page.id==page_id).one()
            return page, page.layout
        except saexc.NoResultFound:
            raise pyrexc.NotFound(u'page, url=%s and is not found' % (url))



class AccessControl(object):
    def __init__(self, request, page, user=None):
        self.request = request
        self.page = page
        self.user = user

    def can_access(self):
        return True

    def rendering_page(self):
        return "http://www.example.com"
