# encoding: utf-8

def includeme(config):
    config.add_route('tickets.index', '/')
    config.add_route('tickets.formats.new', '/formats/new')
    config.add_route('tickets.formats.show', '/formats/{id}')
    config.add_route('tickets.formats.edit', '/formats/{id}/edit')
    config.add_route('tickets.formats.delete', '/formats/{id}/delete')
    config.add_route('tickets.formats.data', '/formats/{id}/data')

    config.add_route('tickets.templates.new', '/templates/new', factory=".resources.TicketsResource")
    config.add_route('tickets.templates.show', '/templates/{id}', factory=".resources.TicketsResource")
    config.add_route('tickets.templates.edit', '/templates/{id}/edit', factory=".resources.TicketsResource")
    config.add_route('tickets.templates.download', '/templates/{id}/download', factory=".resources.TicketsResource")
    config.add_route('tickets.templates.delete', '/templates/{id}/delete', factory=".resources.TicketsResource")
    config.add_route('tickets.templates.data', '/templates/{id}/data', factory=".resources.TicketsResource")

    config.add_route('tickets.printer', '/print/printer')
    config.add_route('tickets.print.dequeue', '/print/dequeue')

    ## events.tickets.templatesもview`configに含まれている
    config.scan('.views')
