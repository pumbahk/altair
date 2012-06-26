from .security import get_acl_candidates
from altaircms.page.models import PageSet

class RenderingPageResource(object):
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

class AccessControl(object):
    def __init__(self, request, page, user=None):
        self.request = request
        self.page = page
        self.user = user

    def can_access(self):
        return True

    def rendering_page(self):
        return "http://www.example.com"
