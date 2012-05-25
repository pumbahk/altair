# -*- coding: utf-8 -*-

def includeme(config):
    config.add_route('events.index', '/')
    config.add_route('events.new', '/new')
    config.add_route('events.show', '/show/{event_id}')
    config.add_route('events.edit', '/edit/{event_id}')
    config.add_route('events.delete', '/delete/{event_id}')
    config.add_route('events.sync', '/sync/{event_id}')

    config.include('ticketing.events.performances', route_prefix='performances')
    config.include('ticketing.events.sales_segments', route_prefix='sales_segments')
    config.include('ticketing.events.payment_delivery_method_pair', route_prefix='payment_delivery_method_pair')
    config.include('ticketing.events.stock_holders', route_prefix='stock_holders')
    config.include('ticketing.events.stock_types' , route_prefix='stock_types')
