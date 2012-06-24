# coding: utf-8
import logging
import json
logger = logging.getLogger(__file__)
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPCreated, HTTPForbidden, HTTPBadRequest, HTTPNotFound

from ..models import Sale
from ..lib.fanstatic_decorator import with_bootstrap

from .models import Event
from .forms import EventForm

from . import helpers as h
from .event_info import get_event_notify_info
##
## CMS view
##
@view_config(route_name='event', renderer='altaircms:templates/event/view.mako', permission='event_read',
             decorator=with_bootstrap)
def view(request):
    id_ = request.matchdict['id']

    event = Event.query.filter_by(id=id_).first()
    performances = event.performances
    sales = Sale.query.filter_by(event_id=id_)
    return dict(
        event=event,
        performances=performances, 
        sales=sales
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
        logger.exception(e)
        return HTTPBadRequest(body=json.dumps({u'status':u'error', u'message':unicode(e), "apikey": apikey}))


@view_config(route_name="api_event_info", request_method="GET", renderer="json")
def event_info(request):
    apikey = request.headers.get('X-Altair-Authorization', None)
    backend_id = request.matchdict["event_id"]

    if apikey is None:
        logger.info("*api* event info: apikey not found (backend event_id=%s)" % backend_id)
        return HTTPForbidden("")
    if not h.validate_apikey(request, apikey):
        logger.warn("*api* event info: invalid api key %s (backend event id=%s)" % (apikey, backend_id))
        return HTTPForbidden(body=json.dumps({u'status':u'error', u'message':u'access denined'}))

    event = Event.query.filter_by(backend_id=backend_id).first()

    if event is None:
        logger.warn("*api* event info: event not found (backend event_id=%s)" % backend_id)
        return dict(event=[])
    try:
        return get_event_notify_info(event)
    except ValueError as e:
        logger.exception(e)
        return HTTPBadRequest(body=json.dumps({u'status':u'error', u'message':unicode(e), "apikey": apikey}))

