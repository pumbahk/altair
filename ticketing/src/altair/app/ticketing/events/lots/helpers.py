# -*- coding:utf-8 -*-
from api import get_lots_cart_url
from sqlalchemy import sql
from webhelpers.html.tags import link_to
from altair.app.ticketing.lots.helpers import timezone_label
from altair.app.ticketing.core.models import (
    DBSession,
    Performance,
    StockStatus,
    ProductItem,
    Product,
    Stock,
)
from altair.app.ticketing.lots.models import (
    LotEntry,
    LotEntryWish,
    LotElectedEntry,
    LotEntryProduct,
    LotRejectWork,
)


class Link(object):
    def __init__(self, label, url, **attrs):
        self.label = label
        self.url = url
        self.attrs = attrs

    def __html__(self):
        return link_to(self.label, self.url, **self.attrs)

    def __str__(self):
        return self.__html__()


def lots_cart_url(request, event_id, lot_id):
    return get_lots_cart_url(request=request, event_id=event_id, lot_id=lot_id)


def is_quantity_only_stock_type(lot, seat_stock_type):
    stock_types = lot.event.stock_types
    for stock_type in stock_types:
        if stock_type.id == seat_stock_type.id:
            if stock_type.quantity_only:
                return True
    return False


def exist_not_quantity_only_stock_type(lot):
    for product in lot.products:
        if not is_quantity_only_stock_type(lot, product.seat_stock_type):
            # 座席選択あり
            return True
    return False

def performance_stock_quantity(lot_id):
    s = [Stock, Performance, sql.func.sum(LotEntryProduct.quantity * ProductItem.quantity)]
    performance_stock_info = DBSession.query(*s).filter(
        LotEntry.lot_id == lot_id
    ).filter(
        LotEntryWish.lot_entry_id == LotEntry.id
    ).filter(
        LotElectedEntry.lot_entry_id == LotEntry.id
    ).filter(
        LotEntryProduct.lot_wish_id == LotEntryWish.id
    ).filter(
        LotEntryProduct.product_id == Product.id
    ).filter(
        Product.id == ProductItem.product_id
    ).filter(
        Stock.id == ProductItem.stock_id
    ).filter(
        Performance.id == ProductItem.performance_id
    ).filter(
        LotElectedEntry.completed_at == None
    ).filter(
        LotEntryWish.canceled_at == None
    ).filter(
        LotEntryWish.elected_at != None
    ).group_by(Stock.id)

    return performance_stock_info.all()

def rejecting_count(lot_id):
    lot_reject_cnt = LotRejectWork.query.filter(
        LotRejectWork.lot_entry_no == LotEntry.entry_no
    ).filter(
        LotEntry.lot_id == lot_id
    ).count()

    return lot_reject_cnt
