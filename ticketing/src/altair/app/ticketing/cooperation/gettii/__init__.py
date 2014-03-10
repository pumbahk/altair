#-*- coding: utf-8 -*-
from altair.app.ticketing.cooperation.utils import add_routes

ROUTE_URL_RESOURCE = {
    # venue
    'gettii.venue.index': ('/venues/{venue_id}', None),
    'gettii.venue.download': ('/venues/{venue_id}/download', None),
    'gettii.venue.upload': ('/venues/{venue_id}/upload', None),
    }


def includeme(config):
    add_routes(config, ROUTE_URL_RESOURCE)
