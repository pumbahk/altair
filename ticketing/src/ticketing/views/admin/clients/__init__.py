# -*- coding: utf-8 -*-

def add_routes(config):
    config.add_route('admin.clients.index'   , '/')
    config.add_route('admin.clients.new'     , '/new')
    config.add_route('admin.clients.show'    , '/show/{client_id}')
    config.add_route('admin.clients.edit'    , '/edit/{client_id}')

