 # -*- coding: utf-8 -*-

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_path

from ticketing.models import merge_session_with_post, record_to_multidict
from models import session, Event, Performance
from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap

from forms import EventForm

import webhelpers.paginate as paginate

@view_defaults(decorator=with_bootstrap)
class Events(BaseView):

    @view_config(route_name='events.index', renderer='ticketing:templates/events/index.html')
    def index(self):
        current_page = int(self.request.params.get("page", 0))
        page_url = paginate.PageURL_WebOb(self.request)
        query = session.query(Event)
        clients = paginate.Page(query.order_by(Event.id), current_page, url=page_url)
        return {
            'events'        : clients
        }


    @view_config(route_name='events.show', renderer='ticketing:templates/events/show.html')
    def show(self):

        event_id = int(self.request.matchdict.get("event_id", 0))
        event = Event.get(event_id)
        if event is None:
            return HTTPNotFound("event id %d is not found" % event_id)

        current_page = int(self.request.params.get("page", 0))
        page_url = paginate.PageURL_WebOb(self.request)
        query = session.query(Performance).filter(Performance.event_id == event_id)
        performances = paginate.Page(query.order_by(Performance.id), current_page, url=page_url)

        return {
            'event'         : event,
            'performances'  : performances
        }

    @view_config(route_name='events.new', request_method="GET", renderer='ticketing:templates/events/new.html')
    def new_get(self):
        f = EventForm()
        event_id = int(self.request.GET.get("event_id", 0))
        if event_id:
            event = Event.get(event_id)
            if event is None:
                return HTTPNotFound('Event not found')
            f.process(record_to_multidict(event))

        return {
            'form':f
        }

    @view_config(route_name='events.new', request_method="POST", renderer='ticketing:templates/events/new.html')
    def new_post(self):
        f = EventForm(self.request.POST)
        if f.validate():
            data = f.data
            record = Event()
            record = merge_session_with_post(record, data)
            Event.add(record)
            return HTTPFound(location=route_path('events.index', self.request))
        else:
            return {
                'form':f
            }

    @view_config(route_name='events.edit', request_method="GET", renderer='ticketing:templates/events/edit.html')
    def edit_get(self):
        event_id = int(self.request.matchdict.get("event_id", 0))
        event = Event.get(event_id)
        if event is None:
            return HTTPNotFound("client id %d is not found" % event_id)

        app_structs = record_to_multidict(event)
        f = EventForm()
        f.process(app_structs)
        return {
            'form' :f,
            'event' : event
        }

    @view_config(route_name='events.edit', request_method="POST", renderer='ticketing:templates/events/edit.html')
    def edit_post(self):
        event_id = int(self.request.matchdict.get("event_id", 0))
        event = Event.get(event_id)
        if event is None:
            return HTTPNotFound("client id %d is not found" % event_id)

        f = EventForm(self.request.POST)
        if f.validate():
            data = f.data
            record = merge_session_with_post(event, data)
            Event.update(record)
            return HTTPFound(location=route_path('events.show', self.request, event_id=event.id))
        else:
            return {
                'form':f
            }