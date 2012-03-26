# -*- coding: utf-8 -*-
from ticketing.resources import *

def includeme(config):

    config.add_route('events.index'   , '/')
    config.add_route('events.new'     , '/new')
    config.add_route('events.show'    , '/show/{event_id}')
    config.add_route('events.edit'    , '/edit/{event_id}')
    config.add_route('events.delete'  , '/delete/{event_id}')
