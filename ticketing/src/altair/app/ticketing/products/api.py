# -*- coding: utf-8 -*-
from altair.app.ticketing.lots.models import Lot
from altair.app.ticketing.core.models import DBSession
from altair.app.ticketing.core.models import Product, ProductItem


def get_lot_products(original_product_id):
    return Product.query.filter(Product.original_product_id == original_product_id).all()


def get_lot_product_items(original_product_item_id):
    return ProductItem.query.filter(ProductItem.original_product_item_id == original_product_item_id).all()


def add_lot_product(sales_segment_group, original_product):
    for ss in sales_segment_group.sales_segments:
        lots = Lot.query.filter(Lot.sales_segment_id == ss.id).all()
        for lot in lots:
            product = Product(name=original_product.name,
                              price=original_product.price,
                              display_order=original_product.display_order,
                              description=original_product.description,
                              seat_stock_type_id=original_product.seat_stock_type_id,
                              performance_id=original_product.performance_id,
                              sales_segment=lot.sales_segment,
                              original_product_id=long(original_product.id))
            DBSession.add(product)

            # 抽選商品明細の登録
            for product_item in original_product.items:
                add_lot_product_item(product, product_item)


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
    lot_products = get_lot_products(original_product.id)

    for lot_product in lot_products:
        lot_product.name = original_product.name
        lot_product.price = original_product.price
        lot_product.display_order = original_product.display_order
        lot_product.description = original_product.description
        lot_product.seat_stock_type_id = original_product.seat_stock_type_id
        lot_product.min_product_quantity = original_product.min_product_quantity
        lot_product.min_product_quantity = original_product.max_product_quantity


def edit_lot_product_item(original_product_item):
    lot_product_items = get_lot_product_items(original_product_item.id)
    for lot_product_item in lot_product_items:
        lot_product_item.name = original_product_item.name
        lot_product_item.price = original_product_item.price
        lot_product_item.quantity = original_product_item.quantity
        lot_product_item.ticket_bundle_id = original_product_item.ticket_bundle_id


def edit_lot_product_add_lot_product_item(original_product, original_product_item):
    lot_products = get_lot_products(original_product.id)
    for lot_product in lot_products:
        lot_product.name = original_product.name
        lot_product.price = original_product.price
        lot_product.display_order = original_product.display_order
        lot_product.description = original_product.description
        lot_product.seat_stock_type_id = original_product.seat_stock_type_id
        lot_product.min_product_quantity = original_product.min_product_quantity
        lot_product.min_product_quantity = original_product.max_product_quantity

        add_lot_product_item(lot_product, original_product_item)


def delete_lot_product(original_product):
    lot_products = get_lot_products(original_product.id)
    for lot_product in lot_products:
        lot_product.delete()


def delete_lot_product_item(original_product_item):
    lot_product_items = get_lot_product_items(original_product_item.id)
    for lot_product_item in lot_product_items:
        lot_product_item.delete()
