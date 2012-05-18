# -*- encoding:utf-8 -*-

from collections import namedtuple
from datetime import datetime

from . import searcher

# SearchResult = namedtuple("SearchResult", "category_icons page_description deal_limit deal_info_icons deal_description purchase_link")
class SearchResult(dict):
    pass

class SearchPageResource(object):
    def __init__(self, request):
        self.request = request
        
    def get_result_sequence_from_form(self, form):
        query = self._get_pageset_query(form)
        return result_sequence_from_query(query)

    # def _get_pageset_query(self, form):
    #     query_params = form.make_query_params()
    #     return searcher.get_pageset_query(query_params)        

    def _get_pageset_query(self, form):
        return [None, None, None, None, None]

def result_sequence_from_query(query, _nowday=datetime.now):
    """
    ここでは、検索結果のqueryを表示に適した形式に直す
    """
    today = _nowday()    
    for pageset in query:
        yield SearchResultRender(pageset, today)


class SearchResultRender(object):
    def __init__(self, pageset, today):
        self.pageset = pageset
        self.today = today

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
        ## todo: pagesetからカテゴリを取ってくる
        return u'<img src="/static/ticketstar/img/search/icon_music.gif" alt="音楽" width="82" height="20" />'

    def page_description(self):
        return u'''<p><a href="#">ソ・ジソブ　日本公式ファンクラブ1周年記念！2012 ファンミーティング in 東京</a></p>
<p class="align1">2012/3/24(土) 東京ビッグサイト（東京国際展示場）(東京都)</p>'''

    def deal_limit(self):
        return u'あと2日'
    
    def deal_info_icons(self):
        return u'<img src="/static/ticketstar/img/search/icon_release.gif" alt="一般発売" width="60" height="14" />'

    def deal_description(self):
        return u'<strong>チケット発売中</strong> ～2012/3/23(金) 23:59'

    def purchase_link(self):
        return u'<a href="#"><img src="/static/ticketstar/img/search/btn_buy.gif" alt="購入へ" width="86" height="32" /></a>'

