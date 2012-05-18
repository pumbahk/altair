# -*- encoding:utf-8 -*-
import sqlalchemy as sa
import sqlalchemy.orm as orm

from altaircms.models import (
    Category, 
    Performance
)
from altaircms.models import DBSession
from altaircms.page.models import PageSet
from altaircms.event.models import Event

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

def search_by_area(prefectures, qs=None):
    qs = qs or PageSet.query
    if not prefectures:
        return qs

    matched_perf_ids = DBSession.query(Performance.event_id).filter(Performance.venue.in_(prefectures))
    matched_event_ids = DBSession.query(Event.id).filter(Event.id.in_(matched_perf_ids))

    return qs.filter(PageSet.event_id.in_(matched_event_ids))

# def search_by_
