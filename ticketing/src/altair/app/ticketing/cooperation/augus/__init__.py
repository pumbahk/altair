#-*- coding: utf-8 -*-
from altair.app.ticketing import newRootFactory
from .resources import (
    VenueResource,
    AugusVenueResource,
    AugusVenueListResource,
    PerformanceResource,
    SeatTypeResource,
    )

ROUTE_URL_RESOURCE = {
    'augus.test': ('/test', None),
    'augus.venue.index': ('/venues/{venue_id}', VenueResource),
    'augus.venue.download': ('/venues/{venue_id}/download', VenueResource),
    'augus.venue.upload': ('/venues/{venue_id}/upload', VenueResource),
    'augus.augus_venue.index': ('/augus_venues/{augus_venue_code}',
                                AugusVenueListResource),
    'augus.augus_venue.show': ('/augus_venues/{augus_venue_code}/version/{augus_venue_version}',
                               AugusVenueResource),
    'augus.augus_venue.download': ('/augus_venues/{augus_venue_code}/version/{augus_venue_version}/download',
                                   AugusVenueResource),
    'augus.augus_venue.upload': ('/augus_venues/{augus_venue_code}/version/{augus_venue_version}/upload',
                                 AugusVenueResource),

    # event
    'augus.event.show': ('/events/{event_id}', PerformanceResource),
    # performance
    'augus.performance.index': ('/events/{event_id}/performances', PerformanceResource),
    'augus.performance.show': ('/events/{event_id}/performances/show', PerformanceResource),
    'augus.performance.edit': ('/events/{event_id}/performances/edit', PerformanceResource),
    'augus.performance.save': ('/events/{event_id}/performances/save', PerformanceResource),

    # stock type
    'augus.stock_type.index': ('/events/{event_id}/stock_types', SeatTypeResource),
    'augus.stock_type.show': ('/events/{event_id}/stock_types/show', SeatTypeResource),
    'augus.stock_type.edit': ('/events/{event_id}/stock_types/edit', SeatTypeResource),
    'augus.stock_type.save': ('/events/{event_id}/stock_types/save', SeatTypeResource),
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
