# -*- coding: utf-8 -*-

def includeme(config):
    config.add_route('reports.index', '/{event_id}/')
    config.add_route('reports.sales', '/{event_id}/sales')
    config.add_route('reports.stocks', '/{event_id}/stocks')
    config.add_route('reports.stocks_by_stockholder', '/{event_id}/stocks_by_stockholder')
