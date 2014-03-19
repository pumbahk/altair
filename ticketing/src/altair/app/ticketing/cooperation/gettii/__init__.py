#-*- coding: utf-8 -*-
from altair.app.ticketing.cooperation.utils import add_routes
from .resources import (
    VenueResource,
    )

ROUTE_URL_RESOURCE = {
    # venue
    'gettii.venue.index': ('/venues/{venue_id}', VenueResource),
    'gettii.venue.download': ('/venues/{venue_id}/download', VenueResource),
    'gettii.venue.upload': ('/venues/{venue_id}/upload', VenueResource),
    # test
    'gettii.test.index': ('/test', None),
    }


def includeme(config):
    add_routes(config, ROUTE_URL_RESOURCE)
