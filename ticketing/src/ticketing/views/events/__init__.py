# -*- coding: utf-8 -*-
from ticketing.resources import *

def add_routes(config):
    config.add_route('admin.events.index'   , '/')
    config.add_route('admin.events.new'     , '/new')
    config.add_route('admin.events.show'    , '/show/{event_id}')
    config.add_route('admin.events.edit'    , '/edit/{event_id}')
    config.add_route('admin.events.delete'  , '/delete/{event_id}')
