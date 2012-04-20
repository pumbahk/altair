# -*- coding: utf-8 -*-

def includeme(config):

    config.add_route('bookmark.index'   , '/')
    config.add_route('bookmark.new'     , '/new')
    config.add_route('bookmark.show'    , '/show/{bookmark_id}')
    config.add_route('bookmark.edit'    , '/edit/{bookmark_id}')