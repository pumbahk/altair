from .interfaces import IVenueSiteDrawingProviderAdapterFactory
from datetime import datetime

from . import VISIBLE_VENUES_SESSION_KEY

def set_visible_venue(request):
    request.session[VISIBLE_VENUES_SESSION_KEY] = str(datetime.now())

def set_invisible_venue(request):
    del request.session[VISIBLE_VENUES_SESSION_KEY]

def get_venue_site_adapter(request, site):
    return request.registry.queryAdapter(site, IVenueSiteDrawingProviderAdapterFactory)(request)

