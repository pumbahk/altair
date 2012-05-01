# -*- coding: utf-8 -*-
from ticketing.resources import *

def includeme(config):
    config.add_route('performances.index', '/')
    config.add_route('performances.new', '/{event_id}/new')
    config.add_route('performances.show', '/show/{performance_id}')
    config.add_route('performances.edit', '/edit/{performance_id}')
    config.add_route('performances.delete', '/delete/{performance_id}')
    config.add_route('performances.stock_holder.new', '/stock_holder/new/{performance_id}')
