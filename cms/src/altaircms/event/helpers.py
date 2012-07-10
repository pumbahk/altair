import json
from pyramid.response import Response
from .interfaces import IAPIKeyValidator, IEventRepository

def validate_apikey(request, apikey):
    reg = request.registry
    validator = reg.getUtility(IAPIKeyValidator)
    return validator(apikey)
    
def parse_and_save_event(request, data):
    reg = request.registry
    repository = reg.getUtility(IEventRepository)
    return repository.parse_and_save_event(data)

from pyramid.view import render_view_to_response
from markupsafe import Markup
from ..viewlet import api as va

def pageset_describe_viewlet(request, event):
    va.set_event(request, event)
    response = render_view_to_response(request.context, request, name="pageset_from_event")
    if response is None:
        raise ValueError
    return Markup(response.text)

def performance_describe_viewlet(request, event):
    va.set_event(request, event)
    response = render_view_to_response(request.context, request, name="performance_from_event")
    if response is None:
        raise ValueError
    return Markup(response.text)

def sale_describe_viewlet(request, event):
    va.set_event(request, event)
    response = render_view_to_response(request.context, request, name="sale_from_event")
    if response is None:
        raise ValueError
    return Markup(response.text)
