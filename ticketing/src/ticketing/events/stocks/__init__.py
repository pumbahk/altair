# -*- coding: utf-8 -*-
from ticketing.resources import *

def includeme(config):
    config.add_route('stocks.edit', '/edit/{performance_id}/{stock_holder_id}')
    config.add_route('stocks.allocate_number', '/allocate_number')
    config.add_route('stocks.allocate', '/allocate/{performance_id}')
