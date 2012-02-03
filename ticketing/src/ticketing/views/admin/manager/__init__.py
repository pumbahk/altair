# -*- coding: utf-8 -*-

def add_routes(config):
    config.add_route('admin.manager.index'          , '/')
    config.add_route('admin.manager.new'            , '/new')
    config.add_route('admin.manager.show'           , '/new')
    config.add_route('admin.manager.edit'           , '/edit')
    config.add_route('admin.manager.edit_multiple'  , '/edit_multiple')

    