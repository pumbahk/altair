 # -*- coding: utf-8 -*-

import webhelpers.paginate as paginate

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_path

from ticketing.models import merge_session_with_post, record_to_multidict
from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap
from ticketing.venues.models import session, SeatType
from ticketing.seat_types.forms import SeatTypeForm

import sqlahelper
session = sqlahelper.get_session()

@view_defaults(decorator=with_bootstrap)
class SeatTypes(BaseView):

    @view_config(route_name='seat_types.show', renderer='ticketing:templates/seat_type/show.html')
    def show(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        query = session.query(SeatType).filter(SeatType.event_id == event_id)
        seat_types = paginate.Page(query.order_by(SeatType.id))

        f = SeatTypeForm()
        return {
            'form' : f,
            'seat_types' : seat_types,
            'event_id' : event_id,
        }

    @view_config(route_name='seat_types.new', request_method='POST')
    def new_post(self):
        event_id = int(self.request.matchdict.get('event_id', 0))

        f = SeatTypeForm(self.request.POST)
        record = merge_session_with_post(SeatType(), f.data)
        record.event_id = event_id
        SeatType.add(record)

        self.request.session.flash(u'席種を保存しました')
        return HTTPFound(location=route_path('seat_types.show', self.request, event_id=event_id))

    @view_config(route_name='seat_types.edit', request_method='POST')
    def edit_post(self):
        seat_type_id = int(self.request.matchdict.get('seat_type_id', 0))
        seat_type = SeatType.get(seat_type_id)
        if seat_type is None:
            return HTTPNotFound('seat_type id %d is not found' % id)

        seat_type.name = self.request.POST.get('name')
        SeatType.update(seat_type)

        self.request.session.flash(u'席種を保存しました')
        event_id = int(self.request.matchdict.get('event_id', 0))
        return HTTPFound(location=route_path('seat_types.show', self.request, event_id=event_id))

    @view_config(route_name='seat_types.delete')
    def delete(self):
        seat_type_id = int(self.request.matchdict.get('seat_type_id', 0))
        seat_type = SeatType.get(seat_type_id)
        if seat_type is None:
            return HTTPNotFound('seat_type id %d is not found' % id)

        SeatType.delete(seat_type)

        self.request.session.flash(u'席種を削除しました')
        event_id = int(self.request.matchdict.get('event_id', 0))
        return HTTPFound(location=route_path('seat_types.show', self.request, event_id=event_id))

