# -*- coding:utf-8 -*-
from pyramid.decorator import reify
from altairsite.pyramidlayout import MyLayout as LayoutBase
from .datelib import get_now, get_today, has_session_key
from .helpers.base import jdatetime
from .api import get_backend_url_builder

class MyLayout(LayoutBase):
    class color:
        organization = "#fdf"
        event = "#dfd"
        page = "#ffd"
        item = "#ddd"
        asset = "#fdd"
        master = "#ddf"

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def now(self):
        return self.request.now

    def today(self):
        return get_today(self.request)

    @property
    def backend_url(self):
        return get_backend_url_builder(self.request).top_page_url(self.request)

    @property
    def information_get_now(self):
        if has_session_key(self.request):
            prefix = u"時間指定有効"
        else:
            prefix = u"時間指定無効"
        return u"{0}: {1}".format(prefix, jdatetime(self.request.now))
