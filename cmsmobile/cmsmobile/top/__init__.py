# -*- coding: utf-8 -*-
from ticketing.resources import *

def includeme(config):
    config.add_route('top.search', '/search')
    config.add_route('top.genre', '/genre')
    config.add_route('top.detail', '/detail/')
