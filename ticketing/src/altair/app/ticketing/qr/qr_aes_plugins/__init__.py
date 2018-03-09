# encoding: utf-8

def includeme(config):
    config.include('.ht')
    config.include('.bw')
    config.scan(__name__)