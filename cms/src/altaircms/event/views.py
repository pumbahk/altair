# coding: utf-8
import logging
import json
import sqlalchemy as sa
logger = logging.getLogger(__file__)
from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid.httpexceptions import HTTPCreated, HTTPForbidden, HTTPBadRequest, HTTPNotFound, HTTPFound

from ..lib.fanstatic_decorator import with_bootstrap
from ..auth.api import get_or_404
from .models import Event
from . import forms
from . import searcher
from ..models import DBSession
from . import helpers as h
from .event_info import get_event_notify_info
from ..page.subscribers import notify_page_update
##
## CMS view
##
@view_defaults(route_name="event_takein_pageset", renderer="altaircms:templates/event/takein_pageset.mako", 
               permission="event_update", 
               decorator=with_bootstrap)
class PageSetTakein(object):
    """ pagesetを配下のページとして取り込む"""
    def __init__(self, request):
        self.request = request

    @view_config(request_method="GET")
    def input_view(self):
        event = get_or_404(self.request.allowable(Event), Event.id==self.request.matchdict["event_id"])
        form = forms.EventTakeinPageForm(event=event)
        return {"form": form, "event": event}

    @view_config(request_method="POST")
    def page_takein(self):
        event = get_or_404(self.request.allowable(Event), Event.id==self.request.matchdict["event_id"])
        form = forms.EventTakeinPageForm(self.request.POST)
        if form.validate():
            pageset = form.data["pageset"]
            pageset.take_in_event(event)
            for page in pageset.pages:
                notify_page_update(self.request, page)
            DBSession.add(pageset)
            return HTTPFound(self.request.route_url("event", id=event.id))
        else:
            return {"form": form, "event": event}



@view_config(route_name='event', renderer='altaircms:templates/event/view.mako', permission='event_read',
             decorator=with_bootstrap)
def view(request):
    id_ = request.matchdict['id']

    event = request.allowable(Event).filter_by(id=id_).first()
    if event is None:
        raise HTTPNotFound() ##
    performances = event.performances
    sales = event.sales
    return dict(
        event=event,
        performances=performances, 
        sales=sales, 
        myhelpers=h
    )

@view_config(route_name='event_list', renderer='altaircms:templates/event/list.mako', permission='event_read', request_method="GET", 
             decorator=with_bootstrap)
def event_list(request):
    events = request.allowable(Event)

    params = dict(request.GET)
    if "page" in params:
        params.pop("page") ## pagination
    if params:
        search_form = forms.EventSearchForm(request.GET)
        if search_form.validate():
            events = searcher.make_event_search_query(request, search_form.data, qs=events)
    else:
        search_form = forms.EventSearchForm()

    return dict(
        events=events.order_by(sa.desc("updated_by")), 
        search_form=search_form, 
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

