# -*- coding: utf-8 -*-

QR_CHARACTERS = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
QR_STR_PREFIX = 'TS'
QR_STR_LENGTH = 20


def includeme(config):
    config.add_route('skidata.property.show', '/property')
    config.add_route('skidata.property.new', '/property/{prop_type}/new')
    config.add_route('skidata.property.edit', '/property/{id}/edit')
    config.add_route('skidata.property.delete', '/property/{id}/delete')
    config.scan(".")
