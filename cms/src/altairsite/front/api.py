# -*- coding:utf-8 -*-
import sqlalchemy as sa
from altaircms.models import Category

def _get_categories(request, hierarchy):
        return Category.get_toplevel_categories(hierarchy=hierarchy, request=request).order_by(sa.asc("orderno"))

def get_navigation_categories(request):
    top_outer_categories = _get_categories(request, hierarchy=u"top_outer")
    top_inner_categories = _get_categories(request, hierarchy=u"top_inner")

    categories = _get_categories(request, hierarchy=u"大")

    return dict(categories=categories,
                top_outer_categories=top_outer_categories,
                top_inner_categories=top_inner_categories)
