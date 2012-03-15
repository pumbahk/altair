# -*- coding: utf-8 -*-

def add_routes(config):

    config.add_route('admin.index'            , '/')
    config.include('ticketing.views.admin.clients.add_routes'           , route_prefix='/clients')
    config.include('ticketing.views.admin.performances.add_routes'      , route_prefix='/performance')
    #config.include('ticketing.views.admin.operators.add_routes'         , route_prefix='/operators')
    config.include('ticketing.views.admin.operator_roles.add_routes'    , route_prefix='/operators/role')
    config.include('ticketing.views.admin.user.add_routes'              , route_prefix='/user')
