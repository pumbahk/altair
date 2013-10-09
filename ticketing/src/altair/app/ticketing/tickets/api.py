# -*- coding:utf-8 -*-
from .interfaces import ISVGBuilder

def get_svg_builder(request):
    return request.registry.getUtility(ISVGBuilder)
