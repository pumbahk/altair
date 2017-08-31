# -*- coding: utf-8 -*-

def includeme(config):
    from .resources import ReportAdminResource
    config.add_route('reports.index', '/{event_id}/', factory=ReportAdminResource)
    config.add_route('reports.sales', '/{event_id}/sales', factory=ReportAdminResource)
    config.add_route('reports.stocks', '/{event_id}/stocks', factory=ReportAdminResource)
    config.add_route('reports.stocks_by_stockholder', '/{event_id}/stocks_by_stockholder', factory=ReportAdminResource)
