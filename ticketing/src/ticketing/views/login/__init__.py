# -*- coding: utf-8 -*-
from ticketing.resources import *

def add_routes(config):
    config.add_route('login.index'                  , '/')
    config.add_route('login.info'                   , '/info')
    config.add_route('login.info.edit'                   , '/info/edit')
    config.add_route('login.logout'                 , '/logout')


