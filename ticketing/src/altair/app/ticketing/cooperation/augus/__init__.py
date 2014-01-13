#-*- coding: utf-8 -*-
from altair.app.ticketing import newRootFactory
from .resources import (
    AugusVenueResource,
    )

# /cooperation/augus/event/event_id
# /cooperation/augus/event/event_id/performances
# /cooperation/augus/event/event_id/seat_types
# /cooperation/augus/event/event_id/distribution
# /cooperation/augus/event/event_id/putback
# /cooperation/augus/event/event_id/reverse
# /cooperation/augus/venue/venue_id
# /cooperation/augus/venue/venue_id/download
# /cooperation/augus/venue/venue_id/upload

ROUTE_URL_RESOURCE = {
    'augus.test': ('/test', None),
    'augus.venue.index': ('/venue/{venue_id}', AugusVenueResource),
    'augus.venue.download': ('/venue/{venue_id}/download', AugusVenueResource),
    'augus.venue.upload': ('/venue/{venue_id}/upload', AugusVenueResource),
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


    
    
