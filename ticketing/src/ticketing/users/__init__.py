# -*- coding: utf-8 -*-

def includeme(config):
    config.add_route('users.index'          , '/')

    config.scan(".")
