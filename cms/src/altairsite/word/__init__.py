# -*- coding:utf-8 -*-

def includeme(config):
    config.add_route('api.word.get', '/word/')
    config.scan(".views")
