# -*- coding:utf-8 -*-

""" PC/Mobile のスーパービュークラス
"""
import logging
from pyramid.httpexceptions import HTTPFound
from sqlalchemy.sql.expression import desc, asc
from sqlalchemy.orm import joinedload, aliased
from altair.app.ticketing.core import models as c_models
from altair.app.ticketing.models import DBSession
from . import helpers as h
from collections import OrderedDict
from .exceptions import NoEventError
from .resources import PerformanceOrientedTicketingCartResource

logger = logging.getLogger(__name__)

class IndexViewMixin(object):
    def prepare(self):
        if self.context.event is None:
            raise NoEventError()

        from .api import get_event_info_from_cms
        self.event_extra_info = get_event_info_from_cms(self.request, self.context.event.id)
        logger.info(self.event_extra_info)

    def check_redirect(self, mobile):
        if isinstance(self.request, PerformanceOrientedTicketingCartResource):
            performance_id = self.request.context.performance.id
        else:
            performance_id = self.request.params.get('pid') or self.request.params.get('performance')

        if performance_id:
            specified = c_models.Performance.query.filter(c_models.Performance.id==performance_id).filter(c_models.Performance.public==True).first()
            if mobile:
                if specified is not None and specified.redirect_url_mobile:
                    raise HTTPFound(specified.redirect_url_mobile)
            else:
                if specified is not None and specified.redirect_url_pc:
                    raise HTTPFound(specified.redirect_url_pc)

def get_amount_without_pdmp(cart):
    return sum([cp.product.price * cp.quantity for cp in cart.products])

def get_seat_type_dicts(request, sales_segment, seat_type_id=None):
    # TODO: cachable
    q = DBSession.query(c_models.StockType, c_models.Product, c_models.ProductItem, c_models.Stock, c_models.StockStatus.quantity) \
        .filter(c_models.StockType.display == True) \
        .filter(c_models.Product.public == True) \
        .filter(c_models.Product.deleted_at == None) \
        .filter(c_models.ProductItem.product_id==c_models.Product.id) \
        .filter(c_models.ProductItem.stock_id==c_models.Stock.id) \
        .filter(c_models.ProductItem.deleted_at == None) \
        .filter(c_models.Stock.stock_type_id==c_models.StockType.id) \
        .filter(c_models.Stock.deleted_at == None) \
        .filter(c_models.StockHolder.id==c_models.Stock.stock_holder_id) \
        .filter(c_models.StockHolder.deleted_at == None) \
        .filter(c_models.StockStatus.stock_id==c_models.Stock.id) \
        .filter(c_models.Product.sales_segment_id == sales_segment.id) \
        .order_by(
            asc(c_models.StockType.display_order),
            asc(c_models.Product.display_order),
            desc(c_models.Product.price)
            )

    if seat_type_id is not None:
        _ProductItem = aliased(c_models.ProductItem)
        _Product = aliased(c_models.Product)
        _Stock = aliased(c_models.Stock)
        q = q.filter(c_models.Product.id.in_(
            DBSession.query(_Product.id) \
            .filter(_Product.id == _ProductItem.product_id) \
            .filter(_ProductItem.stock_id == _Stock.id) \
            .filter(_Stock.stock_type_id == seat_type_id) \
            .distinct()))

    stock_types = OrderedDict()
    products_for_stock_type = dict()
    product_items_for_product = dict()
    stock_for_product_item = dict()

    availability_per_product_map = dict()
    for stock_type, product, product_item, stock, available in q:
        if stock_type.id not in stock_types:
            stock_types[stock_type.id] = stock_type

        products = products_for_stock_type.get(stock_type.id)
        if products is None:
            products = products_for_stock_type[stock_type.id] = OrderedDict()
        products[product.id] = product

        product_items = product_items_for_product.get(product.id)
        if product_items is None:
            product_items = product_items_for_product[product.id] = []
        product_items.append(product_item)

        stock_for_product_item[product_item.id] = stock

        availability_per_product = availability_per_product_map.get(product.id)
        if availability_per_product is None:
            availability_per_product = available / product_item.quantity
        else:
            availability_per_product = min(availability_per_product, available)
        availability_per_product_map[product.id] = availability_per_product

    retval = []
    for stock_type in stock_types.itervalues():
        availability_for_stock_type = max(availability_per_product_map[product_id] for product_id in products_for_stock_type[stock_type.id])
        product_dicts = []
        for product in products_for_stock_type[stock_type.id].itervalues():
            quantity_power = sum([product_item.quantity for product_item in product_items_for_product[product.id] if stock_for_product_item[product_item.id].stock_type_id == product.seat_stock_type_id])
            product_dicts.append(
                dict(
                    id=product.id,
                    name=product.name,
                    description=product.description,
                    price=h.format_number(product.price, ","), 
                    detail=h.product_name_with_unit(product_items_for_product[product.id]),
                    unit_template=h.build_unit_template(product_items_for_product[product.id]),
                    quantity_power=quantity_power,
                    upper_limit=min(sales_segment.upper_limit / quantity_power, availability_per_product_map[product.id]),
                    product_limit=sales_segment.product_limit
                    )
                )
        retval.append(dict(
            id=stock_type.id,
            name=stock_type.name,
            description=stock_type.description,
            style=stock_type.style,
            availability=availability_for_stock_type,
            availability_text=h.get_availability_text(availability_for_stock_type),
            quantity_only=stock_type.quantity_only,
            seat_choice=sales_segment.seat_choice,
            products=product_dicts
            ))

    if seat_type_id is not None:
        retval = [stock_type_dict for stock_type_dict in retval if stock_type_dict['id'] == seat_type_id]

    return retval
