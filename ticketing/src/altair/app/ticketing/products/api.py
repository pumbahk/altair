# -*- coding: utf-8 -*-
from altair.app.ticketing.lots.models import Lot
from altair.app.ticketing.core.models import DBSession
from altair.app.ticketing.core.models import Product, ProductItem


def get_lot_product(original_product_id):
    return Product.query.filter(Product.original_product_id == original_product_id).first()


def get_lot_product_item(original_product_item_id):
    return ProductItem.query.filter(ProductItem.original_product_item_id == original_product_item_id).first()


def add_lot_product(sales_segment_group, original_product):
    for ss in sales_segment_group.sales_segments:
        lot = Lot.query.filter(Lot.sales_segment_id == ss.id).first()
        if lot:
            product = Product(name=original_product.name,
                              price=original_product.price,
                              display_order=original_product.display_order,
                              description=original_product.description,
                              seat_stock_type_id=original_product.seat_stock_type_id,
                              performance_id=original_product.performance_id,
                              sales_segment=lot.sales_segment,
                              original_product_id=long(original_product.id))
            DBSession.add(product)
            return product


def add_lot_product_item(lot_product, original_product_item):
    product_item = ProductItem(
        performance_id=original_product_item.performance_id,
        product=lot_product,
        name=original_product_item.name,
        price=original_product_item.price,
        quantity=original_product_item.quantity,
        stock_id=original_product_item.stock_id,
        ticket_bundle_id=original_product_item.ticket_bundle_id,
        original_product_item_id=original_product_item.id
    )
    product_item.save()
    return product_item


def edit_lot_product(original_product):
    lot_product = get_lot_product(original_product.id)
    if not lot_product:
        return None

    lot_product.name = original_product.name
    lot_product.price = original_product.price
    lot_product.display_order = original_product.display_order
    lot_product.description = original_product.description
    lot_product.seat_stock_type_id = original_product.seat_stock_type_id
    lot_product.min_product_quantity = original_product.min_product_quantity
    lot_product.min_product_quantity = original_product.max_product_quantity
    return lot_product


def edit_lot_product_item(original_product_item):
    lot_product_item = get_lot_product_item(original_product_item.id)
    if not lot_product_item:
        return None

    lot_product_item.name = original_product_item.name
    lot_product_item.price = original_product_item.price
    lot_product_item.quantity = original_product_item.quantity
    lot_product_item.ticket_bundle_id = original_product_item.ticket_bundle_id
    return lot_product_item


def delete_lot_product(original_product):
    lot_product = get_lot_product(original_product.id)
    if lot_product:
        lot_product.delete()


def delete_lot_product_item(original_product_item):
    lot_product_item = get_lot_product_item(original_product_item.id)
    if lot_product_item:
        lot_product_item.delete()
