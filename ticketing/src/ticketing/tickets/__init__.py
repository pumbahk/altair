# encoding: utf-8

def includeme(config):
    config.add_route('tickets.formats.index', '/formats')
    config.add_route('tickets.formats.new', '/formats/new')
    config.add_route('tickets.formats.show', '/formats/{id}')

    config.add_route('tickets.templates.index', '/templates')
    config.add_route('tickets.templates.new', '/templates/new')

    config.scan('.')
