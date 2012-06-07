# -*- coding: utf-8 -*-
from ticketing.resources import *

def includeme(config):
    config.add_route('stocks.allocate_number', '/allocate_number')
    config.add_route('stocks.edit', '/edit/{stock_holder_id}')
