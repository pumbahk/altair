# -*- coding: utf-8 -*-

def includeme(config):
    config.add_route('products.index', '/{event_id}')
    config.add_route('products.new', '/new/{event_id}')
    config.add_route('products.edit', '/edit/{product_id}')
    config.add_route('products.delete', '/delete/{product_id}')

    config.add_route('product_items.new', '/items/new')
    config.add_route('product_items.edit', '/items/edit/{product_item_id}')
    config.add_route('product_items.delete', '/items/delete/{product_item_id}')
    config.scan(".")
