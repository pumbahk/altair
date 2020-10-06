# -*- coding: utf-8 -*-
from altair.app.ticketing import newRootFactory
from .resources import ProductResource, ProductCreateResource, ProductAPIResource, ProductShowResource\
    , ProductItemResource, TapirsProductResource


def includeme(config):
    product_factory = newRootFactory(ProductResource)
    config.add_route('products.edit', '/edit/{product_id}', factory=product_factory)
    config.add_route('products.delete', '/delete/{product_id}', factory=product_factory)
    config.add_route('product_items.new', '/items/new/{product_id}', factory=product_factory)

    tapirs_factory = newRootFactory(TapirsProductResource)
    config.add_route('tapirs.products.download', '/tapirs/download/{product_id}', factory=tapirs_factory)

    product_item_factory = newRootFactory(ProductItemResource)
    config.add_route('product_items.edit', '/items/edit/{product_item_id}', factory=product_item_factory)
    config.add_route('product_items.delete', '/items/delete/{product_item_id}', factory=product_item_factory)

    product_create_factory = newRootFactory(ProductCreateResource)
    config.add_route('products.new', '/new', factory=product_create_factory)
    config.add_route('products.copy', '/copy', factory=product_create_factory)

    product_api_factory = newRootFactory(ProductAPIResource)
    config.add_route('products.api.get', '/api/get/', factory=product_api_factory)
    config.add_route('products.api.set', '/api/set/', factory=product_api_factory)

    show_factory = newRootFactory(ProductShowResource)
    config.add_route("products.sub.newer.show", "/sub/show/newer/{sales_segment_id}", factory=show_factory)
    config.add_route("products.sub.older.show", "/sub/show/older/{sales_segment_id}", factory=show_factory)


    config.scan(".views")
