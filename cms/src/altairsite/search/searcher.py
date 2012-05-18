# -*- encoding:utf-8 -*-
import sqlalchemy as sa
import sqlalchemy.orm as orm

from altaircms.models import Category
from altaircms.models import DBSession
from altaircms.page.models import PageSet

"""
todo:

form でデータを受け取り searcherが検索queryにする。
そのような昨日を持った関数をapi.pyに書く。
view/resourceからは、apiを呼び出す
"""

def search_by_ganre(top_categories, sub_categories, qs=None):
    """ジャンルからページセットを取り出す
    :params qs:
    :return: query set of PageSet
    """
    qs = qs or PageSet.query

    ## どのチェックボックスもチェックされていない場合には絞り込みを行わない
    if not (top_categories or sub_categories):
        return qs

    where = sa.null()    

    if top_categories:
        parent_category_ids = DBSession.query(Category.id).filter(Category.name.in_(top_categories))
        where = Category.parent_id.in_(parent_category_ids)

    if sub_categories:
        where = where | Category.name.in_(sub_categories)

    ## カテゴリ(ジャンル)に対応するカテゴリトップのページを取り出す
    category_page_ids = DBSession.query(PageSet.id).join(Category, PageSet.id==Category.pageset_id).filter(where)

    ## サブカテゴリトップのページと紐づいているページを取り出す
    return qs.filter(PageSet.parent_id.in_(category_page_ids))

def pagesets_by_big_category_name(name):
    parent_category_stmt = DBSession.query(Category.id).filter_by(name=name).subquery()
    parents_ids = orm.aliased(Category, parent_category_stmt)
    category_stmt = Category.query.join(parents_ids, parents_ids.id==Category.parent_id).all()

