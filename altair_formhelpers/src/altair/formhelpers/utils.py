from datetime import date, timedelta

__all__ = (
    'days_of_month',
    'atom',
    )

def atom(name):
    return type(name, (object,), dict(__str__=lambda self:name, __repr__=lambda self:'%s()' % name))

def days_of_month(year, month):
    return ((date(year, month, 1) + timedelta(31)).replace(day=1) - timedelta(1)).day
