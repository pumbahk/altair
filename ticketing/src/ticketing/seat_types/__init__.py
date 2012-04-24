# -*- coding: utf-8 -*-
from ticketing.resources import *

def includeme(config):
    config.add_route('seat_types.show', '/show/{event_id}')
    config.add_route('seat_types.new', '/new/{event_id}')
    config.add_route('seat_types.edit', '/edit/{event_id}/{seat_type_id}')
    config.add_route('seat_types.delete', '/delete/{event_id}/{seat_type_id}')

