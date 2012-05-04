 # -*- coding: utf-8 -*-

import webhelpers.paginate as paginate

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_path

from ticketing.models import merge_session_with_post, record_to_multidict
from ticketing.views import BaseView
from ticketing.models import DBSession
from ticketing.fanstatic import with_bootstrap
from ticketing.events.models import Event, Performance
from ticketing.events.forms import EventForm

@view_defaults(decorator=with_bootstrap, permission="event_editor")
class Events(BaseView):

    @view_config(route_name='events.index', renderer='ticketing:templates/events/index.html')
    def index(self):
        current_page = int(self.request.params.get('page', 0))
        sort = self.request.GET.get('sort', 'Event.id')
        direction = self.request.GET.get('direction', 'asc')
        if direction not in ['asc', 'desc']: direction = 'asc'

        page_url = paginate.PageURL_WebOb(self.request)
        query = DBSession.query(Event).filter(Event.organization_id == int(self.context.user.organization_id))
        query = query.order_by(sort + ' ' + direction)

        events = paginate.Page(query, page=current_page, items_per_page=3, url=page_url)

        f = EventForm()
        return {
            'form':f,
            'events':events,
        }

    @view_config(route_name='events.show', renderer='ticketing:templates/events/show.html')
    def show(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        current_page = int(self.request.params.get('page', 0))
        sort = self.request.GET.get('sort', 'Performance.id')
        direction = self.request.GET.get('direction', 'asc')
        if direction not in ['asc', 'desc']: direction = 'asc'

        page_url = paginate.PageURL_WebOb(self.request)
        query = DBSession.query(Performance).filter(Performance.event_id == event_id)
        query = query.order_by(sort + ' ' + direction)

        performances = paginate.Page(query, current_page, items_per_page=10, url=page_url)

        f = EventForm()
        return {
            'form':f,
            'event':event,
            'performances':performances,
        }

    @view_config(route_name='events.new', request_method='GET', renderer='ticketing:templates/events/edit.html')
    def new_get(self):
        f = EventForm()

        event_id = int(self.request.matchdict.get('event_id', 0))
        if event_id:
            event = Event.get(event_id)
            if event is None:
                return HTTPNotFound('event id %d is not found' % event_id)
            event = record_to_multidict(event)
            event.pop('id')
            f.process(event)

        return {
            'form':f
        }

    @view_config(route_name='events.new', request_method='POST', renderer='ticketing:templates/events/edit.html')
    def new_post(self):
        f = EventForm(self.request.POST)

        if f.validate():
            event = merge_session_with_post(Event(), f.data)
            event.organization_id = self.context.user.organization_id
            event.save()

            self.request.session.flash(u'イベントを登録しました')
            return HTTPFound(location=route_path('events.index', self.request))
        else:
            return {
                'form':f
            }

    @view_config(route_name='events.edit', request_method='GET', renderer='ticketing:templates/events/edit.html')
    def edit_get(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        f = EventForm()
        f.process(record_to_multidict(event))
        return {
            'form':f,
            'event':event
        }

    @view_config(route_name='events.edit', request_method='POST', renderer='ticketing:templates/events/edit.html')
    def edit_post(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        f = EventForm(self.request.POST)
        if f.validate():
            event = merge_session_with_post(event, f.data)
            event.organization_id = self.context.user.organization_id
            event.save()

            self.request.session.flash(u'イベントを保存しました')
            return HTTPFound(location=route_path('events.show', self.request, event_id=event.id))
        else:
            return {
                'form':f,
                'event':event
            }

    @view_config(route_name='events.delete')
    def delete(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        event.delete()

        self.request.session.flash(u'イベントを削除しました')
        return HTTPFound(location=route_path('events.index', self.request))
