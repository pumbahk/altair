# -*- coding: utf-8 -*-

def includeme(config):

    config.add_route('admin.performances.index'            , '/')
    config.add_route('admin.performances.new'              , '/new')
    config.add_route('admin.performances.show'             , '/show/{event_id}')
    config.add_route('admin.performances.edit'             , '/edit/{event_id}')
    config.add_route('admin.performances.edit_multiple'    , '/edit_multiple')
    config.add_route('admin.performances.delete'           , '/delete/{event_id}')


    