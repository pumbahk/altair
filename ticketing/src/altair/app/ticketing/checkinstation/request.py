# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

class PostRequestFromJsonRequest(object):
    def __init__(self, request):
        self.request = request

    def __getattr__(self, k):
        return getattr(self.request, k)

    @property
    def params(self):
        return self.request.json_body

    @property
    def POST(self):
        return self.request.json_body
