# coding: utf-8

def includeme(config):
    config.add_route('layout_demo', '/demo/layout/')
    config.scan(".views")
