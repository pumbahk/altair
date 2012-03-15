# -*- coding: utf-8 -*-
from ticketing.resources import *

def add_routes(config):
    config.add_route('login.index'                  , '/')
    config.add_route('login.info'                   , '/info')
    config.add_route('login.info.edit'                   , '/info/edit')
    config.add_route('login.logout'                 , '/logout')

    config.add_route('login.authorize'                 , '/authorize')
    config.add_route('login.access_token'              , '/access_token')
    config.add_route('login.missing_redirect_url'      , '/missing_redirect_url')





