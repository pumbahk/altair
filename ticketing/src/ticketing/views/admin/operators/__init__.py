# -*- coding: utf-8 -*-

def add_routes(config):
    config.add_route('admin.operators.index'          , '/')
    config.add_route('admin.operators.new'            , '/new')
    config.add_route('admin.operators.show'           , '/show/{operator_id}')
    config.add_route('admin.operators.edit'           , '/edit/{operator_id}')
    config.add_route('admin.operators.edit_multiple'  , '/edit_multiple')

    