# -*- coding: utf-8 -*-

from pyramid.view import view_config
from cmsmobile.event.detailsearch.forms import DetailSearchForm

@view_config(route_name='detailsearch', request_method="GET", renderer='cmsmobile:templates/detailsearch/detailsearch.mako')
def move_detailsearch(request):

    form = DetailSearchForm()

    return {
        'form':form
    }

@view_config(route_name='detailsearch', request_method="POST", renderer='cmsmobile:templates/searchresult/detailsearch.mako')
def move_detailsearch_post(request):

    form = DetailSearchForm()

    return {
        'form':form
    }
