# -*- coding: utf-8 -*-

def includeme(config):
    config.add_route('products.new', '/new')
    config.add_route('products.edit', '/edit/{product_id}')
    config.add_route('products.delete', '/delete/{product_id}')
    config.add_route('products.api.get', '/api/get/')
    config.add_route('products.api.set', '/api/set/')

    config.add_route('product_items.new', '/items/new/{product_id}')
    config.add_route('product_items.edit', '/items/edit/{product_item_id}')
    config.add_route('product_items.delete', '/items/delete/{product_item_id}')
    config.scan(".views")


    config.add_route('product.new', '/product/new')
