# -*- coding:utf-8 -*-
from pyramid.decorator import reify
from .linklib import get_global_link_settings
from altairsite.pyramidlayout import MyLayout as LayoutBase
from .datelib import get_now, get_today, has_session_key
from .helpers.base import jdatetime
        
class MyLayout(LayoutBase):
    class color:
        event = "#dfd"
        page = "#ffd"
        item = "#ddd"
        asset = "#fdd"
        master = "#ddf"

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @reify
    def global_link(self):
        return get_global_link_settings(self.request)

    def now(self):
        return self.request.now

    def today(self):
        return get_today(self.request)

    @property
    def information_get_now(self):
        if has_session_key(self.request):
            prefix = u"時間指定有効"
        else:
            prefix = u"時間指定無効"
        return u"{0}: {1}".format(prefix, jdatetime(self.request.now))
