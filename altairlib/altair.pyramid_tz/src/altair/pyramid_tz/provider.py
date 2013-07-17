from zope.interface import implementer
from .interfaces import ITimeZoneInfoProvider

__all__ = [
    'PyTZTimeZoneInfoProvider',
    ]

reverse_map = None

def _populate_reverse_map():
    import pytz
    from datetime import datetime
    if reverse_map is not None:
        return

    _reverse_map = {}
    ambiguous = datetime(1970, 1, 1, 0, 0, 0)
    for name in pytz.all_timezones:
        tzinfo = pytz.timezone(name)
        try:
            _reverse_map[tzinfo.tzname(ambiguous, False)] = name
            _reverse_map[tzinfo.tzname(ambiguous, True)] = name
        except TypeError:
            pass

    global reverse_map
    reverse_map = _reverse_map
    

def tzname_to_name(tzname):
    _populate_reverse_map()
    return reverse_map[tzname]

@implementer(ITimeZoneInfoProvider)
class PyTZTimeZoneInfoProvider(object):
    def __call__(self, timezone_name):
        import pytz
        try:
            return pytz.timezone(timezone_name)
        except:
            _populate_reverse_map()
            timezone_name = reverse_map[timezone_name]
            return pytz.timezone(timezone_name)
