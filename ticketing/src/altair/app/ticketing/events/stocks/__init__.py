# -*- coding: utf-8 -*-
from altair.app.ticketing.resources import *

def includeme(config):
    config.add_route('stocks.allocate', '/allocate/{performance_id}')
