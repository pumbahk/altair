# -*- coding: utf-8 -*-
from .resources import APIContext

def includeme(config):
    config.add_route('api.access_token'            , '/access_token')
    config.add_route('api.forget_loggedin'       , '/forget_loggedin' )

    config.add_route('login.authorize'              , '/authorize')
    config.add_route('login.access_token'           , '/access_token')
    config.add_route('login.missing_redirect_url'   , '/missing_redirect_url')

    config.add_route('api.stock_statuses_for_event', '/events/{event_id}/stock_statuses', factory=APIContext)
    config.scan(".")
