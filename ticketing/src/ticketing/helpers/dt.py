import datetime

__all__ = [
    'todatetime',
    'todate'
    ]

def todatetime(d):
    if not isinstance(d, datetime.date):
        raise TypeError()
    return datetime.datetime.fromordinal(d.toordinal())

def todate(d):
    if not isinstance(d, datetime.date):
        raise TypeError()
    if isinstance(d, datetime.datetime):
        return d.date()
    else:
        return d

