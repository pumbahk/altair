# coding: utf-8
import logging
import json

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPCreated, HTTPForbidden, HTTPBadRequest

from altaircms.models import Performance
from .models import Event
from altaircms.page.models import Page
from altaircms.lib.fanstatic_decorator import with_bootstrap

from altaircms.event.forms import EventForm
from . import helpers as h


##
## CMS view
##
@view_config(route_name='event', renderer='altaircms:templates/event/view.mako', permission='event_read',
             decorator=with_bootstrap)
def view(request):
    id_ = request.matchdict['id']

    event = Event.query.filter_by(id=id_).first()
    pages = Page.query.filter_by(event_id=id_)
    performances = Performance.query.filter_by(event_id=id_)
    return dict(
        event=event,
        pages=pages, 
        performances=performances
    )


@view_config(route_name='event_list', renderer='altaircms:templates/event/list.mako', permission='event_read', request_method="GET", 
             decorator=with_bootstrap)
def event_list(request):
    events = Event.query
    form = EventForm()
    return dict(
        form=form,
        events=events
    )

##
## バックエンドとの通信用
##
@view_config(route_name="api_event_register", request_method="POST")
def event_register(request):
    apikey = request.headers.get('X-Altair-Authorization', None)
    if apikey is None:
        return HTTPForbidden("")
    if not h.validate_apikey(request, apikey):
        return HTTPForbidden(body=json.dumps({u'status':u'error', u'message':u'access denined'}))
    try:
        h.parse_and_save_event(request, request.json_body)
        return HTTPCreated(body=json.dumps({u'status':u'success'}))
    except ValueError as e:
        logging.exception(e)
        return HTTPBadRequest(body=json.dumps({u'status':u'error', u'message':unicode(e)}))
