# -*- coding:utf-8 -*-
from pyramid.view import view_config
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
    query_form = forms.get_search_forms(request.GET)

    result_seq = request.context.get_result_sequence_from_form(
        query_form,
        searchfn=searcher.get_pageset_query_fullset
        )

    params = front_api.get_navigation_categories(request)
    params.update(result_seq=result_seq)
    return params

@view_config(route_name="page_search_result_simple", renderer="altaircms:templates/front/layout/ticketstar.search.mako")
def page_freeword_result(request):
    ## 全文検索を使って検索。, で区切られた文字はandで結合
    query_params = dict(query=request.GET.get("textfield", u""), query_cond="intersection")

    result_seq = request.context.get_result_sequence_from_query_params(
        query_params,
        searchfn=searcher.get_pageset_query_from_freeword
        )
    params = front_api.get_navigation_categories(request)
    params.update(result_seq=result_seq)
    return params
