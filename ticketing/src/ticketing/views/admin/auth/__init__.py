# -*- coding: utf-8 -*-

def add_routes(config):
    config.add_route('admin.auth.index'   , '/')
    config.add_route('admin.auth.new'     , '/new')
    config.add_route('admin.auth.show'    , '/show/{client_id}')
    config.add_route('admin.auth.edit'    , '/edit/{client_id}')

