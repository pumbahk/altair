from pyramid.interfaces import IRequest
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

def includeme(config):
    config.add_route("venues.index", "/")
    config.add_route("venues.new", '/new')
    config.add_route("venues.edit", "/edit/{venue_id}")
    config.add_route("venues.show", "/show/{venue_id}")
    config.add_route("venues.checker", "/{venue_id}/checker")
    config.add_route("api.get_site_drawing", "/api/drawing/{site_id}")
    config.add_route("api.get_seats", "/{venue_id}/seats/")
    config.add_route("api.get_frontend", "/{venue_id}/frontend/{part}")
    config.add_route("seats.download", "/download/{venue_id}")
    config.registry.registerAdapter(
        new_venue_site_provider_factory_factory(config),
        (ITentativeVenueSite, ),
        IVenueSiteDrawingProviderAdapterFactory
        )
    config.scan(".")
