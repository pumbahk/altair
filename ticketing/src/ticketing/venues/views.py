# coding: utf-8

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response
from sqlalchemy.orm import joinedload, noload
from urllib2 import urlopen

from ticketing.models import DBSession
from .models import Venue, Seat, SeatAttribute, VenueArea, SeatAdjacency, SeatAdjacencySet
from ticketing.products.models import Stock, StockHolder, StockType

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
    for seat in DBSession.query(Seat).options(joinedload('attributes'), joinedload('areas'), joinedload('stock')).filter_by(venue=venue):
        seat_datum = {
            'id': seat.l0_id,
            'stock_type_id': seat.stock and seat.stock.stock_type_id,
            'stock_holder_id': seat.stock and seat.stock.stock_holder and seat.stock.stock_holder.id,
            'status': seat.status,
            'areas': [area.id for area in seat.areas],
            }
        for attr in seat.attributes:
            seat_datum[attr.name] = attr.value
        seats_data[seat.l0_id] = seat_datum

    seat_adjacencies_data = {}
    for seat_adjacency_set in DBSession.query(SeatAdjacencySet).options(joinedload("adjacencies")).filter_by(venue=venue):
        for seat_adjacency in seat_adjacency_set.adjacencies:
            seat_adjacencies_data[seat_adjacency_set.seat_count] = [
                [seat.l0_id for seat in seat_adjacency.seats] \
                for seat_adjacency in seat_adjacency_set.adjacencies \
                ]

    stock_types_data = {}
    for stock_type in DBSession.query(StockType).filter_by(event=venue.performance.event):
        stock_types_data[stock_type.id] = dict(
            name=stock_type.name,
            style=stock_type.style)

    stock_holders_data = {}
    for stock_holder in DBSession.query(StockHolder).filter_by(performance=venue.performance):
        stock_holders_data[stock_holder.id] = dict(
            name=stock_holder.name,
            style=stock_holder.style)

    return {
        'areas': dict(
            (area.id, { 'id': area.id, 'name': area.name }) \
            for area in venue.areas \
            ),
        'seats': seats_data,
        'seat_adjacencies': seat_adjacencies_data,
        'stock_types': stock_types_data,
        'stock_holders': stock_holders_data
        }

