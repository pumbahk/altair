# coding: utf-8

import csv
from datetime import datetime
from urllib2 import urlopen

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response
from sqlalchemy import and_
from sqlalchemy.sql import exists
from sqlalchemy.orm import joinedload, noload

from ticketing.models import DBSession
from ticketing.core.models import Venue, Seat, SeatAdjacencySet, Stock, StockHolder, StockType, ProductItem
from ticketing.venues.export import SeatCSV

@view_config(route_name="api.get_drawing", request_method="GET", permission='event_viewer')
def get_drawing(request):
    venue_id = int(request.matchdict.get('venue_id', 0))
    venue = Venue.get(venue_id)
    if venue is None:
        return HTTPNotFound("Venue id #%d not found" % venue_id)

    return Response(app_iter=urlopen(venue.site.drawing_url), content_type='text/xml; charset=utf-8')

@view_config(route_name="api.get_seats", request_method="GET", renderer='json', permission='event_viewer')
def get_seats(request):
    venue_id = int(request.matchdict.get('venue_id', 0))
    _necessary_params = request.params.get(u'n', None)
    necessary_params = set() if _necessary_params is None else set(_necessary_params.split(u'|'))
    filter_params = request.params.get(u'f', set())

    venue = Venue.get(venue_id)
    if venue is None:
        return HTTPNotFound("Venue id #%d not found" % venue_id)

    retval = {}

    if u'areas' in necessary_params:
        retval[u'areas'] = dict(
            (area.id, { 'id': area.id, 'name': area.name }) \
            for area in venue.areas \
            )

    if u'seats' in necessary_params:
        seats_data = {}
        seats_query = DBSession.query(Seat).options(joinedload('attributes_'), joinedload('areas'), joinedload('status_')).filter_by(venue=venue)
        # 販売している座席のみの指定がある場合
        if u'sale_only' in filter_params:
            seats_query = seats_query.filter(exists().where(and_(ProductItem.performance_id==venue.performance_id, ProductItem.stock_id==Seat.stock_id)))

        for seat in seats_query:
            seat_datum = {
                'id': seat.l0_id,
                'seat_no': seat.seat_no,
                'stock_id': seat.stock_id,
                'status': seat.status,
                'areas': [area.id for area in seat.areas],
                }
            for attr in seat.attributes:
                seat_datum[attr] = seat[attr]
            seats_data[seat.l0_id] = seat_datum
        retval[u'seats'] = seats_data

    if u'adjacencies' in necessary_params:
        retval[u'adjacencies'] = [
            dict(
                count=seat_adjacency_set.seat_count,
                set=[
                    [seat.l0_id for seat in seat_adjacency.seats] \
                    for seat_adjacency in seat_adjacency_set.adjacencies \
                    ]
                ) \
            for seat_adjacency_set in DBSession.query(SeatAdjacencySet).options(joinedload("adjacencies"), joinedload('adjacencies.seats')).filter(SeatAdjacencySet.venue==venue)
            ]

    # 販売している座席のみの指定がある場合
    stocks_query = DBSession.query(Stock).options(joinedload('stock_status')).filter_by(performance=venue.performance)
    if u'sale_only' in filter_params:
        stocks_query = stocks_query.filter(exists().where(and_(ProductItem.performance_id==venue.performance_id, ProductItem.stock_id==Seat.stock_id)))
    retval[u'stocks'] = [
        dict(
            id=stock.id,
            assigned=stock.quantity,
            stock_type_id=stock.stock_type_id,
            stock_holder_id=stock.stock_holder_id,
            available=stock.stock_status.quantity)\
        for stock in stocks_query
        ]

    retval[u'stock_types'] = [
        dict(
            id=stock_type.id,
            name=stock_type.name,
            is_seat=stock_type.is_seat,
            quantity_only=stock_type.quantity_only,
            style=stock_type.style) \
        for stock_type in DBSession.query(StockType).filter_by(event=venue.performance.event).order_by(StockType.display_order)
        ]

    retval[u'stock_holders'] = [
        dict(
            id=stock_holder.id,
            name=stock_holder.name,
            style=stock_holder.style) \
        for stock_holder in DBSession.query(StockHolder).filter_by(event=venue.performance.event)
        ]

    return retval

@view_config(route_name='seats.download', permission='event_editor')
def download(request):
    venue_id = int(request.matchdict.get('venue_id', 0))
    venue = Venue.get(venue_id)
    if venue is None:
        return HTTPNotFound("Venue id #%d not found" % venue_id)

    seats = Seat.filter_by(venue_id=venue_id).all()

    headers = [
        ('Content-Type', 'application/octet-stream; charset=cp932'),
        ('Content-Disposition', 'attachment; filename=seats_{date}.csv'.format(date=datetime.now().strftime('%Y%m%d%H%M%S')))
    ]
    response = Response(headers=headers)

    seats_csv = SeatCSV(seats)

    writer = csv.DictWriter(response, seats_csv.header, delimiter=',', quoting=csv.QUOTE_ALL)
    writer.writeheader()
    writer.writerows(seats_csv.rows)

    return response
