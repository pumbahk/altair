# -*- coding: utf-8 -*-

def includeme(config):
    config.add_route('events.index', '/')
    config.add_route('events.new', '/new')
    config.add_route('events.show', '/show/{event_id}')
    config.add_route('events.edit', '/edit/{event_id}')
    config.add_route('events.delete', '/delete/{event_id}')

    config.add_route('performances.index', '/{event_id}/performances')
    config.add_route('performances.new', '/{event_id}/performances/new')
    config.include('ticketing.events.performances', route_prefix='performances')

    config.add_route('sales_segments.index', '/{event_id}/sales_segments')
    config.include('ticketing.events.sales_segments', route_prefix='sales_segments')

    config.add_route('products.index', '/{event_id}/products')

    config.include('ticketing.events.payment_delivery_method_pair', route_prefix='payment_delivery_method_pair')
