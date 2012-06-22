# coding: utf-8
import logging
import json
logger = logging.getLogger(__file__)
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPCreated, HTTPForbidden, HTTPBadRequest, HTTPNotFound

from altaircms.models import Sale
from .models import Event
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
    if apikey is None:
        return HTTPForbidden("")
    if not h.validate_apikey(request, apikey):
        return HTTPForbidden(body=json.dumps({u'status':u'error', u'message':u'access denined'}))

    backend_id = request.matchdict["event_id"]
    logger.debug("*api* event info: apikey=%s event.id=%s (backend)" % (apikey, backend_id))
    event = Event.query.filter_by(backend_id=backend_id).first()

    if event is None:
        return dict(event=None)
    try:
        return dict(event=dict(subtitle=event.subtitle, 
                               contact=h.base.nl_to_br(event.inquiry_for), 
                               notice=h.base.nl_to_br(event.notice), 
                               performer=event.performers, 
                               ))
    except ValueError as e:
        logger.exception(e)
        return HTTPBadRequest(body=json.dumps({u'status':u'error', u'message':unicode(e), "apikey": apikey}))
