# coding: utf-8

import csv
from datetime import datetime
from urllib2 import urlopen

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response
from sqlalchemy import and_, distinct
from sqlalchemy.sql import exists, join, func
from sqlalchemy.orm import joinedload, noload, aliased

from ticketing.models import DBSession
from ticketing.core.models import Site, Venue, VenueArea, Seat, SeatAttribute, SeatStatus, SeatAdjacencySet, SeatAdjacency, Seat_SeatAdjacency, Stock, StockStatus, StockHolder, StockType, ProductItem, Performance, Event
from ticketing.venues.export import SeatCSV
from ticketing.fanstatic import with_bootstrap

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
    venue = Venue.get(venue_id)
    if venue is None:
        return HTTPNotFound("Venue id #%d not found" % venue_id)

    _necessary_params = request.params.get(u'n', None)
    necessary_params = set() if _necessary_params is None else set(_necessary_params.split(u'|'))
    _filter_params = request.params.get(u'f', None)
    filter_params = set() if _filter_params is None else set(_filter_params.split(u'|'))
    loaded_at = request.params.get(u'loaded_at', None)
    if loaded_at:
        loaded_at = datetime.fromtimestamp(float(loaded_at))

    retval = {}

    if u'areas' in necessary_params:
        retval[u'areas'] = dict(
            (area.id, { 'id': area.id, 'name': area.name })\
            for area in venue.areas
            )

    if u'adjacencies' in necessary_params:
        query = DBSession.query(SeatAdjacencySet).options(joinedload("adjacencies"), joinedload('adjacencies.seats'))
        query = query.filter(SeatAdjacencySet.venue==venue)
        retval[u'adjacencies'] = [
            dict(
                count=seat_adjacency_set.seat_count,
                set=[
                    [seat.l0_id for seat in seat_adjacency.seats]\
                    for seat_adjacency in seat_adjacency_set.adjacencies\
                    ]
                )\
            for seat_adjacency_set in query
            ]

    if u'seats' in necessary_params:
        seats_data = {}
        query = DBSession.query(Seat).options(joinedload('attributes_'), joinedload('areas'), joinedload('status_')).filter_by(venue=venue)
        if u'sale_only' in filter_params:
            query = query.filter(exists().where(and_(ProductItem.performance_id==venue.performance_id, ProductItem.stock_id==Seat.stock_id)))
        if loaded_at:
            query = query.join(SeatStatus).filter(SeatStatus.updated_at>loaded_at)
        for seat in query:
            seat_datum = {
                'id': seat.l0_id,
                'name': seat.name,
                'seat_no': seat.seat_no,
                'stock_id': seat.stock_id,
                'status': seat.status,
                'areas': [area.id for area in seat.areas],
                }
            for attr in seat.attributes:
                seat_datum[attr] = seat[attr]
            seats_data[seat.l0_id] = seat_datum
        retval[u'seats'] = seats_data

    if u'stocks' in necessary_params:
        query = DBSession.query(Stock).options(joinedload('stock_status')).filter_by(performance=venue.performance)
        if u'sale_only' in filter_params:
            query = query.filter(exists().where(and_(ProductItem.performance_id==venue.performance_id, ProductItem.stock_id==Seat.stock_id)))
        if loaded_at:
            query = query.join(StockStatus).filter(StockStatus.updated_at>loaded_at)
        retval[u'stocks'] = [
            dict(
                id=stock.id,
                assigned=stock.quantity,
                stock_type_id=stock.stock_type_id,
                stock_holder_id=stock.stock_holder_id,
                available=stock.stock_status.quantity)\
            for stock in query
            ]

    if u'stock_types' in necessary_params:
        query = DBSession.query(StockType).filter_by(event=venue.performance.event).order_by(StockType.display_order)
        if loaded_at:
            query = query.filter(StockType.updated_at>loaded_at)
        retval[u'stock_types'] = [
            dict(
                id=stock_type.id,
                name=stock_type.name,
                is_seat=stock_type.is_seat,
                quantity_only=stock_type.quantity_only,
                style=stock_type.style)\
            for stock_type in query
            ]

    if u'stock_holders' in necessary_params:
        query = DBSession.query(StockHolder).filter_by(event=venue.performance.event)
        if loaded_at:
            query = query.filter(StockHolder.updated_at>loaded_at)
        retval[u'stock_holders'] = [
            dict(
                id=stock_holder.id,
                name=stock_holder.name,
                style=stock_holder.style)\
            for stock_holder in query
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

@view_config(route_name='venues.index', renderer='ticketing:templates/venues/index.html', decorator=with_bootstrap, permission='event_editor')
def index(request):
    sort = request.GET.get('sort', 'Venue.site_id')
    direction = request.GET.get('direction', 'asc')
    if direction not in ['asc', 'desc']:
        direction = 'asc'

    query = DBSession.query(Venue, func.count(Seat.id))
    query = query.outerjoin(Performance).filter(Performance.deleted_at==None)
    query = query.outerjoin(Event).filter(Event.deleted_at==None)
    query = query.filter_by(organization_id=request.context.user.organization_id)
    query = query.outerjoin(Seat)
    query = query.group_by(Venue.id)
    query = query.order_by(sort + ' ' + direction)

    class VenueCount:
        def __init__(self, venue, count):
            self.venue = venue
            self.count = count

    items = []
    for venue, count in query:
        items.append(VenueCount(venue, count))

    return {
        'items': items
    }

@view_config(route_name="api.get_frontend", request_method="GET", permission='event_viewer')
def frontend_drawing(request):
    venue_id = int(request.matchdict.get('venue_id', 0))
    venue = Venue.get(venue_id, organization_id=request.context.user.organization_id)
    part = request.matchdict.get('part')
    return Response(body=venue.site.get_drawing(part).stream().read(), content_type='text/xml; charset=utf-8')

# FIXME: add permission limitation
@view_config(route_name='venues.show', renderer='ticketing:templates/venues/show.html', decorator=with_bootstrap)
def show(request):
    venue_id = int(request.matchdict.get('venue_id', 0))
    venue = Venue.get(venue_id, organization_id=request.context.user.organization_id)
    site = Site.get(venue.site_id)
    root = None
    if site._metadata != None:
        for page, info in site._metadata.get('pages').items():
            if info.get('root'):
                root = page

    class SeatInfo:
        def __init__(self, seat, venuearea, attr, status):
            self.seat = seat
            self.venuearea = venuearea
            self.row = attr
            self.status = status

    seats = DBSession.query(Seat, VenueArea, SeatAttribute, SeatStatus)\
        .filter_by(venue_id=venue_id)\
        .join(Seat.areas)\
        .join(SeatAttribute).filter_by(name="row")\
        .join(SeatStatus)
    items = []
    for seat, venuearea, attr, status in seats:
        items.append(SeatInfo(seat, venuearea, attr, status))
    
    class SeatAdjacencyInfo:
        def __init__(self, adj, count):
            self.adj = adj
            self.count = count

    _adjs = DBSession\
        .query(SeatAdjacencySet, func.count(distinct(Seat.id)))\
        .filter_by(venue_id=venue.id)\
        .outerjoin(SeatAdjacencySet.adjacencies)\
        .join(Seat_SeatAdjacency)\
        .join(Seat, Seat_SeatAdjacency.seat_id==Seat.id)\
        .order_by('seat_count')\
        .group_by(SeatAdjacencySet.id)\
        .all()
    adjs = []
    for adj, count in _adjs:
        adjs.append(SeatAdjacencyInfo(adj, count))

    return {
        'venue': venue,
        'site': site,
        'root': root,
        'items': items,
        'adjs': adjs,
    }
