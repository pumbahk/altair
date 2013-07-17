from . import CONFIG_PREFIX
from .interfaces import ITimeZoneInfoProvider
from pyramid.interfaces import IRequest
from pyramid.threadlocal import get_current_request
import time

def get_timezone(request_or_timezone_name, timezone_name=None):
    if IRequest.providedBy(request_or_timezone_name):
        request = request_or_timezone_name
    else:
        if timezone_name is not None:
            raise TypeError('extra argument to get_timezone()?')
        request = get_current_request()
        timezone_name = request_or_timezone_name

    if timezone_name is None:
        timezone_name = request.registry.settings.get(CONFIG_PREFIX + 'timezone', time.tzname[0])

    provider = request.registry.queryUtility(ITimeZoneInfoProvider)
    return provider(timezone_name)
