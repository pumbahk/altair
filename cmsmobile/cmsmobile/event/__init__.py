# -*- coding: utf-8 -*-
from ticketing.resources import *

def includeme(config):
    config.add_route('search', '/search')
    config.add_route('genre', '/genre')
    config.add_route('detail', '/detail')
    config.add_route('inquiry', '/inquiry')
    config.add_route('help', '/help')
    config.add_route('order', '/order')
