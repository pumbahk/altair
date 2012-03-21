 # -*- coding: utf-8 -*-

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_path

from ticketing.models import merge_session_with_post, record_to_multidict
from ticketing.models.boxoffice import session, Event, Performance

from forms import EventForm

from ticketing.fanstatic import with_bootstrap
from ticketing.fanstatic import bootstrap_need

import webhelpers.paginate as paginate

@view_config(route_name='admin.events.index', renderer='ticketing:templates/events/index.html', decorator=with_bootstrap)
def index(context, request):
    current_page = int(request.params.get("page", 0))
    page_url = paginate.PageURL_WebOb(request)
    query = session.query(Event)
    clients = paginate.Page(query.order_by(Event.id), current_page, url=page_url)
    return {
        'events'        : clients
    }


@view_config(route_name='admin.events.show', renderer='ticketing:templates/events/show.html', decorator=with_bootstrap)
def show(context, request):

    event_id = int(request.matchdict.get("event_id", 0))
    event = Event.get(event_id)
    if event is None:
        return HTTPNotFound("event id %d is not found" % event_id)

    current_page = int(request.params.get("page", 0))
    page_url = paginate.PageURL_WebOb(request)
    query = session.query(Performance).filter(Performance.event_id == event_id)
    performances = paginate.Page(query.order_by(Performance.id), current_page, url=page_url)

    return {
        'event'         : event,
        'performances'  : performances
    }

@view_config(route_name='admin.events.new', renderer='ticketing:templates/events/new.html', decorator=with_bootstrap)
def new(context, request):
    if 'submit' in request.POST:
        f = EventForm(request.POST)
        if f.validate():
            data = f.data
            record = Event()
            record = merge_session_with_post(record, data)
            Event.add(record)
            return HTTPFound(location=route_path('admin.events.index', request))
        else:
            return {
                'form':f
            }
    else:
        f = EventForm()
        # copy from event
        event_id = int(request.GET.get("event_id", 0))
        if event_id:
            event = Event.get(event_id)
            if event is None:
                return HTTPNotFound('Event not found')
            f.process(record_to_multidict(event))

        return {
            'form':f
        }

@view_config(route_name='admin.events.edit', renderer='ticketing:templates/events/edit.html', decorator=with_bootstrap)
def edit(context, request):
    event_id = int(request.matchdict.get("event_id", 0))
    event = Event.get(event_id)
    if event is None:
        return HTTPNotFound("client id %d is not found" % client_id)

    if 'submit' in request.POST:
        f = EventForm(request.POST)
        if f.validate():
            data = f.data
            record = merge_session_with_post(event, data)
            Event.update(record)
            return HTTPFound(location=route_path('admin.events.show', request, event_id=event.id))
        else:
            return {
                'form':f
            }
    else:
        appstruct = record_to_multidict(event)
        f = EventForm()
        print appstruct
        f.process(appstruct)
        return {
            'form' :f,
            'event' : event
        }
