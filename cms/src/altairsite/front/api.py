# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__file__)

from .resolver import ILayoutModelResolver
from .renderer import FrontPageRenderer

def get_frontpage_renderer(request):
    """ rendererを取得
    """
    return FrontPageRenderer(request)

def get_frontpage_discriptor_resolver(request):
    return request.registry.getUtility(ILayoutModelResolver)

