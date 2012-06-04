# -*- coding: utf-8 -*-
from ticketing.resources import *

def includeme(config):
    config.add_route('stock_types.index', '/{event_id}')
    config.add_route('stock_types.new', '/new/{event_id}')
    config.add_route('stock_types.edit', '/edit/{stock_type_id}')
    config.add_route('stock_types.delete', '/delete/{stock_type_id}')
    config.add_route('stock_types.allocate', '/allocate/')
