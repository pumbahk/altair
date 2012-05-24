# -*- coding:utf-8 -*-
from pyramid.view import view_config
from pyramid.view import view_defaults
import logging
from ..front import api as front_api
from . import forms
from . import searcher

logger = logging.getLogger(__file__)

@view_config(route_name="page_search_input", renderer="altaircms:templates/front/layout/ticketstar.search.input.mako")
def page_search_input(request):
    """ 絞り込み検索フォーム画面
    """
    params = front_api.get_navigation_categories(request)
    params.update(forms=forms.get_search_forms())
    return params

@view_config(route_name="page_search_result", renderer="altaircms:templates/front/layout/ticketstar.search.mako")
def page_search_result(request):
    """ 詳細検索 検索結果
    """
    logger.debug("search GET params: %s" % request.GET)
    query_params = forms.get_search_forms(request.GET).make_query_params()
    result_seq = request.context.get_result_sequence_from_query_params(
        query_params, 
        searchfn=searcher.get_pageset_query_fullset
        )
    html_query_params = request.context.get_query_params_as_html(query_params)

    params = front_api.get_navigation_categories(request)
    params.update(result_seq=result_seq, query_params=html_query_params)
    return params

@view_defaults(route_name="page_search_by", renderer="altaircms:templates/front/layout/ticketstar.search.mako")
class SearchByKindView(object):
    def __init__(self, context, request):
        self.request = request
        self.context = context

    @view_config(match_param="kind=freeword", request_param="textfield")
    def search_by_freeword(self):
        """ フリーワード検索
        """
        ## 全文検索を使って検索。, で区切られた文字はandで結合
        query_params = dict(query=self.request.GET.get("textfield", u""), query_cond="intersection")

        result_seq = self.context.get_result_sequence_from_query_params(
            query_params,
            searchfn=searcher.get_pageset_query_from_freeword
            )
        ## query_paramsをhtml化する
        html_query_params = self.context.get_query_params_as_html(query_params)
        ### header page用のcategoryを集めてくる
        params = front_api.get_navigation_categories(self.request)
        params.update(result_seq=result_seq, query_params=html_query_params)
        return params

    @view_config(match_param="kind=genre", request_param="genre")
    def search_by_genre(self):
        """ ジャンルで検索
        top_category -> sub_categoryの２段階までしかサポートしていない。
        sub_category == ジャンル
        """
        forms.
        genre = self.request.GET["genre"]
        query_params = dict(top_categories=[], 
                            sub_categories=[], 
                            category_tree=MarkedTree)

        result_seq = self.context.get_result_sequence_from_query_params(
            query_params,
            searchfn=searcher.get_pageset_query_from_freeword
            )
        ## query_paramsをhtml化する
        html_query_params = self.context.get_query_params_as_html(query_params)
        ### header page用のcategoryを集めてくる
        params = front_api.get_navigation_categories(self.request)
        params.update(result_seq=result_seq, query_params=html_query_params)
        return params

    @view_config(match_param="kind=mock")
    def search_by_mock(self):
        """ mockup (for testing)
        """
        class mock_query_parms(object):
            @classmethod
            def __html__(cls):
                return "mock-dummy"
        html_query_params = mock_query_parms
        result_seq = self.context.get_result_sequence_from_query_params(
            mock_query_parms, 
            )
        ### header page用のcategoryを集めてくる
        params = front_api.get_navigation_categories(self.request)
        params.update(result_seq=result_seq, query_params=html_query_params)
        return params

    
