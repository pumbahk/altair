# -*- coding: utf-8 -*-

def add_routes(config):
    config.add_route('admin.client.index'   , '/')
    config.add_route('admin.client.new'     , '/new')
    config.add_route('admin.client.show'    , '/show/{client_id}')
    config.add_route('admin.client.edit'    , '/edit/{client_id}')

