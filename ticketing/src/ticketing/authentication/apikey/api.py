from zope.interface.verify import verifyObject
from .interfaces import IAPIKeyEntry
API_ENTRY_ATTR = '_altair_apikeyentry'

def get_apikeyentry(request):
    """Retrieves the IAPIKeyEntry object from the API-authenticated request. Returns None if the request is not authenticated"""
    return getattr(request, API_ENTRY_ATTR, None)

def set_apikeyentry(request, apikeyentry):
    """Associates the IAPIKeyEntryObject to the request"""
    assert apikeyentry is None or verifyObject(IAPIKeyEntry, apikeyentry)
    if apikeyentry is None and hasattr(request, API_ENTRY_ATTR):
        delattr(request, API_ENTRY_ATTR)
    else:
        setattr(request, API_ENTRY_ATTR, apikeyentry)
