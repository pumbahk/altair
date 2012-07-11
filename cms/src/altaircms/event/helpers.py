import json
from pyramid.response import Response
from .interfaces import IAPIKeyValidator, IEventRepository

## for viewlet
from pyramid.view import render_view_to_response
from markupsafe import Markup
from ..viewlet import api as va

## for fulltext search
# -*

from altaircms.solr.api import pageset_id_list_from_word

def validate_apikey(request, apikey):
    reg = request.registry
    validator = reg.getUtility(IAPIKeyValidator)
    return validator(apikey)
    
def parse_and_save_event(request, data):
    reg = request.registry
    repository = reg.getUtility(IEventRepository)
    return repository.parse_and_save_event(request, data)

def pageset_describe_viewlet(request, event):
    va.set_event(request, event)
    va.set_pagesets(request, event.pagesets)
    response = render_view_to_response(request.context, request, name="describe_pageset")
    if response is None:
        raise ValueError
    return Markup(response.text)

def performance_describe_viewlet(request, event):
    va.set_event(request, event)
    va.set_performances(request, event.performances)
    response = render_view_to_response(request.context, request, name="describe_performance")
    if response is None:
        raise ValueError
    return Markup(response.text)

def sale_describe_viewlet(request, event):
    va.set_event(request, event)
    va.set_sales(request, event.sales)
    response = render_view_to_response(request.context, request, name="describe_sale")
    if response is None:
        raise ValueError
    return Markup(response.text)
