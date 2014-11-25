# encoding: utf-8

from __future__ import absolute_import

import re
from wtforms import validators
from datetime import date, datetime

__all__ = (
    'DateTimeInRange',
    'DateTimeFormat',
    'after1900',
    )

def todatetime(d):
    if not isinstance(d, date):
        raise TypeError()
    if isinstance(d, datetime):
        return d
    else:
        return datetime.fromordinal(d.toordinal())

class DateTimeFormat(object):
    def __init__(self, message=u''):
        self.message = message

    def __call__(self, form, field):
        try:
            data = todatetime(field.data)
        except:
            if not field.errors and not self.message: # input data is emputy
                message = field.gettext('This field is required.')
            else:
                message = self.message
            raise validators.ValidationError(message)

class DateTimeInRange(object):
    def __init__(self, from_=None, to=None):
        self.from_ = from_ and todatetime(from_)
        self.to = to and todatetime(to)

    def format_datetime(self, field, date, type_):
        if hasattr(field._translations, 'format_datetime'):
            if type_ == datetime:
                return field._translations.format_datetime(date)
            else:
                return field._translations.format_date(date)
        else:
            if type_ == datetime:
                return date.strftime("%Y-%m-%d %H:%M:%S")
            else:
                return date.strftime("%Y-%m-%d")

    def __call__(self, form, field):
        if field.data is None:
            return
        data = todatetime(field.data)
        if self.from_ is not None and self.from_ > data:
            raise ValueError(field.gettext(u'Field must be a date/time after or equal to %(datetime)s') % dict(field=field.label, datetime=self.format_datetime(field, self.from_, field.data.__class__)))
        if self.to is not None and self.to <= data:
            raise ValueError(field.gettext(u'Field must be a date/time before %(datetime)s') % dict(field=field.label, datetime=self.format_datetime(field, self.to, field.data.__class__)))

after1900 = DateTimeInRange(from_=date(1900, 1, 1))

