# -*- coding: utf-8 -*-

def includeme(config):
    config.add_route('reports.index', '/{event_id}')
    config.add_route('reports.sales', '/{event_id}/sales')
    config.add_route('reports.seat_stocks', '/{event_id}/seat_stocks')
    config.add_route('reports.seat_stock_to_stockholder', '/{event_id}/seat_stock_to_stockholder/{stock_holder_id}')
    config.add_route('reports.seat_unsold', '/{event_id}/seat_unsold')
