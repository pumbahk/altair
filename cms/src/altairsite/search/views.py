# -*- coding:utf-8 -*-
from pyramid.view import view_config
from ..front import api as front_api
@view_config(route_name="detail_page_search_input", renderer="altaircms:templates/front/ticketstar/search/detail_search_input.mako")
def detail_page_search_input(request):
    return {}

@view_config(route_name="detail_page_search", renderer="altaircms:templates/front/ticketstar/search/detail_search_result.mako")
def detail_page_search(request):
    return {}

@view_config(route_name="page_search", renderer="altaircms:templates/front/ticketstar/search/search_result.mako")
def page_search(request):
    params = front_api.get_navigation_categories(request)
    params.update(results=[mockup_search_result()]*5)
    return params



### mockups ###
class RawText(object):
    def __init__(self, text):
        self.text = text

    def __html__(self):
        return self.text

from collections import namedtuple
SearchResult = namedtuple("SearchResult", "category_icons page_description sales_limit sales_info_icons sales_description purchase_link")
def mockup_search_result():
    return SearchResult(
        category_icons = RawText(u'<img src="/static/ticketstar/img/search/icon_music.gif" alt="音楽" width="82" height="20" />'), 
        page_description =RawText(u'''<p><a href="#">ソ・ジソブ　日本公式ファンクラブ1周年記念！2012 ファンミーティング in 東京</a></p>
<p class="align1">2012/3/24(土) 東京ビッグサイト（東京国際展示場）(東京都)</p>'''), 
        sales_limit=RawText(u'あと2日'), 
        sales_info_icons=RawText(u'<img src="/static/ticketstar/img/search/icon_release.gif" alt="一般発売" width="60" height="14" />'), 
        sales_description=RawText(u'<strong>チケット発売中</strong> ～2012/3/23(金) 23:59'), 
        purchase_link=RawText(u'<a href="#"><img src="/static/ticketstar/img/search/btn_buy.gif" alt="購入へ" width="86" height="32" /></a>')
        )
