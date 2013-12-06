# -*- coding: utf-8 -*-
from altair.app.ticketing import newRootFactory
from .resources import CooperationResource

ROUTE_URL_RESOURCE = {
    'cooperation.index': ('/', None),
    'cooperation.show': ('/show/{venue_id}', None),
    'cooperation.upload': ('/upload/{venue_id}', CooperationResource),
    'cooperation.download': ('/download/{venue_id}', CooperationResource),
    }


def includeme(config):
    for route, values in ROUTE_URL_RESOURCE.items():
        url, resource_class = values
        kwds = {}
        if resource_class:
            kwds['factory'] = newRootFactory(resource_class)
        config.add_route(route, url, **kwds)
    config.scan('.')
