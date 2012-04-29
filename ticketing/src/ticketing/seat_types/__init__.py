# -*- coding: utf-8 -*-
from ticketing.resources import *

def includeme(config):
    config.add_route('seat_types.show', '/show/{performance_id}')
    config.add_route('seat_types.new', '/new/{performance_id}')
    config.add_route('seat_types.edit', '/edit/{seat_type_id}')
    config.add_route('seat_types.delete', '/delete/{seat_type_id}')
