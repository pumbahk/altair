# -*- coding: utf-8 -*-
from altair.app.ticketing import newRootFactory
from altair.app.ticketing.venues.resources import VenueAdminResource
from .resources import CooperationResource

ROUTE_URL_RESOURCE = {
    # cooperation events
    'cooperation.events': ('/events/{event_id}', None),
    # cooperation performance web api
    'cooperation.api.performances.get': ('/api/events/{event_id}/performances', None),
    'cooperation.api.performances.save': ('/api/events/{event_id}/performances', None),
    # cooperation venue    
    'cooperation.show': ('/show/{venue_id}', VenueAdminResource),
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
