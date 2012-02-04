# -*- coding: utf-8 -*-

def add_routes(config):
    config.add_route('admin.operator_roles.index'          , '/roles')
    config.add_route('admin.operator_roles.new'            , '/roles/new')
    config.add_route('admin.operator_roles.show'           , '/roles/show/{operator_role_id}')
    config.add_route('admin.operator_roles.edit'           , '/roles/edit/{operator_role_id}')
    config.add_route('admin.operator_roles.edit_multiple'  , '/roles/edit_multiple')

    