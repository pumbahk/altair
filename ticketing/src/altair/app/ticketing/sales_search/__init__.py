# -*- coding: utf-8 -*-


def includeme(config):
    config.add_route('sales_search.index', '/', factory='.resources.SalesSearchResource')
    config.add_route('sales_search.search', '/search', factory='.resources.SalesSearchResource')
    config.add_route('sales_search.download', '/download', factory='.resources.SalesSearchResource')
    config.scan(".")
