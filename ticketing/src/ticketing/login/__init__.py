# -*- coding: utf-8 -*-

def includeme(config):
    config.add_route('login.index'                  , '/')
    config.add_route('login.info'                   , '/info')
    config.add_route('login.info.edit'              , '/info/edit')
    config.add_route('login.logout'                 , '/logout')
    config.add_route('login.reset'                  , '/reset')
    config.add_route('login.reset.complete'         , '/reset/complete')
    config.scan(".")
