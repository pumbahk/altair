# -*- coding: utf-8 -*-
from altair.app.ticketing import newRootFactory
from .resources import (
    AugusAccountResource,
    AugusAccountListResource,
    )

ROUTE_URL_RESOURCE = {
    'augus.accounts.index': ('/', AugusAccountListResource),
    'augus.accounts.create': ('/create', AugusAccountResource),
    'augus.accounts.edit': ('/edit/{augus_account_id}', AugusAccountResource),
    'augus.accounts.show': ('/show/{augus_account_id}', AugusAccountResource),
    'augus.accounts.delete': ('/delete/{augus_account_id}', AugusAccountResource),
    }

def add_routes(config, route_url_resource):
    for route, values in ROUTE_URL_RESOURCE.items():
        url, resource_class = values
        kwds = {}
        if resource_class:
            kwds['factory'] = newRootFactory(resource_class)
        config.add_route(route, url, **kwds)

def includeme(config):
    add_routes(config, ROUTE_URL_RESOURCE)
