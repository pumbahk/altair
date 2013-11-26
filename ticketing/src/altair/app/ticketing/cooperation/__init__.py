# -*- coding: utf-8 -*-

def includeme(config):
    config.add_route('cooperation.index', '/')
    config.add_route('cooperation.show', '/show/{venue_id}')
    config.add_route('cooperation.upload', '/upload/{venue_id}')
    config.add_route('cooperation.download', '/download/{venue_id}')
    config.scan('.')
    
    
