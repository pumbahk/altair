CONFIG_PREFIX = __name__ + "."

def includeme(config):
    from interfaces import ITimeZoneInfoProvider
    from provider import PyTZTimeZoneInfoProvider
    config.registry.registerUtility(PyTZTimeZoneInfoProvider(), ITimeZoneInfoProvider)
