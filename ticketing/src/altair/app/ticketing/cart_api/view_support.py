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
    StockStatus,
    Stock_drawing_l0_id
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


def parse_fields_params(request):
    """return params list"""
    fields = request.GET.get('fields')
    if fields:
        fields = fields.replace(' ', '').split(',')
    else:
        fields = []
    return fields


def get_filtered_stock_types(request, sales_segment, session=None):
    if not session:
        session = get_db_session(request, 'slave')
    params = request.GET
    min_price = params.get("min_price", None)
    max_price = params.get("max_price", None)
    need_quantity = params.get("quantity", "1")
    stock_type_name = params.get("stock_type_name", None)

    from decimal import Decimal
    min_price = Decimal(min_price) if min_price else None
    max_price = Decimal(max_price) if max_price else None
    need_quantity = Decimal(need_quantity)

    # 在庫設定があって公開されているものだけ
    stock_list = session.query(Stock, StockStatus, StockType, Product.price)\
        .join(StockType)\
        .join(StockStatus)\
        .join(Product)\
        .join(ProductItem)\
        .filter(Product.sales_segment_id==sales_segment.id)\
        .filter(Stock.performance_id==sales_segment.performance_id)\
        .filter(ProductItem.stock_id==Stock.id)\
        .filter(0 < Stock.quantity)\
        .filter(StockType.display == 1)\
        .filter(Product.public == 1)\
        .order_by(StockType.id, Product.display_order)

    stock_type_dict = dict()
    rest_quantity_by_stock = dict()
    for stock, stock_status, stock_type, price in stock_list:
        # 名称が含まれているか？
        if stock_type_name and stock_type.name.count(stock_type_name) == 0:
            continue

        if stock_type.id not in stock_type_dict:
            # logger.debug("count stock %d-%d(%d/%d)" % (stock_type.id, stock.id, stock_status.quantity, stock.quantity))
            rest_quantity_by_stock[stock.id] = stock_status.quantity
            stock_type_dict[stock_type.id] = dict(
                stock_type_id=stock_type.id,
                stock_type_name=stock_type_name,
                first_product_price=price,

                stocks=[stock],
                quantity=stock.quantity,
                rest_quantity=stock_status.quantity
            )
        else:
            if stock.id not in rest_quantity_by_stock:
                logger.debug("count stock %d-%d(%d/%d)" % (stock_type.id, stock.id, stock_status.quantity, stock.quantity))
                rest_quantity_by_stock[stock.id] = stock_status.quantity
                stock_type_dict[stock_type.id]['stocks'].append(stock)
                stock_type_dict[stock_type.id]['quantity'] += stock.quantity
                stock_type_dict[stock_type.id]['rest_quantity'] += stock_status.quantity

    filtered_stock_type = []
    for stock_type_id, d in stock_type_dict.iteritems():
        # 価格は、先頭の商品で判定する
        if min_price and d['first_product_price'] < min_price:
            continue

        if max_price and max_price < d['first_product_price']:
            continue

        # 残席数が足りていなければ除外
        if need_quantity and d['rest_quantity'] < need_quantity:
            continue

        filtered_stock_type.append(d)

    stock_dict = dict()
    for d in filtered_stock_type:
        for s in d['stocks']:
            if s.id not in stock_dict:
                stock_dict[s.id] = s

    stock_ids = stock_dict.keys()

    region_dict = dict()
    drawing_list = session.query(Stock_drawing_l0_id.stock_id, Stock_drawing_l0_id.drawing_l0_id)\
        .filter(Stock_drawing_l0_id.stock_id.in_(stock_ids))
    for stock_id, drawing_l0_id in drawing_list:
        stock = stock_dict[stock_id]
        rest_quantity = rest_quantity_by_stock[stock_id]

        # 1つのregionに複数のstockが設定されていると、重複して加算されるが、やむ無し
        if drawing_l0_id not in region_dict:
            region_dict[drawing_l0_id] = dict(
                quantity=0,
                rest_quantity=0,
                #by_stock_type=dict()
            )
        region_dict[drawing_l0_id]['quantity'] += stock.quantity
        region_dict[drawing_l0_id]['rest_quantity'] += rest_quantity

        #if stock_type_id not in region_dict[drawing_l0_id]['by_stock_type']:
        #    region_dict[drawing_l0_id]['by_stock_type'][stock_type_id] = dict(
        #        quantity=0,
        #        rest_quantity=0,
        #    )
        #region_dict[drawing_l0_id]['by_stock_type'][stock_type_id]['quantity'] += stock.quantity
        #region_dict[drawing_l0_id]['by_stock_type'][stock_type_id]['rest_quantity'] += rest_quantity

    return dict(
        stock_types=[dict(
            stock_type_id=v['stock_type_id'],
            quantity=v['quantity'],
            rest_quantity=v['rest_quantity'],
            stocks=v['stocks']
        ) for v in filtered_stock_type],
        regions=[dict(
            region_id=id,
            quantity=v['quantity'],
            rest_quantity=v['rest_quantity']
        ) for id, v in region_dict.iteritems()],
    )


def search_seat(request, stock_ids, session=None):
    if not session:
        session = get_db_session(request, 'slave')
    q = session.query(Seat.l0_id, Seat.stock_id, SeatStatus.status)\
            .join(Seat.status_)\
            .filter(Seat.stock_id.in_(stock_ids))
    return q


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