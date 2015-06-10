# -*- coding: utf-8 -*-

from pyramid.interfaces import IRequest
from pyramid.settings import asbool
from altair.app.ticketing import newRootFactory
from .interfaces import IVenueSiteDrawingProviderAdapterFactory, ITentativeVenueSite
from .adapters import VenueSiteDrawingProviderAdapterFactory

VISIBLE_VENUES_SESSION_KEY = '_visible_venues'

def new_venue_site_provider_factory_factory(config):
    frontend_metadata_base_url = config.registry.settings.get(
        'altair.site_data.frontend_base_url',
        config.registry.settings.get('altair.site_data.base_url', '')
        )
    backend_metadata_base_url = config.registry.settings.get(
        'altair.site_data.backend_base_url',
        config.registry.settings.get('altair.site_data.base_url', '') + '../backend/'
        )
    force_indirect_serving = asbool(config.registry.settings.get(
        'altair.site_data.force_indirect_serving', 'false'))

    factory = VenueSiteDrawingProviderAdapterFactory(
        frontend_metadata_base_url,
        backend_metadata_base_url,
        force_indirect_serving
        )
    def factory_factory(site):
        def _(request):
            return factory(request, site) 
        return _
    return factory_factory

def setup_components(config):
    config.registry.registerAdapter(
        new_venue_site_provider_factory_factory(config),
        (ITentativeVenueSite, ),
        IVenueSiteDrawingProviderAdapterFactory
        )
    config.include('.views')

def includeme(config):
    from .resources import VenueAdminResource
    factory = newRootFactory(VenueAdminResource)
    config.add_route("venues.index", "/", factory=factory)
    config.add_route("venues.new", '/new', factory=factory)
    config.add_route("venues.edit", "/edit/{venue_id}", factory=factory)
    config.add_route("venues.show", "/show/{venue_id}", factory=factory)
    config.add_route("venues.show._seat_adjacency_counts", "/show/{venue_id}/_seat_adjacency_counts", factory=factory)
    config.add_route("venues.checker", "/{venue_id}/checker", factory=factory)
    config.add_route("venues.visible", "/visible", factory=factory)
    config.add_route("venues.invisible", "/invisible", factory=factory)
    config.add_route("api.get_site_drawing", "/api/drawing/{site_id}", factory=factory)
    config.add_route("api.seat_info", "/{venue_id}/seat_info/", factory=factory)
    config.add_route("api.seat_priority", "/{venue_id}/seat_priority/", factory=factory)
    config.add_route("api.group", "/{venue_id}/group/", factory=factory)
    config.add_route("api.get_seats", "/{venue_id}/seats/", factory=factory)
    config.add_route("api.get_frontend", "/{venue_id}/frontend/{part}", factory=factory)
    config.add_route("seats.download", "/download/{venue_id}", factory=factory)
    config.include(setup_components)
    config.scan(".")
