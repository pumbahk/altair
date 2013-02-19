import datetime

__all__ = [
    'todatetime',
    ]

def todatetime(d):
    if not isinstance(d, datetime.date):
        raise TypeError()
    return datetime.datetime.fromordinal(d.toordinal())
