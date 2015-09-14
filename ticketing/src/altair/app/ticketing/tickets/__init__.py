# -*- coding:utf-8 -*-

def setup_svg(config):
    from .interfaces import ISVGBuilder
    from .svg_builder import TicketModelControl
    from .svg_builder import SVGBuilder
    import pystache
    builder = SVGBuilder(TicketModelControl(), renderer=pystache)
    config.registry.registerUtility(builder, ISVGBuilder)

def includeme(config):
    config.include(setup_svg)
    config.add_route('tickets.index', '/')

    config.add_route('tickets.ticketformats.new', '/ticketformats/new')
    config.add_route('tickets.ticketformats.show', '/ticketformats/{id}')
    config.add_route('tickets.ticketformats.edit', '/ticketformats/{id}/edit')
    config.add_route('tickets.ticketformats.delete', '/ticketformats/{id}/delete')
    config.add_route('tickets.ticketformats.data', '/ticketformats/{id}/data')

    config.add_route('tickets.pageformats.new', '/pageformats/new')
    config.add_route('tickets.pageformats.show', '/pageformats/{id}')
    config.add_route('tickets.pageformats.edit', '/pageformats/{id}/edit')
    config.add_route('tickets.pageformats.delete', '/pageformats/{id}/delete')
    config.add_route('tickets.pageformats.data', '/pageformats/{id}/data')

    config.add_route('tickets.templates.new', '/templates/new', factory=".resources.TicketsResource")
    config.add_route('tickets.templates.show', '/templates/{id}', factory=".resources.TicketsResource")
    config.add_route('tickets.templates.edit', '/templates/{id}/edit', factory=".resources.TicketsResource")
    config.add_route('tickets.templates.download', '/templates/{id}/download', factory=".resources.TicketsResource")
    config.add_route('tickets.templates.delete', '/templates/{id}/delete', factory=".resources.TicketsResource")
    config.add_route('tickets.templates.data', '/templates/{id}/data', factory=".resources.TicketsResource")
    config.add_route('tickets.templates.update_derivatives', '/templates/{id}/update_derivatives')

    config.add_route('tickets.covers.new', '/covers/new')
    config.add_route('tickets.covers.show', '/covers/{id}')
    config.add_route('tickets.covers.edit', '/covers/{id}/edit')
    config.add_route('tickets.covers.delete', '/covers/{id}/delete')

    config.add_route('tickets.queue.index', '/queue', factory=".resources.TicketsResource")
    config.add_route('tickets.queue.delete', '/queue/delete', factory=".resources.TicketsResource")
    config.add_route('tickets.queue.mask', '/queue/mask', factory=".resources.TicketsResource")
    config.add_route('tickets.queue.unmask', '/queue/unmask', factory=".resources.TicketsResource")

    config.add_route('tickets.printer', '/print/printer')
    config.add_route('tickets.printer2', '/print/printer2')
    config.add_route('tickets.printer3', '/print/printer3')
    config.add_route('tickets.printer.api.formats', '/print/formats')
    config.add_route('tickets.printer.api.enqueue', '/print/enqueue')
    config.add_route('tickets.printer.api.ticket', '/print/ticket/{event_id}/{id:.*}')
    config.add_route('tickets.printer.api.ticket_data', '/print/ticket_data')
    config.add_route('tickets.printer.api.history', '/print/history')
    config.add_route('tickets.printer.api.peek', '/print/peek')
    config.add_route('tickets.printer.api.dequeue', '/print/dequeue')
    config.add_route('tickets.printer.api.list', '/print/list')
    config.add_route('tickets.printer.api.mask', '/print/mask')
    config.add_route('tickets.printer.api.unmask', '/print/unmask')
    config.add_route('tickets.printer.api.delete', '/print/delete')

    config.scan('.views')
    config.include(".preview")
