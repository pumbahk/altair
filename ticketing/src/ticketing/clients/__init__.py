# -*- coding: utf-8 -*-

def includeme(config):

    config.add_route('clients.index'   , '/')
    config.add_route('clients.new'     , '/new')
    config.add_route('clients.show'    , '/show/{client_id}')
    config.add_route('clients.edit'    , '/edit/{client_id}')
