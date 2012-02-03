# -*- coding: utf-8 -*-

def add_routes(config):
    config.include('ticketing.views.admin.clients.add_routes'  , route_prefix='/client')
    config.include('ticketing.views.admin.events.add_routes'   , route_prefix='/events')
    config.include('ticketing.views.admin.performances.add_routes'   , route_prefix='/performance')
    config.include('ticketing.views.admin.manager.add_routes' , route_prefix='/manager')
    config.include('ticketing.views.admin.user.add_routes'    , route_prefix='/user')