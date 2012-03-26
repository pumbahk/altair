# -*- coding: utf-8 -*-

def includeme(config):

    config.add_route('admin.index'            , '/')

    config.include('ticketing.admin.performances'      , route_prefix='/performance')
    config.include('ticketing.admin.user'              , route_prefix='/user')
