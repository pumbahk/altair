# -*- encoding:utf-8 -*-

from datetime import datetime
# from collections import namedtuple
# SearchResult = namedtuple("SearchResult", "category_icons page_description deal_limit deal_info_icons deal_description purchase_link")
import logging
logger = logging.getLogger(__file__)

from . import searcher
import altaircms.helpers as h
import pprint

class SearchResult(dict):
    pass

class SearchPageResource(object):
    def __init__(self, request):
        self.request = request

    def result_sequence_from_query(self, query, _nowday=datetime.now):
        """
        ここでは、検索結果のqueryを表示に適した形式に直す
        """
        today = _nowday()    
        for pageset in query:
            yield SearchResultRender(pageset, today, self.request)
        
    def get_result_sequence_from_form(self, form):
        query_params = form.make_query_params()
        logger.info(pprint.pformat(query_params))
        query = self._get_pageset_query(query_params)
        return self.result_sequence_from_query(query)

    def _get_pageset_query(self, query_params):
        return searcher.get_pageset_query(self.request, query_params)

    # def _get_pageset_query(self, query_params): ## dummy 
    #     from altaircms.page.models import PageSet, Page
    #     from altaircms.event.models import Event
    #     event = Event(subtitle=u"ソ・ジソブ　日本公式ファンクラブ1周年記念！2012 ファンミーティング in 東京", 
    #                   description=u"2012/3/24(土) 東京ビッグサイト（東京国際展示場）(東京都)", 
    #                   event_open=datetime(2012, 5, 1))
    #     page_set = PageSet(url="http://www.example.com", version_counter=1, event=event)
    #     page = Page(pageset=page_set, version=1, 
    #                 description="楽天チケットイベント詳細ページです", 
    #                 )
    #     return [page_set]*5


class SearchResultRender(object):
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
        return SearchResult(
            category_icons = self.category_icons(), 
            page_description = self.page_description(),
            deal_limit = self.deal_limit(),
            deal_info_icons = self.deal_info_icons(),
            deal_description = self.deal_description(),
            purchase_link = self.purchase_link()
            )

    def category_icons(self):
        import warnings
        warnings.warn("difficult. so supported this function is later.")
        return u'<img src="/static/ticketstar/img/search/icon_music.gif" alt="音楽" width="82" height="20" />'

    def page_description(self):
        fmt =  u"""\
<p><a href="%s">%s</a></p>
<p>%s</p>
<p class="align1">%s</p>
"""
        link = h.link.to_publish_page_from_pageset(self.request, self.pageset)
        link_label = self.pageset.event.title
        description = self.pageset.event.description
        ## todo. ticketから開催場所の情報を取り出す
        performances = self.pageset.event.performances[:5]
        return fmt % (link, link_label, description, performances)

    def deal_limit(self):
        N = (self.pageset.event.event_open - self.today).days
        return u"あと%d日" % N
        #return u"開演まであと%d日" % N
    
    def deal_info_icons(self):
        import warnings
        warnings.warn("difficult. so supported this function is later.")
        return u'<img src="/static/ticketstar/img/search/icon_release.gif" alt="一般発売" width="60" height="14" />'

    def deal_description(self):
        event = self.pageset.event
        return u'<strong>チケット発売中</strong> %s' % (h.base.term(event.deal_open, event.deal_close))

    def purchase_link(self):
        import warnings
        warnings.warn("difficult. so supported this function is later.")
        return u'dummy<a href="#"><img src="/static/ticketstar/img/search/btn_buy.gif" alt="購入へ" width="86" height="32" /></a>'

