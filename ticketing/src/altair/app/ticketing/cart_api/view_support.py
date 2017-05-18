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
from ..cart.helpers import get_availability_text
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


def build_region_dict(sales_segment, min_price, max_price, need_quantity):
    # svg側では描画エリアをregionと定義しているのでそれに合わせる
    """
    リージョン毎の在庫状況を取得
    条件
    ・配席されている
    ・商品が公開中
    ・販売区分で公開中
    返り値
    ・{region_id:region_status(◎☓△)}
    """
    # region毎の在庫を集計
    from decimal import Decimal
    min_price = Decimal(min_price) if min_price else None
    max_price = Decimal(max_price) if max_price else None
    need_quantity = Decimal(need_quantity) if need_quantity else None

    region_dict = dict()
    for stock in sales_segment.performance.stocks:
        if stock.quantity == 0:
            continue

        if not stock.product_items:
            continue

        if not stock.product_items[0].product.public:
            continue

        if not stock.performance.sales_segments[0].public:
            if not stock.performance.sales_segments[0].use_default_stock_holder_id:
                continue

            if not stock.performance.sales_segments[0].sales_segment_group.stock_holder_id:
                continue

        price = 0
        for item in stock.product_items:
            price = price + item.price

        for drawing_l0_id in stock.drawing_l0_ids:
            quantity = stock.quantity
            rest_quantity = stock.stock_status.quantity

            if drawing_l0_id in region_dict:
                quantity = quantity + region_dict[drawing_l0_id]['quantity']
                rest_quantity = rest_quantity + region_dict[drawing_l0_id]['rest_quantity']

            if need_quantity and rest_quantity < need_quantity:
                continue

            if min_price and price < min_price:
                continue

            if max_price and price > max_price:
                continue

            region_dict.update({drawing_l0_id: dict(quantity=quantity, rest_quantity=rest_quantity)})

    # region毎のステータスを入れる
    for key in region_dict:
        values = region_dict[key]
        setting = sales_segment.event.setting
        status = get_availability_text(values['quantity'], values['rest_quantity']
                              , setting.middle_stock_threshold, setting.middle_stock_threshold_percent)
        region_dict.update({key: status})

    return region_dict


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