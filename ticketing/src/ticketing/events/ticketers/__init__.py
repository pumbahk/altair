 # -*- coding: utf-8 -*-

def includeme(config):
    config.add_route('ticketers.index'   , '/')
    config.add_route('ticketers.new'     , '/new')
    config.add_route('ticketers.show'    , '/show/{event_id}')
    config.add_route('ticketers.edit'    , '/edit/{event_id}')
    config.add_route('ticketers.delete'  , '/delete/{event_id}')