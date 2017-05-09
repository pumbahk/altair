# -*- coding:utf-8 -*-
from altair.sqlahelper import get_db_session
from altair.app.ticketing.core.models import (
    Performance,
    StockType,
    Seat,
    Stock,
    StockType,
    SeatStatus,
    SeatStatusEnum,
    Product,
    ProductItem,
    SalesSegment,
    StockStatus
)
from sqlalchemy import distinct, func

from altair.app.ticketing.models import DBSession

from altair.app.ticketing.venues.api import get_venue_site_adapter
from datetime import datetime, timedelta
from altair.pyramid_boto.s3.assets import IS3KeyProvider
import time
import re
import logging
logger = logging.getLogger(__name__)


def build_seat_query(request, sales_segment_id, session=None):
    if not session:
        session = get_db_session(request, 'slave')
    params = request.GET
    q = session.query(distinct(Seat.l0_id), Stock, Stock.stock_type_id, SeatStatus.status, StockStatus.quantity)\
            .join(Seat.status_)\
            .join(Seat.stock)\
            .join(Stock.product_items)\
            .join(Stock.stock_status)\
            .join(Stock.stock_type)\
            .join(ProductItem.product)\
            .join(Product.sales_segment)\
            .filter(SalesSegment.id == sales_segment_id)
    if params.get('min_price'):
        q = q.filter(Product.price >= params.get('min_price'))
    if params.get('max_price'):
        q = q.filter(Product.price <= params.get('max_price'))
    if params.get('stock_type_name'):
        q = q.filter(StockType.name.like(u'%{}%'.format(params.get('stock_type_name'))))
    if params.get('quantity'):
        q = q.filter(StockStatus.quantity >= params.get('quantity'))
    return q


def build_non_seat_query(request, sales_segment_id, session=None):
    if not session:
        session = get_db_session(request, 'slave')
    params = request.GET
    q = session.query(Stock, Stock.stock_type_id, StockStatus.quantity)\
            .join(Stock.product_items)\
            .join(Stock.stock_status)\
            .join(Stock.stock_type)\
            .join(ProductItem.product)\
            .join(Product.sales_segment)\
            .filter(SalesSegment.id == sales_segment_id)\
            .filter(StockType.quantity_only == True)
    if params.get('min_price'):
        q = q.filter(Product.price >= params.get('min_price'))
    if params.get('max_price'):
        q = q.filter(Product.price <= params.get('max_price'))
    if params.get('stock_type_name'):
        q = q.filter(StockType.name.like(u'%{}%'.format(params.get('stock_type_name'))))
    if params.get('quantity'):
        q = q.filter(StockStatus.quantity >= params.get('quantity'))
    return q


def parse_fields_parmas(request):
    """return params list"""
    fields = request.GET.get('fields')
    if fields:
        fields = fields.replace(' ', '').split(',')
    else:
        fields = []
    return fields


def get_spa_svg_urls(request, performance_id):
    retval = {}
    performance = DBSession.query(Performance).filter_by(id=performance_id).first()
    drawings = get_venue_site_adapter(request, performance.venue.site).get_frontend_drawings_spa()
    if drawings:
        for name, drawing in drawings.items():
            url = ''
            if IS3KeyProvider.providedBy(drawing):
                key = drawing.get_key()
                headers = {}
                if re.match('^.+\.(svgz|gz)$', drawing.path):
                    headers['response-content-encoding'] = 'gzip'
                cache_minutes = 30
                expire_date = datetime.now() + timedelta(minutes=cache_minutes)
                expire_date = expire_date.replace(minute=(expire_date.minute/cache_minutes*cache_minutes), second=0)
                expire_epoch = time.mktime(expire_date.timetuple())
                url = key.generate_url(expires_in=expire_epoch, expires_in_absolute=True, response_headers=headers)
            retval[name] = url
    return retval