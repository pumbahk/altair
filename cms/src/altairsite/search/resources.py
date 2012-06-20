# -*- encoding:utf-8 -*-

from copy import deepcopy
from datetime import datetime
import logging
logger = logging.getLogger(__file__)

import altaircms.helpers as h
import pprint
from altaircms.lib.structures import Nullable
from . import forms

class SearchResult(dict):
    pass

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

    def result_sequence_from_query(self, query, _nowday=datetime.now):
        """
        ここでは、検索結果のqueryを表示に適した形式に直す
        """
        today = _nowday()    
        # for pageset in query:
        #     yield SearchResultRender(pageset, today, self.request)
        return [SearchResultRender(pageset, today, self.request) for pageset in query]

    def get_query_params_as_html(self, query_params):
        return QueryParamsRender(query_params)

    def get_result_sequence_from_query_params(self, query_params, searchfn=_get_mocked_pageset_query):
        logger.info(pprint.pformat(query_params))
        qp = deepcopy(query_params)
        # escape query
        if 'query' in qp:
            qp['query'] = '"%s"' % qp['query'].replace('"', '\\"').replace("'", "\\'")
        query = searchfn(self.request, qp)
        return self.result_sequence_from_query(query)

class QueryParamsRender(object):
    """ 渡された検索式をhtmlとしてレンダリング
    """
    def __init__(self, query_params):
        self.query_params = query_params

    def _listing_from_tree(self, marked_tree):
        translator = marked_tree.translator
        for parent, children in marked_tree.tree:
            if parent in marked_tree.check_all_list:
                yield u"%s&gt全て" % translator[parent]
            else:
                for child in children:
                    yield u"%s&gt%s" % (translator[parent], translator[child])

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
        convertor = forms.DealCondPartForm.DDICT
        if len(deal_cond_list) <= 1:
            return convertor[deal_cond_list[0]]
        else:
            return u" or ".join(convertor[k] for k in deal_cond_list)

    def __html__(self):
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
        if qp.get("category_tree") and qp.get("top_categories") or qp.get("sub_categories"):
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
            r.append(u"受付・販売開始: %s" % qp["before_deal_start"])
        if qp.get("till_deal_end"):
            r.append(u"販売終了まで: %s" % qp["till_deal_end"])
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
    def __init__(self, pageset, today, request):
        self.pageset = pageset
        self.today = today
        self.request = request

    def __html__(self):
        return u"""\
  <div class="searchResult">
      <dl>
          <dt>%(category_icons)s</dt>
          <dd>
            %(page_description)s
          </dd>
      </dl>
      <ul>
          <li class="searchRemaining">%(deal_limit)s</li>
          <li>%(deal_info_icons)s</li>
          <li class="searchDate">%(deal_description)s</li>
      </ul>
      <p>%(purchase_link)s</p>
  </div>
        """ % self.make_result()
        
    def make_result(self):
        # assert self.pageset.event
        return SearchResult(
            category_icons = self.category_icons(), 
            page_description = self.page_description(),
            deal_limit = self.deal_limit(),
            deal_info_icons = self.deal_info_icons(),
            deal_description = self.deal_description(),
            purchase_link = self.purchase_link()
            )

        
    def category_icons(self): ## fixme: too access DB.
        v = Nullable(self.pageset).parent.category.origin.value
        if v is None:
            return u'<div class="icon-category icon-category-other"></div>'
        else:
            return u'''\
<div class="icon-category icon-category-%s"></div>
''' % v
        
    def page_description(self):
        fmt =  u"""\
<p><a href="%s">%s</a></p>
<p class="align1">%s</p>
<p class="align1">%s</p>
"""
        link = h.link.to_publish_page_from_pageset(self.request, self.pageset)
        link_label = u"%s %s" % (self.pageset.event.title, self.pageset.name)
        description = self.pageset.event.description
        ## todo. ticketから開催場所の情報を取り出す
        performances = u"</p><p class='align1'>".join([u"%s %s(%s)" % (p.start_on, p.venue, p.jprefecture) for p in self.pageset.event.performances[:2]])
        return fmt % (link, link_label, description, performances)

    def deal_limit(self):
        N = (self.pageset.event.deal_open - self.today).days
        if N > 0:
            return u"販売開始まであと%d日" % N
        elif N == 0:
            return u"本日販売"

        N = (self.pageset.event.deal_close - self.today).days
        if N > 0:
            return u"販売終了まであと%d日" % N
        else:
            return u"販売終了"

    def deal_info_icons(self):
        import warnings
        warnings.warn("difficult. so supported this function is later.")
        return u'''\
<img src="/static/ticketstar/img/search/icon_release.gif" alt="一般発売" width="60" height="14" />
'''

    def deal_description(self):
        event = self.pageset.event
        label = u'<strong>チケット発売中</strong> ' if event.deal_open <= self.today and self.today <= event.deal_close else ''
        return u'%s%s' % (label, h.base.term(event.deal_open, event.deal_close))


    def purchase_link(self):
        fmt = u'''\
<a href="%s"><img src="/static/ticketstar/img/search/btn_detail.gif" alt="詳細へ" width="86" height="32" /></a>
<a href="%s"><img src="/static/ticketstar/img/search/btn_buy.gif" alt="購入へ" width="86" height="32" /></a>
'''
        return fmt % (h.link.to_publish_page_from_pageset(self.request, self.pageset), 
                      h.link.get_purchase_page_from_event(self.request, self.pageset.event))

