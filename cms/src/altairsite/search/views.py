# -*- coding:utf-8 -*-
from pyramid.view import view_config
from ..front import api as front_api
from . import forms

@view_config(route_name="detail_page_search_input", renderer="altaircms:templates/front/layout/ticketstar.search.input.mako")
def detail_page_search_input(request):
    params = front_api.get_navigation_categories(request)
    params.update(forms=forms.get_search_forms())
    return params

@view_config(route_name="detail_page_search", renderer="altaircms:templates/front/ticketstar/search/detail_search_result.mako")
def detail_page_search(request):
    query_form = forms.get_search_forms(request.POST)
    result_seq = request.context.get_result_sequence_from_form(query_form)

    params = front_api.get_navigation_categories(request)
    params.update(result_seq=result_seq)
    return params

@view_config(route_name="page_search", renderer="altaircms:templates/front/ticketstar/search/search_result.mako")
def page_search(request):
    params = front_api.get_navigation_categories(request)
    params.update(results=[mockup_search_result()]*5)
    return params
