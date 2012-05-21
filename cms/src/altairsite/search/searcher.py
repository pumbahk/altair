# -*- encoding:utf-8 -*-
import sqlalchemy as sa
import sqlalchemy.orm as orm
import datetime
import logging
logger = logging.getLogger(__file__)
from altaircms.models import (
    Category, 
    Performance
)
from altaircms.models import DBSession
from altaircms.page.models import PageSet
from altaircms.event.models import Event
from altaircms.solr import api as solrapi


def search_by_freeword(qs, request, words, query_cond):
    assert query_cond in ("intersection", "union")

    fulltext_search = solrapi.get_fulltext_search(request)
    solr_query = solrapi.create_query_from_freeword(words, query_cond=query_cond)
    result = fulltext_search.search(solr_query, fields=["id"])
    
    pageset_ids = [f["id"] for f in result]
    logger.info("pageset_id: %s" % pageset_ids)
    return qs.filter(PageSet.id.in_(pageset_ids))

def _extract_tags(params, k):
    if k not in params:
        return []
    tags = [e.strip() for e in params.pop(k).split(",")] ##
    return [k for k in tags if k]

def get_pageset_query(request, query_params): 
    """ 検索する関数.このモジュールのほかの関数は全てこれのためにある。

    0. フリーワード検索追加. 
    1. カテゴリトップページから、対応するページを見つける
    2. イベントデータから、対応するページを見つける(sub_qs)
    """
    sub_qs = DBSession.query(Event.id)
    sub_qs = events_by_area(sub_qs, query_params.get("prefectures"))
    sub_qs = events_by_performance_term(sub_qs, query_params.get("start_date"), query_params.get("end_date"))
    sub_qs = events_by_deal_cond_flags(sub_qs, query_params) ## 未実装
    sub_qs = events_by_added_service(sub_qs, query_params) ## 未実装
    sub_qs = events_by_about_deal(sub_qs, query_params.get("before_deal_start"), query_params.get("till_deal_end"), 
                                  query_params.get("closed_only"), query_params.get("canceld_only"))

    qs = PageSet.query
    qs = search_by_ganre(query_params.get("top_categories"), query_params.get("sub_categories"), qs=qs)
    qs = search_by_events(qs, sub_qs)
    if "query" in query_params:
        words = _extract_tags(query_params, "query")
        qs = search_by_freeword(qs, request, words, query_params.get("query_cond"))
    return  qs


def search_by_events(qs, event_ids):
    return qs.filter(PageSet.event_id.in_(event_ids))

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

def events_by_area(qs, prefectures):
    if not prefectures:
        return qs

    matched_perf_ids = DBSession.query(Performance.event_id).filter(Performance.venue.in_(prefectures))
    return qs.filter(Event.id.in_(matched_perf_ids))

def events_by_performance_term(qs, start_date, end_date):
    if not (start_date or end_date):
        return qs

    if start_date:
        qs = qs.filter(Event.event_open >= start_date)
    if end_date:
        qs = qs.filter(Event.event_close <= end_date)
    return qs

def events_by_deal_cond_flags(qs, flags):
    #return qs.filter(Event._flags.in_(flags))
    import warnings
    warnings.warn("not implemented, yet")
    return qs

def events_by_added_service(qs, flags):
    #return qs.filter(Event._flags.in_(flags))
    import warnings
    warnings.warn("not implemented, yet")
    return qs

def events_by_about_deal(qs, before_deal_start, till_deal_end, closed_only, canceld_only, _nowday=datetime.datetime.now):
    today = _nowday()

    if before_deal_start:
        ## 販売開始？本当はN日以内に発送らし
        end_point = today+datetime.timedelta(days=before_deal_start)
        qs = qs.filter(today <= Event.deal_open).filter(Event.deal_open <= end_point)

    if till_deal_end:
        end_point = today+datetime.timedelta(days=till_deal_end)
        qs = qs.filter(today <= Event.deal_close).filter(Event.deal_close <= end_point)

    ## 通常は、現在の日付よりも未来にあるイベント以外見せない
    if closed_only:
        qs = qs.filter(today > Event.deal_close)
    else:
        qs = qs.filter((today <= Event.deal_close )|( Event.deal_close == None))
        
    if canceld_only:
        qs = qs.filter(Performance.event_id==Event.id).filter(Performance.canceld==True)
    return qs
