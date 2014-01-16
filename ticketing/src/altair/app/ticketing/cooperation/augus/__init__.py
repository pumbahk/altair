#-*- coding: utf-8 -*-
from altair.app.ticketing import newRootFactory
from .resources import (
    VenueResource,
    AugusVenueResource,
    AugusVenueListResource,
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
    'augus.venue.index': ('/venues/{venue_id}', VenueResource),
    'augus.venue.download': ('/venues/{venue_id}/download', VenueResource),
    'augus.venue.upload': ('/venues/{venue_id}/upload', VenueResource),
    'augus.augus_venue.index': ('/augus_venues/{augus_venue_code}',
                                AugusVenueListResource),
    #'augus.augus_venue.new': ('/augus_venue/{augus_venue_code}/new', AugusVenueResource),            
    'augus.augus_venue.show': ('/augus_venues/{augus_venue_code}/version/{augus_venue_version}',
                               AugusVenueResource),
    'augus.augus_venue.download': ('/augus_venues/{augus_venue_code}/version/{augus_venue_version}/download',
                                   AugusVenueResource),
    'augus.augus_venue.upload': ('/augus_venues/{augus_venue_code}/version/{augus_venue_version}/upload',
                                 AugusVenueResource),
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
