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
    'augus.augus_venue.complete': ('/augus_venues/{augus_venue_code}/version/{augus_venue_version}/complete',
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

    # putback
    'augus.putback.index': ('/events/{event_id}/putback', PerformanceResource),
    'augus.putback.new': ('/events/{event_id}/putback/new', PerformanceResource),
    'augus.putback.show': ('/events/{event_id}/putback/show/{putback_code}', PerformanceResource),
    'augus.putback.reserve': ('/events/{event_id}/putback/reserve/{putback_code}', PerformanceResource),

    # achievement
    'augus.achievement.get': ('/events/{event_id}/achievement', PerformanceResource),
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
