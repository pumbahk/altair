# -*- encoding:utf-8 -*-
import sqlalchemy as sa
import sqlalchemy.orm as orm
import datetime
import logging
logger = logging.getLogger(__file__)
from altaircms.models import (
   SalesSegmentGroup, 
   Performance, 
   Genre
)
from altaircms.models import DBSession
from altaircms.page.models import (
   PageSet, 
   Page
)
from altaircms.event.models import Event
from altaircms.tag.models import (
   HotWord, 
   PageTag, 
)

from . import api
from altaircms.page.api import get_pageset_searcher
## todo: datetimeの呼び出し回数減らす

## for document
from zope.interface import Interface, provider
class ISearchFn(Interface):
   def __call__(request,  query_params):
       """ resource.pyでsearchfnを引数に取るメソッドに渡す
           :param query_params:  form.pyのmake_query_paramsで作られた辞書
           :return: query set of pageset
       """
##
def _refine_pageset_collect_future(qs, _nowday=None):
   if _nowday is None:
      _nowday = datetime.datetime.now()

   qs = qs.filter((_nowday <= Event.deal_close )|( Event.deal_close == None))
   return qs

def _refine_pageset_search_order(qs):
   """  検索結果nの表示順序を変更。最も販売終了が間近なものを先頭にする
   """
   return qs.order_by(sa.asc(Event.deal_close))

def _refine_pageset_only_published_term(qs, now=None):
   """ 公開期間中のページのみを集める
   """
   if now is None:
      now = datetime.datetime.now()
   qs = qs.filter(PageSet.id==Page.pageset_id)
   return qs.filter(Page.in_term(now)).filter(Page.published==True)

def _refine_pageset_qs(qs):
    """optimize"""
    # 検索対象に入っているもののみが検索に引っかかる
    qs = qs.filter(Event.is_searchable==True).filter(Event.id==PageSet.event_id)

    qs = _refine_pageset_search_order(qs)
    qs = _refine_pageset_only_published_term(qs)
    return qs.options(orm.joinedload("event"), orm.joinedload("event.performances"), orm.joinedload("genre"))


## todo:test
@provider(ISearchFn)
def get_pageset_query_from_hotword(request, query_params):
    """ Hotwordの検索"""
    qs = request.allowable(PageSet)
    qs = _refine_pageset_collect_future(qs)
    if query_params.get("hotword"):
       qs = request.allowable(PageSet)
       hotword = query_params["hotword"]
       return _refine_pageset_qs(search_by_hotword(request, qs, hotword))
    else:
       return _refine_pageset_qs(qs.filter(PageSet.event_id!=None)) # empty set query is good for that?

@provider(ISearchFn)
def get_pageset_query_from_freeword(request, query_params):
    """ フリーワード検索のみ"""
    qs = request.allowable(PageSet)
    qs = _refine_pageset_collect_future(qs)
    words = _extract_tags(query_params, "query")
    if words and (len(words) > 1 or words[0] != u'""'):
        qs = search_by_freeword(request, qs, words, query_params.get("query_cond"))
        return  _refine_pageset_qs(qs)
    else:
       return _refine_pageset_qs(qs.filter(PageSet.event_id!=None)) # empty set query is good for that?

@provider(ISearchFn)
def get_pageset_query_from_genre(request, query_params):
    """ ジャンルのみ"""
    qs = request.allowable(PageSet)
    qs = _refine_pageset_collect_future(qs)
    if query_params.get("top_categories") or query_params.get("sub_categories"):
       qs = search_by_genre(request, qs, query_params.get("top_categories"), query_params.get("sub_categories"))
       return  _refine_pageset_qs(qs)
    else:
       return _refine_pageset_qs(qs.filter(PageSet.event_id!=None)) # empty set query is good for that?

@provider(ISearchFn)
def get_pageset_query_from_area(request, query_params):
    """ エリアのみ"""
    qs = request.allowable(PageSet)
    qs = _refine_pageset_collect_future(qs)
    if query_params.get("prefectures"):
       sub_qs = request.allowable(Event).with_entities(Event.id)
       sub_qs = events_by_area(sub_qs, query_params.get("prefectures"))
       sub_qs = sub_qs.filter(Event.is_searchable==True)
       qs = search_by_events(qs, sub_qs)
       return  _refine_pageset_qs(qs)
    else:
       return _refine_pageset_qs(qs.filter(PageSet.event_id!=None)) # empty set query is good for that?

@provider(ISearchFn)
def get_pageset_query_from_deal_cond(request, query_params):
    """ 販売条件のみ"""
    qs = request.allowable(PageSet)
    qs = _refine_pageset_collect_future(qs)
    if query_params.get("deal_cond"):
       sub_qs = request.allowable(Event).with_entities(Event.id)
       sub_qs = events_by_deal_cond_flags(sub_qs, query_params.get("deal_cond", []))
       sub_qs = sub_qs.filter(Event.is_searchable==True)
       qs = search_by_events(qs, sub_qs)
       return  _refine_pageset_qs(qs)
    else:
       return _refine_pageset_qs(qs.filter(PageSet.event_id!=None)) # empty set query is good for that?

@provider(ISearchFn)
def get_pageset_query_from_deal_open_within(request, query_params):
    """ N日以内の受付販売開始"""
    qs = request.allowable(PageSet)
    qs = _refine_pageset_collect_future(qs)
    if query_params.get("ndays"):
       sub_qs = request.allowable(Event).with_entities(Event.id)
       sub_qs = events_by_within_n_days_of(sub_qs, Event.deal_open, query_params["ndays"])
       sub_qs = sub_qs.filter(Event.is_searchable==True)
       qs = search_by_events(qs, sub_qs)
       return  _refine_pageset_qs(qs)
    else:
       return _refine_pageset_qs(qs.filter(PageSet.event_id!=None)) # empty set query is good for that?

@provider(ISearchFn)
def get_pageset_query_from_event_open_within(request, query_params):
    """ N日以内に公演"""
##
## todo: 今、N日以内の公演開始のものを集めている。これはおかしいかもしれない。
##
    qs = request.allowable(PageSet)
    qs = _refine_pageset_collect_future(qs)
    if query_params.get("ndays"):
       sub_qs = request.allowable(Event).with_entities(Event.id)
       sub_qs = events_by_within_n_days_of(sub_qs, Event.event_open, query_params["ndays"])
       sub_qs = sub_qs.filter(Event.is_searchable==True)
       qs = search_by_events(qs, sub_qs)
       return  _refine_pageset_qs(qs)
    else:
       return _refine_pageset_qs(qs.filter(PageSet.event_id!=None)) # empty set query is good for that?


@provider(ISearchFn)
def get_pageset_query_from_multi(request, query_params):
    qs = request.allowable(PageSet)
    qs = _refine_pageset_collect_future(qs)
    sub_qs = request.allowable(Event).with_entities(Event.id)
    sub_qs = events_by_area(sub_qs, query_params.get("prefectures"))
    sub_qs = events_by_performance_term(sub_qs, query_params.get("performance_open"), query_params.get("performance_close"))

    #検索対象に入っているもののみが検索に引っかかる
    sub_qs = sub_qs.filter(Event.is_searchable==True)
    qs = search_by_events(qs, sub_qs)
    return _refine_pageset_qs(qs)


@provider(ISearchFn)
def get_pageset_query_fullset(request, query_params): 
    """ 検索する関数.このモジュールのほかの関数は全てこれのためにある。

    0. フリーワード検索追加. 
    1. カテゴリトップページから、対応するページを見つける
    2. イベントデータから、対応するページを見つける(sub_qs)
    """
    sub_qs = request.allowable(Event).with_entities(Event.id)
    sub_qs = events_by_area(sub_qs, query_params.get("prefectures"))
    sub_qs = events_by_performance_term(sub_qs, query_params.get("performance_open"), query_params.get("performance_close"))
    sub_qs = events_by_deal_cond_flags(sub_qs, query_params.get("deal_cond", []))
    sub_qs = events_by_added_service(sub_qs, query_params) ## 未実装
    sub_qs = events_by_about_deal(sub_qs, query_params.get("before_deal_start"), query_params.get("till_deal_end"), 
                                  query_params.get("closed_only"), query_params.get("canceld_only"))

    # 検索対象に入っているもののみが検索に引っかかる
    sub_qs = sub_qs.filter(Event.is_searchable==True)

    qs = request.allowable(PageSet)
    qs = search_by_genre(request, qs, query_params.get("top_categories"), query_params.get("sub_categories"))
    qs = search_by_events(qs, sub_qs)


    if "query" in query_params:
        words = _extract_tags(query_params, "query")
        qs = search_by_freeword(request, qs, words, query_params.get("query_cond"))

    return  _refine_pageset_qs(qs)


def search_by_hotword(request, qs, hotword):
   """　hotwordの検索
   """
   if hotword is None:
      return qs
   searcher = get_pageset_searcher(request)
   return searcher.filter_by_tag(qs, hotword.tag).filter(PageSet.event != None) #そもそもチケット用の検索なのでeventは必須)

def search_by_freeword(request, qs, words, query_cond):
    pageset_ids = api.pageset_id_list_from_words(request, words, query_cond)
    logger.info("pageset_id: %s" % pageset_ids)
    if not pageset_ids:
       return qs
    return qs.filter(PageSet.id.in_(pageset_ids))

def _extract_tags(params, k):
    if k not in params:
        return []
    params = params.copy()
    tags = [e.strip() for e in params.pop(k).split(",")] ##
    return [k for k in tags if k]


def search_by_events(qs, event_ids):
   if event_ids:
      return qs.filter(PageSet.event_id.in_(event_ids))
   else:
      return qs

def search_by_genre(request, qs, *genre_id_list):
    """
    :params qs:
    :return: query set of PageSet
    """
    ## どのチェックボックスもチェックされていない場合には絞り込みを行わない
    if not any(genre_id_list):
       return qs
    xs = []
    for ids in genre_id_list:
       xs.extend(ids)
    tags = PageTag.query.filter(PageTag.label==Genre.label, PageTag.organization_id==None, Genre.organization_id==request.organization.id)
    tag_id_list = tags.filter(Genre.id.in_(xs)).with_entities(PageTag.id).all()
    tag_id_list = [x for xs in tag_id_list for x in xs]
    searcher = get_pageset_searcher(request)
    return searcher.filter_by_system_tag_many(qs, tag_id_list)

def events_by_area(qs, prefectures):
    if not prefectures:
        return qs

    matched_perf_ids = DBSession.query(Performance.event_id).filter(Performance.prefecture.in_(prefectures))
    return qs.filter(Event.id.in_(matched_perf_ids))


##日以内に開始系の関数
def events_by_within_n_days_of(qs, start_from, n, _nowday=datetime.datetime.now):
   today = _nowday()
   qs = qs.filter(today+datetime.timedelta(days=-1) <= start_from).filter(start_from <= (today+datetime.timedelta(days=n)))
   return qs
   

def events_by_performance_term(qs, performance_open, performance_close):
    if not (performance_open or performance_close):
        return qs

    if performance_open:
        qs = qs.filter(Event.event_open >= performance_open)
    if performance_close:
        qs = qs.filter(Event.event_close <= performance_close)
    return qs

def events_by_deal_cond_flags(qs, flags):
   if flags:
      return qs.filter(Event.id==SalesSegmentGroup.event_id).filter(SalesSegmentGroup.kind_id.in_(flags)).distinct()
   else:
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
        end_point = today+datetime.timedelta(days=int(before_deal_start))
        qs = qs.filter(today <= Event.deal_open).filter(Event.deal_open <= end_point)

    if till_deal_end:
        end_point = today+datetime.timedelta(days=int(till_deal_end))
        qs = qs.filter(today <= Event.deal_close).filter(Event.deal_close <= end_point)

    ## 通常は、現在の日付よりも未来にあるイベント以外見せない
    if closed_only:
        qs = qs.filter(today > Event.deal_close)
    else:
        qs = qs.filter((today <= Event.deal_close )|( Event.deal_close == None))
        
    if canceld_only:
        qs = qs.filter(Performance.event_id==Event.id).filter(Performance.canceld==True)
    return qs
