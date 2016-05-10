# -*- encoding:utf-8 -*-

from copy import deepcopy
from datetime import datetime
from altaircms.datelib import get_now
import logging
logger = logging.getLogger(__file__)

import altaircms.helpers as h
from . import searcher
from altaircms.models import Genre
from ..pyramidlayout import get_salessegment_kinds
from altaircms.helpers.base import deal_limit, deal_limit_class

class SearchResult(dict):
    pass


## null object
class Nullable(object):
    """
    >>> Nullable(None).x.y.z.value
    None
    >>> Nullable(1).value
    1
    """
    NULL = None #for flyweight
    def __init__(self, obj):
        self.obj = obj

    def __getattr__(self, k):
        obj = self.obj
        if hasattr(obj, k):
            return Nullable(getattr(obj, k))
        else:
            return self.NULL

    @property
    def value(self):
        return self.__dict__["obj"]

Nullable.NULL = Nullable(None)

def _get_mocked_pageset_query(request, query_params):
    """ mocked pageset queyr (for testing)"""
    from altaircms.page.models import PageSet, Page
    from altaircms.event.models import Event
    event = Event(subtitle=u"ソ・ジソブ　日本公式ファンクラブ1周年記念！2012 ファンミーティング in 東京", 
                  description=u"2012/3/24(土) 東京ビッグサイト（東京国際展示場）(東京都)", 
                  event_open=datetime(2012, 5, 1), 
                  deal_open=datetime(2012, 3, 1))
    page_set = PageSet(url="http://www.example.com", version_counter=1, event=event)
    page = Page(pageset=page_set, version=1, 
                description="楽天チケットイベント詳細ページです", 
                )
    return [page_set]*20

class SearchPageResource(object):
    def __init__(self, request):
        self.request = request

    def result_sequence_from_query(self, query, query_params):
        """
        ここでは、検索結果のqueryを表示に適した形式に直す
        """
        today = get_now(self.request)    
        # for pageset in query:
        #     yield SearchResultRender(pageset, today, self.request)
        return [SearchResultRender(pageset, today, self.request, query_params) for pageset in query]

    def get_query_params_as_html(self, query_params):
        return QueryParamsRender(self.request, query_params)

    def get_result_sequence_from_query_params_ext(self, query_params, searchfn=_get_mocked_pageset_query):
        """ ## side effect. update query_params
        """
        if not "genre" in self.request.GET:
            return self.get_result_sequence_from_query_params(query_params, searchfn=searchfn)

        genre_id = self.request.GET["genre"]
        genre = Genre.query.filter_by(id=genre_id).first()
        if genre is None:
            return self.get_result_sequence_from_query_params(query_params, searchfn=searchfn)                

        gs = genre.ancestors_include_self
        gs.pop()
        query_params.update(sub_categories=genre_id, 
                            category_label=u">".join([g.label for g in reversed(gs)]))
        def with_filter_by_genre(request, query_params):
            return searcher.search_by_genre(self.request, searchfn(self.request, query_params), [self.request.GET["genre"]])
        return self.get_result_sequence_from_query_params(query_params, searchfn=with_filter_by_genre)

    def get_result_sequence_from_query_params(self, query_params, searchfn=_get_mocked_pageset_query):
        query = searchfn(self.request, query_params)
        return self.result_sequence_from_query(query, query_params)

class QueryParamsRender(object):
    """ 渡された検索式をhtmlとしてレンダリング
    """
    def __init__(self, request, query_params):
        self.request = request
        self.query_params = query_params

    def _listing_from_tree(self, marked_tree):
        translator = marked_tree.translator
        for parent, children in marked_tree.tree:
            if parent in marked_tree.check_all_list:
                yield u"%s>全て" % translator[parent]
            else:
                for child in children:
                    yield u"%s>%s" % (translator[parent], translator[child])

    def describe_from_tree(self, marked_tree):
        """ 「関東 > 全て, 北海道 > 北海道」 のような表示"""
        return u", ".join(self._listing_from_tree(marked_tree))

    def describe_from_term(self, bdate, edate):
        """ 「2011/12/12 〜 2011/12/30」のような表示"""
        if bdate and edate:
            return u"%s 〜 %s" % (bdate.strftime("%Y/%m/%d"), edate.strftime("%Y/%m/%d"))
        elif bdate:
            return u"%s 〜" % bdate.strftime("%Y/%m/%d") 
        else:
            return u"〜 %s" % edate.strftime("%Y/%m/%d") 

    def describe_deal_cond(self, deal_cond_list):
        """最速抽選 or 先行抽選 or 一般発売"""
        kinds = get_salessegment_kinds(self.request)
        convertor = {unicode(k.id): k.label for k in kinds}
        if len(deal_cond_list) <= 1:
            return convertor.get(deal_cond_list[0], "")
        else:
            return u" or ".join(convertor.get(k, "") for k in deal_cond_list)

    def __unicode__(self):
        u"""\
        フリーワード:a, b, cc,
        ジャンル:音楽 &gt ジャズ・ヒュージョン,演歌・邦楽, スポーツ &gt 野球
        開催地:北海道 &gt 全て, 東北 &gt 青森,
        公演日:2011/12/12 〜 2011/12/30,
        販売条件: 先行,
        付加サービス: お隣キープ,座席選択可能,
        受付・販売開始: 10日
        販売終了まで: 7日前
        販売終了：含む
        公演中止：含む
        """

        r = []
        qp = self.query_params
        if "query" in qp:
            r.append(u"フリーワード: %s" % qp["query"])
        if qp.get("category_label"):
            r.append(u"ジャンル: %s" % qp.get("category_label"))
        elif qp.get("category_tree") and qp.get("top_categories") or qp.get("sub_categories"):
            if "category_tree" in qp:
                r.append(u"ジャンル: %s " % self.describe_from_tree(qp["category_tree"]))
        if qp.get("area_tree") and qp.get("prefectures"):
            r.append(u"開催地: %s" % self.describe_from_tree(qp["area_tree"]))
        if qp.get("performance_open") or qp.get("performance_close"):
            r.append(u"公演日: %s" % self.describe_from_term(qp.get("performance_open"), qp.get("performance_close")))
        if qp.get("deal_cond"):
            r.append(u"販売条件: %s" % self.describe_deal_cond(qp.get("deal_cond")))
        if qp.get("added_service"):
            r.append(u"付加サービス: %s" % "--dummy--")
        if qp.get("before_deal_start"):
            r.append(u"受付・販売開始: %s日" % qp["before_deal_start"])
        if qp.get("till_deal_end"):
            r.append(u"販売終了まで: %s日" % qp["till_deal_end"])
        if qp.get("closed_only"):
            r.append(u"販売終了: 含む")
        if qp.get("canceled_only"):
            r.append(u"公演中止: 含む")

        if qp.get("query_expr_message"):
            r.append(qp["query_expr_message"])
        return u", ".join(r)

class SearchResultRender(object):
    """検索結果をhtmlとしてレンダリング
    """
    def __init__(self, pageset, today, request, query_params):
        self.pageset = pageset
        self.today = today
        self.request = request
        self.query_params = query_params

    def __html__(self):
        return u"""\
  <div class="searchResult">
      <dl>
          <dt>%(category_icons)s</dt>
          <dd>
            %(page_description)s
          </dd>
      </dl>
      <div class="%(deal_limit_class)s">%(deal_limit)s</div>
      <ul>
          %(deal_description)s
      </ul>
      <p>%(purchase_link)s</p>
  </div>
        """ % self.make_result()

    def make_result(self):
        # assert self.pageset.event
        limit = deal_limit(self.today, self.pageset.event.deal_open, self.pageset.event.deal_close, self.pageset.event.in_preparation)
        return SearchResult(
            category_icons = self.category_icons(), 
            page_description = self.page_description(),
            deal_limit = limit,
            deal_limit_class = deal_limit_class(limit),
            deal_description = self.deal_description(),
            purchase_link = self.purchase_link()
            )

        
    def category_icons(self): ## fixme: too access DB.
        v = Nullable(self.pageset).genre.origin.value
        if v is None:
            return u'<div class="icon-category icon-category-other"></div>'
        else:
            return u'''\
<div class="icon-category icon-category-%s"></div>
''' % v
        
    def page_description(self):
        fmt =  u"""\
<p><a href="%s">%s</a> 公演/試合数: %s</p>
<p class="align1">%s</p>
<p class="align1">%s</p>
"""
        link = h.link.publish_page_from_pageset(self.request, self.pageset)
        link_label = self.pageset.event.title #xx?
        event = self.pageset.event
        performances = []
        for p in event.performances:
            if not p.public:
                continue

            if p.end_on:
                if self.today <= p.end_on:
                    performances.append(p)
            else:
                if p.start_on >= self.today:
                    performances.append(p)

        perf_num = len(performances)

        if "prefectures" in self.query_params:
            if self.query_params['prefectures']:
                area_performances = []

                for area in self.query_params["prefectures"]:
                    for perf in performances:
                        if perf.prefecture == area:
                            area_performances.append(perf)
                performances = area_performances

        performances = performances if len(performances) < 3 else performances[:3]
        performances = u"</p><p class='align1'>".join([u"%s %s(%s)" %
            (p.start_on.strftime("%Y-%m-%d %H:%M"), p.venue, p.jprefecture) for p in performances])
        return fmt % (link, link_label, perf_num, event.description, performances)

    # def deal_info_icons(self):
    #     event = self.pageset.event
    #     kinds = set(g.kind for g in event.salessegment_groups) 
    #     return u"".join(u'<div class="icon-salessegment %s"></div>'% k for k in kinds)


    def deal_description(self):
        event = self.pageset.event
        r = []
        for g in sorted(event.salessegment_groups, key=lambda g: g.start_on):
            if g.publicp and g.master.publicp:
                # label = u'<strong>%s</strong> ' % g.name
                label = u'<div class="icon-salessegment %s"></div>'% g.kind
                r.append(u'<li class="searchDate">%s%s</li>' % (label, h.term(g.start_on, g.end_on)))
        return u"\n".join(r)


    def purchase_link(self):
        fmt = u'''\
<a href="%s"><img src="%s" alt="詳細へ" width="86" height="32" /></a>
<!--<a href="%s"><img src="%s" alt="購入へ" width="86" height="32" /></a>-->
'''
        return fmt % (h.link.publish_page_from_pageset(self.request, self.pageset), 
                      self.request.static_url("altaircms:static/RT/img/search/btn_detail.gif"), 
                      h.link.get_purchase_page_from_event(self.request, self.pageset.event), 
                      self.request.static_url("altaircms:static/RT/img/search/btn_buy.gif"))

