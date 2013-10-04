# coding: utf-8

import os
import csv
from datetime import datetime
from urllib2 import urlopen
import re
import logging
from urlparse import urlparse

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.response import Response
from pyramid.url import route_path
from sqlalchemy import and_, distinct
from sqlalchemy.sql import exists, join, func, or_, not_
from sqlalchemy.sql.expression import asc, desc
from sqlalchemy.orm import joinedload, noload, aliased, undefer

from altair.pyramid_assets import get_resolver

from altair.app.ticketing.models import DBSession
from altair.app.ticketing.models import merge_session_with_post, record_to_multidict
from altair.app.ticketing.core.models import Site, Venue, VenueArea, Seat, SeatAttribute, SeatStatus, SalesSegment, SeatAdjacencySet, Seat_SeatAdjacency, Stock, StockStatus, StockHolder, StockType, ProductItem, Product, Performance, Event, SeatIndexType, SeatIndex
from altair.app.ticketing.venues.forms import SiteForm
from altair.app.ticketing.venues.export import SeatCSV
from altair.app.ticketing.venues.api import get_venue_site_adapter
from altair.app.ticketing.fanstatic import with_bootstrap

logger = logging.getLogger(__name__)

@view_config(route_name="api.get_site_drawing", request_method="GET", permission='event_viewer')
def get_site_drawing(context, request):
    site_id = long(request.matchdict.get('site_id'))
    site = Site.query \
        .join(Venue.site) \
        .filter_by(id=site_id) \
        .filter(Venue.organization_id==context.user.organization_id) \
        .distinct().one()
    drawing_url = get_venue_site_adapter(request, site).drawing_url
    if drawing_url is None:
        return Response(status_code=404)
    else:
        return Response(
            status_code=200,
            content_type='image/svg',
            body_file=get_resolver(request.registry).resolve(drawing_url).stream()
            )

@view_config(route_name="api.get_seats", request_method="GET", renderer='json', permission='event_viewer')
def get_seats(request):
    venue = request.context.venue

    _necessary_params = request.params.get(u'n', None)
    necessary_params = set() if _necessary_params is None else set(_necessary_params.split(u'|'))
    _filter_params = request.params.get(u'f', None)
    filter_params = set() if _filter_params is None else set(_filter_params.split(u'|'))
    sales_segment_id = request.params.get(u'sales_segment_id', None)
    loaded_at = request.params.get(u'loaded_at', None)
    sale_only = (u'sale_only' in filter_params)
    if loaded_at:
        loaded_at = datetime.fromtimestamp(float(loaded_at))

    retval = {}

    if u'areas' in necessary_params:
        retval[u'areas'] = dict(
            (area.id, { 'id': area.id, 'name': area.name })\
            for area in venue.areas
            )

    if u'seats' in necessary_params:
        seats_data = {}
        query = DBSession.query(Seat).join(SeatStatus).filter(Seat.venue==venue)
        query = query.with_entities(Seat.l0_id, Seat.name, Seat.seat_no, Seat.stock_id, SeatStatus.status)
        # 差分取得のときは販売可能かどうかに関わらず取得する
        if loaded_at:
            query = query.filter(or_(Seat.updated_at>loaded_at, SeatStatus.updated_at>loaded_at))
        elif sale_only:
            if sales_segment_id:
                query = query.join(ProductItem, and_(ProductItem.performance_id==venue.performance_id, ProductItem.stock_id==Seat.stock_id))
                query = query.join(Product).join(SalesSegment).filter(SalesSegment.id==sales_segment_id).distinct()
            else:
                query = query.filter(exists().where(and_(ProductItem.performance_id==venue.performance_id, ProductItem.stock_id==Seat.stock_id)))
        for l0_id, name, seat_no, stock_id, status in query:
            seats_data[l0_id] = {
                'id': l0_id,
                'name': name,
                'seat_no': seat_no,
                'stock_id': stock_id,
                'status': status,
            }
        retval[u'seats'] = seats_data

    if u'stocks' in necessary_params:
        stocks_data = []
        count_column = ProductItem.id if not loaded_at and sale_only else Stock.id
        query = DBSession.query(Stock, func.count(count_column)).options(joinedload('stock_status')).filter_by(performance=venue.performance)
        # 差分取得のときは販売可能かどうかに関わらず取得する
        if loaded_at:
            query = query.join(StockStatus).filter(StockStatus.updated_at>loaded_at)
        elif sale_only:
            query = query.join(ProductItem, and_(ProductItem.performance_id==venue.performance_id, ProductItem.stock_id==Stock.id))
            if sales_segment_id:
                query = query.join(Product).join(SalesSegment).filter(SalesSegment.id==sales_segment_id)
            query = query.having(func.count(ProductItem.id)>0)
        query = query.group_by(Stock.id)
        for (stock, count) in query:
            if sale_only:
                assignable = bool(count > 0)
            else:
                assignable = bool(not stock.locked_at)
            stocks_data.append(dict(
                id=stock.id,
                assigned=stock.quantity,
                stock_type_id=stock.stock_type_id,
                stock_holder_id=stock.stock_holder_id,
                available=stock.stock_status.quantity,
                assignable=assignable
            ))
        retval[u'stocks'] = stocks_data

    if u'stock_types' in necessary_params:
        query = DBSession.query(StockType).filter_by(event=venue.performance.event).order_by(StockType.display_order)
        if sales_segment_id:
            query = query.join(Stock, and_(Stock.performance_id==venue.performance_id, Stock.stock_type_id==StockType.id))
            query = query.join(ProductItem, and_(ProductItem.performance_id==venue.performance_id, ProductItem.stock_id==Stock.id))
            query = query.join(Product).join(SalesSegment).filter(SalesSegment.id==sales_segment_id).distinct()
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
        query = DBSession.query(StockHolder).filter_by(event=venue.performance.event).options(undefer(StockHolder.style))
        if sales_segment_id:
            query = query.join(Stock, and_(Stock.performance_id==venue.performance_id, Stock.stock_holder_id==StockHolder.id))
            query = query.join(ProductItem, and_(ProductItem.performance_id==venue.performance_id, ProductItem.stock_id==Stock.id))
            query = query.join(Product).join(SalesSegment).filter(SalesSegment.id==sales_segment_id).distinct()
        if loaded_at:
            query = query.filter(StockHolder.updated_at>loaded_at)
        retval[u'stock_holders'] = [
            dict(
                id=stock_holder.id,
                name=stock_holder.name,
                style=stock_holder.style)\
            for stock_holder in query
            ]

    logger.debug('seats=%s, stocks=%s, stock_types=%s, stock_holders=%s'
                 % (len(retval[u'seats']), len(retval[u'stocks']), len(retval[u'stock_types']), len(retval[u'stock_holders'])))
    return retval

@view_config(route_name='seats.download', permission='event_editor')
def download(request):
    venue = request.context.venue

    headers = [
        ('Content-Type', 'application/octet-stream; charset=cp932'),
        ('Content-Disposition', 'attachment; filename=seats_{date}.csv'.format(date=datetime.now().strftime('%Y%m%d%H%M%S')))
    ]
    response = Response(headers=headers)

    seats_csv = SeatCSV(venue.seats)

    writer = csv.DictWriter(response, seats_csv.header, delimiter=',', quoting=csv.QUOTE_ALL)
    writer.writeheader()
    writer.writerows(seats_csv.rows)

    return response

@view_config(route_name='venues.index', renderer='altair.app.ticketing:templates/venues/index.html',
             decorator=with_bootstrap, permission='event_editor')
def index(request):
    query = DBSession.query(Venue, Site, Performance)
    query = query.filter(Venue.organization_id==request.context.user.organization_id)
    query = query.join((Site, and_(Site.id==Venue.site_id, Site.deleted_at==None)))
    query = query.outerjoin((Performance, and_(Performance.id==Venue.performance_id, Performance.deleted_at==None)))
    query = query.options(undefer(Site.created_at), undefer(Performance.created_at))
    query = query.group_by(Venue.id)
    query = query.order_by(asc(Venue.site_id), asc(-Venue.performance_id))

    items = []
    for venue, site, performance in query:
        items.append(dict(venue=venue, site=site, performance=performance))

    return dict(items=items)

@view_config(route_name="api.get_frontend", request_method="GET", permission='event_viewer')
def frontend_drawing(request):
    venue = request.context.venue
    part = request.matchdict.get('part')
    drawing = get_venue_site_adapter(request, venue.site).get_frontend_drawing(part)
    if drawing is None:
        return HTTPNotFound()
    content_encoding = None
    if re.match('^.+\.(svgz|gz)$', part):
        content_encoding = 'gzip'
    return Response(body=drawing.stream().read(), content_type='text/xml; charset=utf-8', content_encoding=content_encoding)

@view_config(route_name='venues.show', renderer='altair.app.ticketing:templates/venues/show.html',
             decorator=with_bootstrap, permission='event_editor')
def show(request):
    venue = request.context.venue
    venue_id = venue.id

    site = venue.site
    drawing = get_venue_site_adapter(request, site)
    root = None
    pages = drawing.get_frontend_pages()
    if pages:
        for page, info in pages.items():
            if info.get('root'):
                root = page

    types = SeatIndexType.filter_by(venue_id=venue_id).all()
    type_id = types[0].id if 0<len(types) else None
    if 'index_type' in request.GET:
        type_id = 2
        for type in types:
            if request.GET.get('index_type') == str(type.id):
                type_id = type.id

    class SeatInfo:
        def __init__(self, seat, venuearea, attr, status, index):
            self.seat = seat
            self.venuearea = venuearea
            self.row = attr
            self.status = status
            self.index = index

    seats = DBSession.query(Seat, VenueArea, SeatAttribute, SeatStatus, SeatIndex)\
        .filter_by(venue_id=venue_id)\
        .outerjoin(VenueArea, Seat.areas)\
        .outerjoin(SeatAttribute, and_(SeatAttribute.seat_id==Seat.id, SeatAttribute.name=="row"))\
        .outerjoin(SeatStatus, SeatStatus.seat_id==Seat.id)
    if type_id is not None:
        seats = seats.outerjoin(SeatIndex, and_(SeatIndex.seat_id==Seat.id, SeatIndex.seat_index_type_id==type_id))
    items = []
    for seat, venuearea, attr, status, type in seats:
        items.append(SeatInfo(seat, venuearea, attr, status, type))
    
    class SeatAdjacencyInfo:
        def __init__(self, adj, count):
            self.adj = adj
            self.count = count

    _adjs = DBSession\
        .query(SeatAdjacencySet, func.count(distinct(Seat.id)))\
        .filter_by(site_id=venue.site_id)\
        .outerjoin(SeatAdjacencySet.adjacencies)\
        .join(Seat_SeatAdjacency)\
        .join(Seat, Seat_SeatAdjacency.l0_id==Seat.l0_id)\
        .filter(Seat.venue_id==venue_id)\
        .order_by('seat_count')\
        .group_by(SeatAdjacencySet.id)\
        .all()
    adjs = []
    for adj, count in _adjs:
        adjs.append(SeatAdjacencyInfo(adj, count))

    return {
        'venue': venue,
        'site': site,
        'drawing': drawing,
        'root': root,
        'type_id': type_id,
        'types': types,
        'pages': pages,
        'items': items,
        'adjs': adjs,
    }

@view_config(route_name='venues.checker', renderer='altair.app.ticketing:templates/venues/checker.html',
             decorator=with_bootstrap, permission='event_editor')
def show_checker(context, request):
    venue = request.context.venue
    return {
        'venue': venue,
        'site': venue.site,
        'drawing': get_venue_site_adapter(request, venue.site),
    }

@view_config(route_name='venues.new', request_method='GET', renderer='altair.app.ticketing:templates/venues/edit.html',
             decorator=with_bootstrap, permission='event_editor')
def new_get(request):
    f = SiteForm()
    site = Site()

    site_id = int(request.matchdict.get('site_id', 0))
    if site_id:
        site = Site.get(site_id, organization_id=request.context.user.organization_id)
        if site is None:
            return HTTPNotFound('site id %d is not found' % site_id)

    site = record_to_multidict(site)
    if 'id' in site: site.pop('id')
    f.process(site)

    return {
        'form':f,
        'route_name': u'登録',
        'route_path': request.path,
    }

@view_config(route_name='venues.new', request_method='POST', renderer='altair.app.ticketing:templates/venues/edit.html',
             decorator=with_bootstrap, permission='event_editor')
def new_post(request):
    f = SiteForm(request.POST)

    if f.validate():
        site = merge_session_with_post(Site(), f.data)
        site.save()

        venue = merge_session_with_post(Venue(site_id=site.id, organization_id=request.context.user.organization_id), f.data)
        venue.save()

        request.session.flash(u'会場を登録しました')
        return HTTPFound(location=route_path('venues.show', request, venue_id=venue.id))
    else:
        return {
            'form':f,
            'route_name': u'登録',
            'route_path': request.path,
        }

@view_config(route_name='venues.edit', request_method='GET', renderer='altair.app.ticketing:templates/venues/edit.html',
             decorator=with_bootstrap, permission='event_editor')
def edit_get(request):
    venue = request.context.venue
    if venue.site is None:
        return HTTPNotFound('site id %d is not found' % venue.site_id)

    f = SiteForm()
    f.process(record_to_multidict(venue.site))
    f.name.process_data(venue.name)
    f.sub_name.process_data(venue.sub_name)

    return {
        'form':f,
        'venue':venue,
        'site':venue.site,
        'drawing': get_venue_site_adapter(request, venue.site),
        'route_name': u'編集',
        'route_path': request.path,
    }

@view_config(route_name='venues.edit', request_method='POST', renderer='altair.app.ticketing:templates/venues/edit.html',
             decorator=with_bootstrap, permission='event_editor')
def edit_post(request):
    venue = request.context.venue

    f = SiteForm(request.POST)
    if f.validate():
        venue = merge_session_with_post(venue, f.data)
        venue.save()

        site = merge_session_with_post(venue.site, f.data)
        site.save()

        request.session.flash(u'会場を保存しました')
        return HTTPFound(location=route_path('venues.show', request, venue_id=venue.id))
    else:
        return {
            'form':f,
            'venue':venue,
            'site':venue.site,
            'drawing': get_venue_site_adapter(request, venue.site),
            'route_name': u'編集',
            'route_path': request.path,
        }
