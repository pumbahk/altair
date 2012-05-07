# coding: utf-8
import logging
import json
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response
from sqlalchemy.orm import joinedload, noload
from urllib2 import urlopen

from ticketing.models import DBSession
from .models import Venue, Seat, SeatAttribute, VenueArea, seat_venue_area_table
from ticketing.products.models import SeatStock

@view_config(route_name="api.get_drawing", request_method="GET")
def get_drawing(request):
    venue_id = int(request.matchdict.get('venue_id', 0))
    venue = Venue.get(venue_id)
    if venue is None:
        return HTTPNotFound("Venue id #%d not found" % venue_id)

    return Response(app_iter=urlopen(venue.site.drawing_url), content_type='text/xml; charset=utf-8')

@view_config(route_name="api.get_seats", request_method="GET", renderer='json')
def get_seats(request):
    venue_id = int(request.matchdict.get('venue_id', 0))
    venue = Venue.get(venue_id)
    if venue is None:
        return HTTPNotFound("Venue id #%d not found" % venue_id)

    seats_data = {}
    for seat in DBSession.query(Seat).options(joinedload('attributes'), joinedload('areas')).filter_by(venue=venue):
        seat_datum = {
            'id': seat.l0_id,
            'seat_type_id': seat.seat_type_id,
            'stock_holder_id': seat.seat_stock and seat.seat_stock.stock and seat.seat_stock.stock.holder and seat.seat_stock.stock.holder.id,
            'areas': [area.id for area in seat.areas],
            }
        for attr in seat.attributes:
            seat_datum[attr.name] = attr.value
        seats_data[seat.l0_id] = seat_datum

    return {
        'areas': dict(
            (area.id, { 'id': area.id, 'name': area.name }) \
            for area in venue.areas
            ),
        'seats': seats_data
        }
