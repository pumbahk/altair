# -*- coding: utf-8 -*-
from ticketing.resources import *

def includeme(config):
    config.add_route('stock_allocations.allocate_number', '/allocate_number')
    config.add_route('stock_allocations.allocate_seat', '/allocate_seat')
