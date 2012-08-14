# encoding: utf-8

def includeme(config):
    config.add_route('tickets.formats.index', '/formats')
    config.add_route('tickets.formats.new', '/formats/new')
    config.add_route('tickets.formats.show', '/formats/{id}')
    config.add_route('tickets.formats.edit', '/formats/{id}/edit')
    config.add_route('tickets.formats.delete', '/formats/{id}/delete')

    config.add_route('tickets.templates.index', '/templates')
    config.add_route('tickets.templates.new', '/templates/new')
    config.add_route('tickets.templates.show', '/templates/{id}')
    config.add_route('tickets.templates.edit', '/templates/{id}/edit')
    config.add_route('tickets.templates.delete', '/templates/{id}/delete')

    config.scan('.views')
