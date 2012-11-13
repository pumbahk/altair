# -*- encoding:utf-8 -*-

from altaircms.models import Category
import sqlalchemy as sa
import sqlalchemy.orm as orm


def get_performances(event):
    if event:
        return event.performances
    else:
        return []

## category

def _get_categories(request, hierarchy):
    qs =  Category.get_toplevel_categories(hierarchy=hierarchy, request=request)
    return qs.order_by(sa.asc("display_order")).options(orm.joinedload("pageset"))

def get_subcategories_from_page(request, page):
    """ カテゴリトップのサブカテゴリを取得する
    """
    qs = Category.query.filter(Category.pageset==page.pageset).filter(Category.pageset != None)
    root_category = qs.first()
    return root_category.children if root_category else []
