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
    params = front_api.get_navigation_categories(request)
    params.update(forms=forms.get_search_forms())
    return params

@view_config(route_name="page_search_result", renderer="altaircms:templates/front/layout/ticketstar.search.mako")
def page_search_result(request):
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

    @view_config(match_param="kind=freeword")
    def search_as_freeword(self):
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

    
