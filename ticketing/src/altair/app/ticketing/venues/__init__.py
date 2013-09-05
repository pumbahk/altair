# -*- coding: utf-8 -*-

from pyramid.interfaces import IRequest

from altair.app.ticketing import newRootFactory
from .interfaces import IVenueSiteDrawingProviderAdapterFactory, ITentativeVenueSite
from .adapters import VenueSiteDrawingProviderAdapterFactory

def new_venue_site_provider_factory_factory(config):
    frontend_metadata_base_url = config.registry.settings.get(
        'altair.site_data.frontend_base_url',
        config.registry.settings.get('altair.site_data.base_url', '')
        )
    backend_metadata_base_url = config.registry.settings.get(
        'altair.site_data.backend_base_url',
        config.registry.settings.get('altair.site_data.base_url', '') + '../backend/'
        )

    factory = VenueSiteDrawingProviderAdapterFactory(
        frontend_metadata_base_url,
        backend_metadata_base_url
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

def includeme(config):
    from .resources import VenueAdminResource
    factory = newRootFactory(VenueAdminResource)
    config.add_route("venues.index", "/", factory=factory)
    config.add_route("venues.new", '/new', factory=factory)
    config.add_route("venues.edit", "/edit/{venue_id}", factory=factory)
    config.add_route("venues.show", "/show/{venue_id}", factory=factory)
    config.add_route("venues.checker", "/{venue_id}/checker", factory=factory)
    config.add_route("api.get_site_drawing", "/api/drawing/{site_id}", factory=factory)
    config.add_route("api.get_seats", "/{venue_id}/seats/", factory=factory)
    config.add_route("api.get_frontend", "/{venue_id}/frontend/{part}", factory=factory)
    config.add_route("seats.download", "/download/{venue_id}", factory=factory)
    config.include(setup_components)
    config.scan(".")
