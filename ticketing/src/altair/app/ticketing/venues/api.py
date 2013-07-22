from .interfaces import IVenueSiteDrawingProviderAdapterFactory

def get_venue_site_adapter(request, site):
    return request.registry.queryAdapter(site, IVenueSiteDrawingProviderAdapterFactory)(request)

