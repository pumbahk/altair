# -*- coding:utf-8 -*-


def includeme(config):
    config.add_route('word.index', '/', factory='.resources.WordResource')
    config.scan(".")
