# -*- coding: utf-8 -*-

def includeme(config):

    config.add_route('organizations.index'   , '/')
    config.add_route('organizations.new'     , '/new')
    config.add_route('organizations.show'    , '/show/{organization_id}')
    config.add_route('organizations.edit'    , '/edit/{organization_id}')
