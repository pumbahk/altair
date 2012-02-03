# -*- coding: utf-8 -*-

def add_routes(config):
    config.include('ticketing.views.admin.client.add_routes'  , route_prefix='/client')
    config.include('ticketing.views.admin.event.add_routes'   , route_prefix='/event')
    config.include('ticketing.views.admin.manager.add_routes' , route_prefix='/manager')
    config.include('ticketing.views.admin.user.add_routes'    , route_prefix='/user')