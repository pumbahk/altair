# -*- coding: utf-8 -*-
from altair.app.ticketing import newRootFactory
from altair.app.ticketing.venues.resources import VenueAdminResource
from .resources import CooperationResource

ROUTE_URL_RESOURCE = {
    # converter
    'cooperation.convert2altair': ('/convert2altair/{performance_id}', None),
    # cooperation events
    'cooperation2.events': ('/events/{event_id}', None),
    # cooperation performance web api
    'cooperation2.api.performances': ('/api/events/{event_id}/performances', None),
    # cooperation venue
    'cooperation2.show': ('/show/{venue_id}', VenueAdminResource),
    'cooperation2.upload': ('/upload/{venue_id}', CooperationResource),
    'cooperation2.download': ('/download/{venue_id}', CooperationResource),
    #
    'cooperation2.distribution': ('/event/{event_id}/distribution', None),
    'cooperation2.putback': ('/event/{event_id}/putback', None),
    'cooperation2.achievement': ('/event/{event_id}/achievement', None),
    }


def includeme(config):
    for route, values in ROUTE_URL_RESOURCE.items():
        url, resource_class = values
        kwds = {}
        if resource_class:
            kwds['factory'] = newRootFactory(resource_class)
        config.add_route(route, url, **kwds)
    config.include('altair.app.ticketing.cooperation.augus', route_prefix='augus')
    config.include('altair.app.ticketing.cooperation.gettii', route_prefix='gettii')
    config.scan('.')
