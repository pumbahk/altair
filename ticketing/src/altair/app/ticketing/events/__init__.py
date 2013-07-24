# -*- coding: utf-8 -*-

def includeme(config):
    config.add_route('events.index', '/')
    config.add_route('events.new', '/new')
    config.add_route('events.show', '/show/{event_id}')
    config.add_route('events.edit', '/edit/{event_id}')
    config.add_route('events.copy', '/copy/{event_id}')
    config.add_route('events.delete', '/delete/{event_id}')
    config.add_route('events.send', '/send/{event_id}')

    config.include('altair.app.ticketing.events.performances', route_prefix='performances')
    config.include('altair.app.ticketing.events.sales_segment_groups', route_prefix='sales_segment_groups')
    config.include('altair.app.ticketing.events.sales_segments', route_prefix='sales_segments')
    config.include('altair.app.ticketing.events.payment_delivery_method_pairs', route_prefix='payment_delivery_method_pairs')
    config.include('altair.app.ticketing.events.stock_holders', route_prefix='stock_holders')
    config.include('altair.app.ticketing.events.stock_types' , route_prefix='stock_types')
    config.include('altair.app.ticketing.events.stocks' , route_prefix='stocks')
    config.include('altair.app.ticketing.events.tickets', route_prefix='tickets')
    config.include('altair.app.ticketing.events.mailinfo', route_prefix='mailinfo')
    config.include('altair.app.ticketing.events.reports', route_prefix='reports')
    config.include('altair.app.ticketing.events.sales_reports', route_prefix='sales_reports')
    config.include('altair.app.ticketing.events.lots', route_prefix='lots')
    config.scan(".")
