# -*- coding: utf-8 -*-

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_path

from ticketing.models import merge_session_with_post, record_to_appstruct
from ticketing.models.boxoffice import session, Event

from forms import EventForm
from deform.form import Form,Button
from deform.exception import ValidationFailure

import webhelpers.paginate as paginate

@view_config(route_name='admin.events.index', renderer='ticketing:templates/events/index.html')
def index(context, request):
    current_page = int(request.params.get("page", 0))
    page_url = paginate.PageURL_WebOb(request)
    query = session.query(Event)
    clients = paginate.Page(query.order_by(Event.id), current_page, url=page_url)
    return {
        'events': clients
    }


@view_config(route_name='admin.events.show', renderer='ticketing:templates/events/show.html')
def show(context, request):
    client_id = int(request.matchdict.get("event_id", 0))
    client = Event.get(client_id)
    if client is None:
        return HTTPNotFound("client id %d is not found" % client_id)
    return {
        'event' : client
    }

@view_config(route_name='admin.events.new', renderer='ticketing:templates/events/new.html')
def new(context, request):
    f = Form(EventForm(), buttons=(Button(name='submit',title=u'新規'),))
    if 'submit' in request.POST:
        controls = request.POST.items()
        try:
            data = f.validate(controls)
            record = Event()
            record = merge_session_with_post(record, controls)
            Event.add(record)
            return HTTPFound(location=route_path('admin.events.index', request))
        except ValidationFailure, e:
            return {'form':e.render()}
    else:
        return {
            'form':f.render()
        }

@view_config(route_name='admin.events.edit', renderer='ticketing:templates/events/edit.html')
def edit(context, request):
    event_id = int(request.matchdict.get("event_id", 0))
    event = Event.get(event_id)
    if event is None:
        return HTTPNotFound("client id %d is not found" % client_id)
    f = Form(EventForm(), buttons=(Button(name='submit',title=u'更新'),))
    if 'submit' in request.POST:
        controls = request.POST.items()
        try:
            data = f.validate(controls)
            record = merge_session_with_post(event, controls)
            Event.update(record)
            return HTTPFound(location=route_path('admin.events.index', request))
        except ValidationFailure, e:
            return {'form':e.render()}
    else:
        appstruct = record_to_appstruct(event)
        return {
            'form':f.render(appstruct=appstruct)
        }
