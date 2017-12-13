# -*- coding: utf-8 -*-

AES_SECRET_KEY="THIS_IS_SECRET_KEY_FOR_ALTAIR!!!"

def includeme(config):
    config.add_route('login.default'                , '/')
    config.add_route('login.client_cert'            , '/client_cert')
    config.add_route('login.info'                   , '/info')
    config.add_route('login.info.edit'              , '/info/edit')
    config.add_route('login.logout'                 , '/logout')
    config.add_route('login.reset'                  , '/reset')
    config.add_route('login.reset.complete'         , '/reset/complete')
    config.scan(".")
