# coding: utf-8

import os
import csv
from lxml import etree
from datetime import datetime
from urllib2 import urlopen
import re
import logging
from urlparse import urlparse
from zope.interface import implementer
import webhelpers.paginate as paginate

from pyramid.view import view_defaults, view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.response import Response
from pyramid.url import route_path
from pyramid.settings import asbool
from pyramid.security import has_permission, ACLAllowed
from sqlalchemy import and_, distinct
from sqlalchemy.sql import exists, join, func, or_, not_
from sqlalchemy.sql.expression import asc, desc
from sqlalchemy.orm import joinedload, noload, aliased, undefer
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from altair.sqlahelper import get_db_session

from altair.pyramid_assets import get_resolver
from altair.pyramid_assets.data import DataSchemeAssetDescriptor
from altair.pyramid_boto.s3.assets import IS3KeyProvider
from altair.sqlahelper import get_db_session
from altair.app.ticketing.orders.models import (
    OrderedProductItem,
    OrderedProduct,
    Order,
    )

from altair.app.ticketing.views import BaseView
from altair.app.ticketing.core.utils import PageURL_WebOb_Ex
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.models import merge_session_with_post, record_to_multidict
from altair.app.ticketing.core.models import (
    SiteProfile, Site, Venue, VenueArea, VenueArea_group_l0_id, Seat, SeatAttribute, SeatStatus, SeatStatusEnum, SalesSegment, SalesSegmentSetting,
    SeatAdjacencySet, SeatAdjacency, Seat_SeatAdjacency, Stock, StockStatus, StockHolder, StockType,
    ProductItem, Product, Performance, Event, SeatIndexType, SeatIndex, SeatGroup
)
from altair.app.ticketing.venues.forms import SiteForm, VenueSearchForm
from altair.app.ticketing.venues.export import SeatCSV
from altair.app.ticketing.venues.api import get_venue_site_adapter
from altair.app.ticketing.fanstatic import with_bootstrap
from .utils import is_drawing_compressed, get_s3_url
from .interfaces import IVenueSiteDrawingHandler
from .api import set_visible_venue, set_invisible_venue
from . import VISIBLE_VENUES_SESSION_KEY

logger = logging.getLogger(__name__)


@implementer(IVenueSiteDrawingHandler)
class VenueSiteDrawingHandler(object):
    def __init__(self, config):
        self.use_x_accel_redirect = asbool(config.registry.settings.get('altair.site_data.indirect_serving.use_x_accel_redirect', 'false'))

    def __call__(self, context, request):
        site_id = long(request.matchdict.get('site_id'))
        part = request.params.get('part', 'root.svg')
        site = Site.query \
            .join(Venue.site) \
            .filter_by(id=site_id) \
            .filter(Venue.organization_id==context.user.organization_id) \
            .distinct().one()
        drawing = get_venue_site_adapter(request, site).get_backend_drawing(part)
        logger.debug(u'drawing=%r' % drawing)
        if drawing is None:
            if site._drawing_url is not None:
                logger.debug(u'using site._drawing_url (=%s)' % site._drawing_url)
                drawing = get_resolver(request.registry).resolve(site._drawing_url)
            else:
                # ダミー会場図だった
                drawing = DataSchemeAssetDescriptor('<?xml version="1.0" ?><svg xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 0 1 1" width="1" height="1" />', 'image/svg+xml', [], None)

        if drawing is None:
            return Response(status_code=404)
        else:
            if IS3KeyProvider.providedBy(drawing) and self.use_x_accel_redirect:
                redirect_to = get_s3_url(drawing)
                return Response(
                    status_code=200,
                    headers={ 'X-Accel-Redirect': redirect_to }
                    )
            else:
                headers = {
                    'Cache-Control': 'max-age=3600 private', # hard-coded!
                    }
                resp = Response(
                    status_code=200,
                    content_type='image/svg+xml',
                    body_file=drawing.stream()
                    )
                resp.encode_content('gzip', lazy=True)
                return resp


@view_config(route_name="api.get_site_drawing", request_method="GET", permission='event_viewer')
def get_site_drawing(context, request):
    return request.registry.getUtility(IVenueSiteDrawingHandler)(context, request)

def lxml_result(child_element, message):
    result = etree.Element("result")
    child = etree.SubElement(result, child_element)
    child.text = message
    return result

def create_text_element(parent, name, text):
    e = etree.SubElement(parent, name)
    e.text = text

@view_config(route_name="api.seat_info", request_method="GET", renderer="lxml", permission="event_viewer")
def get_seat_info(context, request):
    slave_session = get_db_session(request, 'slave')
    x_result = etree.Element("result")

    venue = request.context.venue

    x_venue = etree.Element("venue")
    create_text_element(x_venue, "id", str(venue.id))
    create_text_element(x_venue, "name", venue.name)
    x_result.append(x_venue)

    row = aliased(SeatAttribute)
    floor = aliased(SeatAttribute)
    block = aliased(SeatAttribute)
    gate = aliased(SeatAttribute)
    seats = slave_session.query(Seat, VenueArea, row.value, floor.value, block.value, gate.value)\
        .filter_by(venue_id=venue.id)\
        .join(VenueArea, Seat.areas)\
        .outerjoin(row, and_(row.name=="row", row.seat_id==Seat.id))\
        .outerjoin(floor, and_(floor.name=="floor", floor.seat_id==Seat.id))\
        .outerjoin(block, and_(block.name=="block", block.seat_id==Seat.id))\
        .outerjoin(gate, and_(gate.name=="gate", gate.seat_id==Seat.id))

    x_seats = etree.Element("seats")
    x_result.append(x_seats)
    for seat, venuearea, sa_row, sa_floor, sa_block, sa_gate in seats:
        x_seat = etree.Element("seat")
        create_text_element(x_seat, "l0_id", seat.l0_id)
        create_text_element(x_seat, "group_l0_id", seat.group_l0_id)
        create_text_element(x_seat, "venue_area_name", venuearea.name)
        create_text_element(x_seat, "row_l0_id", seat.row_l0_id)
        create_text_element(x_seat, "seat_no", seat.seat_no)
        create_text_element(x_seat, "name", seat.name)
        create_text_element(x_seat, "sa_row", sa_row)
        if sa_floor is not None:
            create_text_element(x_seat, "sa_floor", sa_floor)
        if sa_block is not None:
            create_text_element(x_seat, "sa_block", sa_block)
        if sa_gate is not None:
            create_text_element(x_seat, "sa_gate", sa_gate)
        x_seats.append(x_seat)

    return x_result

@view_config(route_name="api.seat_info", request_method="POST", renderer="lxml", permission="event_editor")
def update_seat_info(context, request):
    venue = request.context.venue
    if venue.id != long(request.POST['venue']):
        return lxml_result("error", "wrong parameter")

    updated = 0

    name_by_gid = dict(zip(request.POST['group_l0_id'].split("\t"), request.POST['group_name'].split("\t")))

    l0_id_list = request.POST['l0_id'].split("\t")
    seat_no_list = request.POST['seat_no'].split("\t")
    name_list = request.POST['name'].split("\t")
    sa_row_list = request.POST['sa_row'].split("\t")
    sa_floor_list = request.POST['sa_floor'].split("\t")
    if 'sa_block' in request.POST:
        sa_block_list = request.POST['sa_block'].split("\t")
    else:
        sa_block_list = None
    sa_gate_list = request.POST['sa_gate'].split("\t")
    
    info_by_id = dict()
    for idx, l0_id in enumerate(l0_id_list):
        info_by_id[l0_id] = (seat_no_list[idx], name_list[idx], sa_row_list[idx], sa_floor_list[idx], sa_block_list[idx] if not (sa_block_list is None) else None, sa_gate_list[idx])

    areas = DBSession.query(VenueArea_group_l0_id, VenueArea)\
        .filter_by(venue_id=venue.id)\
        .join(VenueArea, VenueArea.id==VenueArea_group_l0_id.venue_area_id)

    for group, area in areas:
        if group.group_l0_id in name_by_gid:
            if area.name != name_by_gid[group.group_l0_id]:
                area.name = name_by_gid[group.group_l0_id]
                area.save()
                updated = updated + 1

    row = aliased(SeatAttribute)
    floor = aliased(SeatAttribute)
    block = aliased(SeatAttribute)
    gate = aliased(SeatAttribute)
    seats = DBSession.query(Seat, VenueArea, row.value, floor.value, block.value, gate.value)\
        .filter_by(venue_id=venue.id)\
        .join(VenueArea, Seat.areas)\
        .outerjoin(row, and_(row.name=="row", row.seat_id==Seat.id))\
        .outerjoin(floor, and_(floor.name=="floor", floor.seat_id==Seat.id))\
        .outerjoin(block, and_(block.name=="block", block.seat_id==Seat.id))\
        .outerjoin(gate, and_(gate.name=="gate", gate.seat_id==Seat.id))

    for seat, venuearea, _row, _floor, _block, _gate in seats:
        if seat.l0_id in info_by_id:
            if seat.seat_no != info_by_id[seat.l0_id][0] or seat.name != info_by_id[seat.l0_id][1]:
                seat.seat_no = info_by_id[seat.l0_id][0]
                seat.name = info_by_id[seat.l0_id][1]
                seat.save()
                updated = updated + 1
            if info_by_id[seat.l0_id][2] != _row:
                row = SeatAttribute.query.filter(and_(SeatAttribute.seat_id==seat.id, SeatAttribute.name=="row")).first()
                if row is not None:
                    row.value = info_by_id[seat.l0_id][2]
                    row.save()
                    updated = updated + 1
            if info_by_id[seat.l0_id][3] != _floor:
                floor = SeatAttribute.query.filter(and_(SeatAttribute.seat_id==seat.id, SeatAttribute.name=="floor")).first()
                if floor is not None:
                    floor.value = info_by_id[seat.l0_id][3]
                    floor.save()
                    updated = updated + 1
            if (not info_by_id[seat.l0_id][4] is None) and info_by_id[seat.l0_id][4] != _block:
                block = SeatAttribute.query.filter(and_(SeatAttribute.seat_id==seat.id, SeatAttribute.name=="block")).first()
                if block is not None:
                    block.value = info_by_id[seat.l0_id][4]
                    block.save()
                    updated = updated + 1
                elif info_by_id[seat.l0_id][4] != "":
                    # create new record
                    block = SeatAttribute()
                    block.seat_id = seat.id
                    block.name = "block"
                    block.value = info_by_id[seat.l0_id][4]
                    DBSession.add(block)
                    updated = updated + 1
            if info_by_id[seat.l0_id][5] != _gate:
                gate = SeatAttribute.query.filter(and_(SeatAttribute.seat_id==seat.id, SeatAttribute.name=="gate")).first()
                if gate is not None:
                    gate.value = info_by_id[seat.l0_id][5]
                    gate.save()
                    updated = updated + 1

    return lxml_result("success", "ok, %u records updated." % updated)

@view_config(route_name="api.seat_priority", request_method="GET", renderer="lxml", permission="event_viewer")
def get_seat_priority(context, request):
    x_result = etree.Element("result")
    slave_session = get_db_session(request, 'slave')

    venue = request.context.venue

    x_venue = etree.Element("venue")
    create_text_element(x_venue, "id", str(venue.id))
    create_text_element(x_venue, "name", venue.name)
    x_result.append(x_venue)

    seats = slave_session.query(Seat, SeatIndex.index)\
        .filter_by(venue_id=venue.id)\
        .join(SeatIndex.seat)

    x_seats = etree.Element("seats")
    x_result.append(x_seats)
    for seat, index in seats:
        x_seat = etree.Element("seat")
        create_text_element(x_seat, "l0_id", seat.l0_id)
        create_text_element(x_seat, "index", str(index))
        create_text_element(x_seat, "name", seat.name)
        x_seats.append(x_seat)

    return x_result

@view_config(route_name="api.seat_priority", request_method="POST", renderer="lxml", permission="event_editor")
def update_seat_priority(context, request):
    venue = request.context.venue
    if venue.id != long(request.POST['venue']):
        return lxml_result("error", "wrong parameter")

    updated = 0

    index_by_id = dict(zip(request.POST['l0_id'].split("\t"), request.POST['index'].split("\t")))

    seats = DBSession.query(Seat, SeatIndex)\
        .filter_by(venue_id=venue.id)\
        .join(SeatIndex.seat)
    
    for seat, index in seats:
        if seat.l0_id in index_by_id:
            if index.index != long(index_by_id[seat.l0_id]):
                index.index = long(index_by_id[seat.l0_id])
                index.save()
                updated = updated + 1
    
    return lxml_result("success", "ok, %u records updated." % updated)

@view_config(route_name="api.group", request_method="GET", renderer="lxml", permission="event_viewer")
def get_seat_group(context, request):
    x_result = etree.Element("result")

    venue = request.context.venue
    site = venue.site

    if venue.performance != None:
        create_text_element(x_result, "error", u"公演に紐づいていない初期VenueのIDを指定してください")
        return x_result

    x_venue = etree.Element("venue")
    x_result.append(x_venue)
    create_text_element(x_venue, "id", str(venue.id))
    create_text_element(x_venue, "name", venue.name)

    slave_session = get_db_session(request, 'slave')
    seats = slave_session.query(Seat, SeatIndex.index)\
        .filter_by(venue_id=venue.id)\
        .join(SeatIndex.seat)

    x_seats = etree.Element("seats")
    x_result.append(x_seats)
    for seat, index in seats:
        x_seat = etree.Element("seat")
        x_seats.append(x_seat)
        create_text_element(x_seat, "l0_id", seat.l0_id)
        create_text_element(x_seat, "row_l0_id", seat.row_l0_id)
        create_text_element(x_seat, "name", seat.name)

    groups = slave_session.query(SeatGroup)\
        .filter_by(site_id=site.id)\
        .order_by(SeatGroup.name, SeatGroup.l0_id)

    x_groups = etree.Element("groups")
    x_result.append(x_groups)
    x_group_name = ""
    for group in groups:
        if x_group_name != group.name:
            x_group_name = group.name
            x_group = etree.Element("group")
            x_groups.append(x_group)
            create_text_element(x_group, "name", group.name)
        create_text_element(x_group, "l0_id", group.l0_id)

    return x_result

@view_config(route_name="api.group", request_method="POST", renderer="lxml", permission="event_editor")
def update_seat_group(context, request):
    venue = request.context.venue
    if venue.id != long(request.POST['venue']):
        return lxml_result("error", "wrong parameter")
    if venue.performance != None:
        return lxml_result("error", "not base venue")
    site = venue.site

    # リクエスト
    req_by_l0_id = dict()
    names = request.POST.getall('name[]')
    for i, l0_id_list in enumerate(request.POST.getall('l0_id[]')):
        for l0_id in l0_id_list.split("\t"):
            req_by_l0_id[l0_id] = names[i]

    # DB登録済み
    group_by_l0_id = dict()
    groups = DBSession.query(SeatGroup)\
        .filter_by(site_id=site.id)\
        .order_by(SeatGroup.name, SeatGroup.l0_id)
    for group in groups:
        group_by_l0_id[group.l0_id] = group
    
    # 処理開始
    for l0_id in group_by_l0_id:
        if l0_id in req_by_l0_id:
            if group_by_l0_id[l0_id].name != req_by_l0_id[l0_id]:
                # UPDATE
                group_by_l0_id[l0_id].name = req_by_l0_id[l0_id]
                group_by_l0_id[l0_id].save()
            del req_by_l0_id[l0_id]
        else:
            # DELETE
            DBSession.delete(group_by_l0_id[l0_id])

    for l0_id in req_by_l0_id:
        # INSERT
        new_seat_group = SeatGroup()
        new_seat_group.name = req_by_l0_id[l0_id]
        new_seat_group.site_id = site.id
        new_seat_group.l0_id = l0_id
        DBSession.add(new_seat_group)

    return lxml_result("success", "ok")

@view_config(route_name="api.get_seats", request_method="GET", renderer='json', permission='event_viewer')
def get_seats(request):
    slave_session = get_db_session(request, 'slave')
    venue = request.context.venue

    _necessary_params = request.params.get(u'n', None)
    necessary_params = set() if _necessary_params is None else set(_necessary_params.split(u'|'))
    _filter_params = request.params.get(u'f', None)
    filter_params = set() if _filter_params is None else set(_filter_params.split(u'|'))
    sales_segment_id = request.params.get(u'sales_segment_id', None)
    loaded_at = request.params.get(u'loaded_at', None)
    load_all_seat = request.params.get(u'load_all_seat', None)
    sale_only = (u'sale_only' in filter_params)
    if loaded_at:
        loaded_at = datetime.fromtimestamp(float(loaded_at))
    permit_operator = isinstance(has_permission('event_editor', request.context, request), ACLAllowed)

    retval = {}

    if u'areas' in necessary_params:
        retval[u'areas'] = dict(
            (area.id, { 'id': area.id, 'name': area.name })\
            for area in venue.areas
            )

    if u'seats' in necessary_params:
        seats_data = {}
        query = slave_session.query(Seat).join(SeatStatus).filter(Seat.venue==venue)
        query = query.with_entities(Seat.l0_id, Seat.name, Seat.seat_no, Seat.stock_id, SeatStatus.status)
        # 差分取得のときは販売可能かどうかに関わらず取得する
        if loaded_at:
            query = query.filter(or_(Seat.updated_at>loaded_at, SeatStatus.updated_at>loaded_at))
        elif sale_only:
            if not load_all_seat:
                query = query.filter(SeatStatus.status==SeatStatusEnum.Vacant.v)
            query = query.join(ProductItem, and_(ProductItem.performance_id==venue.performance_id, ProductItem.stock_id==Seat.stock_id))
            query = query.join(Product).join(SalesSegment).distinct()
            if sales_segment_id:
                query = query.filter(SalesSegment.id==sales_segment_id)
            if not permit_operator:
                query = query.join(SalesSegmentSetting).filter(SalesSegmentSetting.sales_counter_selectable==True)
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
        query = slave_session.query(Stock, func.count(ProductItem.id)).options(joinedload('stock_status')).filter_by(performance=venue.performance)
        query = query.outerjoin(ProductItem, and_(
            ProductItem.performance_id==venue.performance_id,
            ProductItem.stock_id==Stock.id,
            ProductItem.deleted_at==None
        ))
        # 差分取得のときは販売可能かどうかに関わらず取得する
        if loaded_at:
            query = query.join(StockStatus).filter(StockStatus.updated_at>loaded_at)
        elif sale_only:
            query = query.join(Product).join(SalesSegment)
            if sales_segment_id:
                query = query.filter(SalesSegment.id==sales_segment_id)
            if not permit_operator:
                query = query.join(SalesSegmentSetting).filter(SalesSegmentSetting.sales_counter_selectable==True)
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
        query = slave_session.query(StockType).filter_by(event=venue.performance.event).order_by(StockType.display_order)
        if sale_only:
            query = query.join(Stock, and_(Stock.performance_id==venue.performance_id, Stock.stock_type_id==StockType.id))
            query = query.join(ProductItem, and_(ProductItem.performance_id==venue.performance_id, ProductItem.stock_id==Stock.id))
            query = query.join(Product).join(SalesSegment).distinct()
            if sales_segment_id:
                query = query.filter(SalesSegment.id==sales_segment_id)
            if not permit_operator:
                query = query.join(SalesSegmentSetting).filter(SalesSegmentSetting.sales_counter_selectable==True)
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
        query = slave_session.query(StockHolder).filter_by(event=venue.performance.event).options(undefer(StockHolder.style))
        if sale_only:
            query = query.join(Stock, and_(Stock.performance_id==venue.performance_id, Stock.stock_holder_id==StockHolder.id))
            query = query.join(ProductItem, and_(ProductItem.performance_id==venue.performance_id, ProductItem.stock_id==Stock.id))
            query = query.join(Product).join(SalesSegment).distinct()
            if sales_segment_id:
                query = query.filter(SalesSegment.id==sales_segment_id)
            if not permit_operator:
                query = query.join(SalesSegmentSetting).filter(SalesSegmentSetting.sales_counter_selectable==True)
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
    slave_session = get_db_session(request, 'slave')
    venue = request.context.venue

    headers = [
        ('Content-Type', 'application/octet-stream; charset=cp932'),
        ('Content-Disposition', 'attachment; filename=seats_{date}.csv'.format(
            date=datetime.now().strftime('%Y%m%d%H%M%S')))
    ]
    response = Response(headers=headers)

    seats_q = slave_session.query(Seat, Order, include_deleted=True) \
        .options(undefer(Order.deleted_at))\
        .outerjoin(Seat.status_) \
        .outerjoin(Seat.stock) \
        .outerjoin(Stock.stock_holder) \
        .outerjoin(Stock.stock_type) \
        .outerjoin(Seat.ordered_product_items) \
        .outerjoin(OrderedProductItem.ordered_product) \
        .outerjoin(OrderedProduct.order) \
        .filter(Seat.venue_id == venue.id) \
        .filter(Seat.deleted_at == None) \
        .filter(Stock.deleted_at == None) \
        .filter(StockHolder.deleted_at == None) \
        .filter(StockType.deleted_at == None) \
        .order_by(asc(Seat.id), desc(Order.id), asc(Order.canceled_at), asc(Order.deleted_at), asc(Order.refunded_at))


    seats_csv = SeatCSV(seats_q)
    writer = csv.DictWriter(response, seats_csv.header,
                             delimiter=',', quoting=csv.QUOTE_ALL)
    writer.writeheader()
    writer.writerows(seats_csv.rows)
    return response

@view_config(route_name='venues.index', renderer='altair.app.ticketing:templates/venues/index.html',
             decorator=with_bootstrap, permission='event_editor')
def index(request):
    query = DBSession.query(Venue, Site, Performance) \
                     .join(Site, and_(Site.id==Venue.site_id, Site.deleted_at==None)) \
                     .outerjoin(Performance, and_(Performance.id==Venue.performance_id, Performance.deleted_at==None)) \
                     .filter(Venue.organization_id==request.context.user.organization_id) \
                     .group_by(Venue.id) \
                     .order_by(desc(Venue.site_id), asc(-Venue.performance_id))

    query = query.options(undefer(Site.created_at), undefer(Performance.created_at))

    form = VenueSearchForm(request.params)
    if request.params:
        if form.validate():
            if form.venue_name.data:
                pattern = u'%{}%'.format(form.venue_name.data)
                query = query.filter(Site.name.like(pattern))
            if form.prefecture.data:
                query = query.filter(Site.prefecture==form.prefecture.data)

    # 会場の表示、非表示
    if not request.session.get(VISIBLE_VENUES_SESSION_KEY, None):
        query = query.filter(Site.visible==True)

    items = paginate.Page(
        query,
        page=int(request.params.get('page', 0)),
        items_per_page=200,
        url=PageURL_WebOb_Ex(request)
    )

    return dict(items=items, form=form)

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


@view_defaults(permission='event_editor')
class VenueShowView(BaseView):
    class SeatAdjacencyInfo(object):
        __slots__ = (
            'adj',
            'count',
            )
        def __init__(self, adj, count):
            self.adj = adj
            self.count = count

    def get_seat_adjacency_counts(self, venue):
        slave_session = get_db_session(self.request, 'slave')
        adjacency_sets = slave_session.query(SeatAdjacencySet).filter_by(site_id=venue.site_id).all()
        retval = []
        for adjacency_set in adjacency_sets:
            count = slave_session\
                .query(Seat_SeatAdjacency) \
                .join(SeatAdjacency)\
                .filter(SeatAdjacency.adjacency_set_id == adjacency_set.id)\
                .with_entities(func.count(distinct(Seat_SeatAdjacency.l0_id)))\
                .scalar()
            # count = slave_session\
            #     .query(Seat) \
            #     .join(Seat_SeatAdjacency, Seat_SeatAdjacency.l0_id == Seat.l0_id)\
            #     .join(SeatAdjacency)\
            #     .filter(SeatAdjacency.adjacency_set_id == adjacency_set.id, Seat.venue_id == venue.id)\
            #     .with_entities(func.count(distinct(Seat.id)))\
            #     .scalar()
            retval.append(self.SeatAdjacencyInfo(adjacency_set, count))
        return retval

    @view_config(route_name='venues.show._seat_adjacency_counts',
                 renderer='altair.app.ticketing:templates/venues/_seat_adjacency_counts.html')
    def seat_adjacency_count(self):
        return dict(adjs=self.get_seat_adjacency_counts(self.context.venue))

    @view_config(route_name='venues.show',
                 renderer='altair.app.ticketing:templates/venues/show.html',
                 decorator=with_bootstrap)
    def get(self):
        request = self.request
        venue = self.context.venue
        venue_id = venue.id
        slave_session = get_db_session(request, 'slave')

        site = venue.site
        drawing = get_venue_site_adapter(request, site)
        root = None
        pages = drawing.get_frontend_pages()
        if pages:
            for page, info in pages.items():
                if info.get('root'):
                    root = page

        types = slave_session.query(SeatIndexType).filter_by(venue_id=venue_id).all()
        type_id = types[0].id if 0<len(types) else None
        if 'index_type' in request.GET:
            type_id = 2
            for type in types:
                if request.GET.get('index_type') == str(type.id):
                    type_id = type.id

        class SeatInfo(object):
            __slots__ = (
                'seat',
                'venuearea',
                'row',
                'status',
                'index',
                )
            def __init__(self, seat, venuearea, attr, status, index):
                self.seat = seat
                self.venuearea = venuearea
                self.row = attr
                self.status = status
                self.index = index

        seats = slave_session.query(Seat, VenueArea, SeatAttribute, SeatStatus, SeatIndex)\
            .filter_by(venue_id=venue_id)\
            .outerjoin(VenueArea, Seat.areas)\
            .outerjoin(SeatAttribute, and_(SeatAttribute.seat_id==Seat.id, SeatAttribute.name=="row"))\
            .outerjoin(SeatStatus, SeatStatus.seat_id==Seat.id)
        if type_id is not None:
            seats = seats.outerjoin(SeatIndex, and_(SeatIndex.seat_id==Seat.id, SeatIndex.seat_index_type_id==type_id))
        items = []
        for seat, venuearea, attr, status, type in seats:
            items.append(SeatInfo(seat, venuearea, attr, status, type))

        return {
            'venue': venue,
            'site': site,
            'drawing': drawing,
            'root': root,
            'type_id': type_id,
            'types': types,
            'pages': pages,
            'items': items,
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

@view_config(route_name='venues.new', request_method='GET', renderer='altair.app.ticketing:templates/venues/new_edit.html',
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

@view_config(route_name='venues.new', request_method='POST', renderer='altair.app.ticketing:templates/venues/new_edit.html',
             decorator=with_bootstrap, permission='event_editor')
def new_post(request):
    f = SiteForm(request.POST)

    if f.validate():
        site = merge_session_with_post(Site(), f.data)
        site.visible = True
        try:
            siteprofile = SiteProfile.get_by_name_and_prefecture(site.name, site.prefecture)
        except NoReSultFound:
            siteprofile = SiteProfile(name = site.name, prefecture = site.prefecture)
            siteprofile.save()
        except MultipleResultsFound:
            logger.error("Multople SiteProfile with same name and prefecture found: (name: %s, prefecture: %s)" % (site.name, site.prefecture))
            request.session.flash("名前と都道府県が同じ会場プロファイルが複数存在します (名前: %s, 都道府県: %s)" % (site.name, site.prefecture))
        site.siteprofile = siteprofile
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

        # Also update corresponding Site only when if this venue is original
        if venue.performance_id is None:
            site = merge_session_with_post(venue.site, f.data)
            default_siteprofile = SiteProfile.get_default_siteprofile()
            if site.siteprofile_id == default_siteprofile.id: # if site's siteprofile is default
                if site.name != default_siteprofile.name or site.prefecture != default_siteprofile.prefecture:
                    # Create new SiteProfile if name or prefecture is different rather than updating default one
                    siteprofile = SiteProfile(name = site.name, prefecture = site.prefecture)
                    siteprofile.save()
                    site.siteprofile = siteprofile
            else:
                siteprofile = SiteProfile.get_by_name_and_prefecture(site.name, site.prefecture)
                if siteprofile is not None: # If there is an existing one
                    if site.siteprofile_id != siteprofile.id:
                        site.siteprofile = siteprofile
                else:
                    siteprofile = SiteProfile(name = site.name, prefecture = site.prefecture)
                    siteprofile.save()
                    site.siteprofile = siteprofile
            site.save()

        request.session.flash(u'会場を保存しました')
        return HTTPFound(location=route_path('venues.show', request, venue_id=venue.id))
    else:
        return {
            'form': f,
            'venue': venue,
            'site': venue.site,
            'drawing': get_venue_site_adapter(request, venue.site),
            'route_name': u'編集',
            'route_path': request.path,
            }

@view_config(route_name='venues.visible', decorator=with_bootstrap, permission='event_editor')
def visible_venues(request):
    set_visible_venue(request)
    return HTTPFound(request.route_path("venues.index"))

@view_config(route_name='venues.invisible', decorator=with_bootstrap, permission='event_editor')
def invisible_venues(request):
    set_invisible_venue(request)
    return HTTPFound(request.route_path("venues.index"))

def includeme(config):
    config.registry.registerUtility(
        VenueSiteDrawingHandler(config),
        IVenueSiteDrawingHandler
        )
