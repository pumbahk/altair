# -*- coding: utf-8 -*-

def includeme(config):
    config.add_route('stock_holders.new', '/new')
    config.add_route('stock_holders.edit', '/edit/{stock_holder_id}')
    config.add_route('stock_holders.delete', '/delete/{stock_holder_id}')
