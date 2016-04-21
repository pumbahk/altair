# coding: utf-8
import logging
import json
import sqlalchemy as sa
logger = logging.getLogger(__name__)
from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid.httpexceptions import HTTPCreated, HTTPForbidden, HTTPBadRequest, HTTPNotFound, HTTPFound

from ..lib.fanstatic_decorator import with_bootstrap
from ..auth.api import get_or_404
from ..auth.models import Organization
from altaircms.auth.models import Host
from . import forms
from . import searcher
from ..models import DBSession
from .models import Event, Word
from . import helpers as h
from .event_info import get_event_notify_info
from ..page.subscribers import notify_page_update
from .receivedata import InvalidParamaterException
from altaircms.viewlib import apikey_required
from altaircms.viewlib import success_result, failure_result
from altaircms.api import (
    get_hostname_from_request, 
    get_usersite_url_builder, 
    get_mobile_url_builder, 
    get_smartphone_url_builder, 
    get_backend_url_builder, 
    get_cms_url_builder, 
    )
from altair.sqlahelper import get_db_session
## CMS view
##
@view_defaults(route_name="event_takein_pageset", renderer="altaircms:templates/event/takein_pageset.html", 
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

## todo:move
class Candidates(object):
    def __init__(self, ks, values):
        assert len(ks) == len(values)
        for k in ks:
            setattr(self, k, k)
        self.candidates = ks
        self.pairs = zip(ks, values)
        self.data = dict(self.pairs)

    def __contains__(self, k):
        return k in self.candidates

    def __getitem__(self, k):
        return self.data[k]

SectionCandidates = Candidates(("pageset", "performance", "description", "accesskey"), 
                               [u"配下のページ", u"パフォーマンス", u"文言情報", u"アクセスキー"] )
def in_section(info, request):
    return request.matchdict.get("section") in SectionCandidates

@view_config(route_name="event", 
             renderer='altaircms:templates/event/view.html', permission='event_read',decorator=with_bootstrap)
@view_config(route_name='event_detail', custom_predicates=(in_section,), 
             renderer='altaircms:templates/event/view.html', permission='event_read',decorator=with_bootstrap)
def event_detail(context, request):
        section = request.matchdict.get("section", "pageset")
        id_ = request.matchdict['id']
        event = get_or_404(request.allowable(Event), Event.id==id_)
        return dict(
            panel_name = u"event_%s" % section,  #use layout?
            section=section, 
            section_pairs = SectionCandidates.pairs, 
            event=event,
            myhelpers=h
        )

@view_config(route_name='event_list', renderer='altaircms:templates/event/list.html', permission='event_read', request_method="GET", 
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

    word = None
    if "word" in params and 0 < len(params["word"]):
        word = Word.query.filter(Word.id==int(params["word"]), Word.deleted_at==None).first()

    return dict(
        events=events.order_by(sa.desc(Event.updated_at)),
        search_form=search_form,
        word=word,
    )

##
## バックエンドとの通信用
##

@view_config(route_name="api_event_register", request_method="POST")
def event_register(request):
    apikey = request.headers.get('X-Altair-Authorization', None)
    if apikey is None:
        logger.warn("*event register api* apikey is not found: params=%s",  request.POST)
        return HTTPForbidden("")
    if not h.validate_apikey(request, apikey):
        logger.warn("*event register api* invalid api key: %s" % apikey)
        return HTTPForbidden(body=json.dumps({u'status':u'error', u'message':u'access denined'}))
    try:
        h.parse_and_save_event(request, request.json_body)
        return HTTPCreated(body=json.dumps({u'status':u'success'}))
    except InvalidParamaterException as e:
        logger.warn("*event register api* invalid paramater received: reason: '%s.'\ndata = %s" % (str(e),request.json_body ))
        _tmp_save(request.json_body)
        return HTTPBadRequest(body=json.dumps({u'status':u'error', u'message':unicode(e), "apikey": apikey}))
    except Exception as e:
        logger.exception(e)
        _tmp_save(request.json_body)
        return HTTPBadRequest(body=json.dumps({u'status':u'error', u'message':unicode(e), "apikey": apikey}))

import tempfile
def _tmp_save(data):
    try:
        filename = tempfile.mktemp()
        logger.warn("temporary save: %s" % filename)
        with open(filename, "w") as wf:
            wf.write(json.dumps(data))
    except Exception, e:
        logger.exception(str(e))


@view_config(route_name="api_event_info", request_method="GET", renderer="json")
def event_info(request):
    apikey = request.headers.get('X-Altair-Authorization', None)
    backend_id = request.matchdict["event_id"]
    session = get_db_session(request, name="slave")

    if apikey is None:
        logger.info("*api* event info: apikey not found (backend event_id=%s)" % backend_id)
        return HTTPForbidden("")
    if not h.validate_apikey(request, apikey):
        logger.warn("*api* event info: invalid api key %s (backend event id=%s)" % (apikey, backend_id))
        return HTTPForbidden(body=json.dumps({u'status':u'error', u'message':u'access denined'}))

    event = session.query(Event).filter_by(backend_id=backend_id).first()

    if event is None:
        logger.info("*api* event info: event not found (backend event_id=%s)" % backend_id)
        return dict(event=[])
    try:
        return get_event_notify_info(event, session=session)
    except ValueError as e:
        logger.exception(e)
        return HTTPBadRequest(body=json.dumps({u'status':u'error', u'message':unicode(e), "apikey": apikey}))

@view_config(route_name="api_event_url_candidates", request_method="GET", renderer="json", 
             custom_predicates=(apikey_required("*event url candidates*"), ))
def api_event_url_candidates(context, request):
    backend_organization_id = request.GET["backend_organization_id"]
    organization = Organization.query.filter_by(backend_id=backend_organization_id).first()
    if organization is None:
        return failure_result(message="organization is not found backend_id = {} ".format(backend_organization_id))

    if request.GET.get("event_id"):
        event = Event.query.filter_by(organization_id=organization.id, id=request.GET["event_id"]).first()
        if event is None:
            return failure_result(message="event is not found")
    else:
        event = Event.query.filter_by(organization_id=organization.id, backend_id=request.GET["backend_event_id"]).first()
        if event is None:
            return success_result(dict(backend_event_id=request.GET["backend_event_id"], urls={}))

    pc_url_builder = get_usersite_url_builder(request)
    mb_url_builder = get_mobile_url_builder(request)
    sp_url_builder = get_smartphone_url_builder(request)
    backend_url_builder = get_backend_url_builder(request)
    cms_url_builder = get_cms_url_builder(request)

    if request.allowable(Host):
        qs = Host.query.filter_by(organization_id=organization.id)
        host = qs.first()
        if host is not None:
            hostname = host.host_name
    else:
        hostname = None
    return success_result({"event_id": event.id, 
            "backend_event_id": event.backend_id, 
            "urls": {"usersite":
                         {"pc": [pc_url_builder.front_page_url(request, p, hostname=hostname) for p in event.pagesets],
                          "mb": [mb_url_builder.event_page_url(request, event, hostname=hostname)],
                          "sp": [sp_url_builder.event_page_url(request, event, hostname=hostname)]
                          }, 
                     "cms": [cms_url_builder.event_page_url(request, event)],
                     "backend": [backend_url_builder.event_page_url(request, event)]}
                           })
