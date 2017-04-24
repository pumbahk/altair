# -*- coding:utf-8 -*-
from altair.sqlahelper import get_db_session
from altair.app.ticketing.core.models import (
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
