from __future__ import absolute_import

from wtforms import fields
from datetime import datetime, date, time
import warnings
from ..utils import atom, days_of_month
from ..widgets.datetime import OurDateTimeWidget, OurDateWidget, OurTimeWidget

__all__ = (
    'Automatic',
    'Max',
    'Min',
    'OurDateTimeFieldBase',
    'OurDateTimeField',
    'OurDateField',
    'OurTimeField',
    'DateTimeField',
    'DateField',
    'TimeField',
    )

Automatic = atom('Automatic')
Max = atom('Max')
Min = atom('Min')

def _raise_undefined_minimum_error(field):
    def _(self, v):
        raise ValueError('minimum value for %s is not defined' % field)
    return _

def _raise_undefined_maximum_error(field):
    def _(self, v):
        raise ValueError('maximum value for %s is not defined' % field)
    return _

class OurDateTimeFieldBase(fields.Field):
    _missing_value_defaults = dict(
        year=u'',
        month=u'1',
        day=u'1',
        hour=u'0',
        minute=u'0',
        second=u'0'
        )

    _min_max = {
        'year': {
            Min: _raise_undefined_minimum_error('year'),
            Max: _raise_undefined_maximum_error('year')
            },
        'month': {
            Min: lambda self, v: 1,
            Max: lambda self, v: 12
            },
        'day': {
            Min: lambda self, v: 1,
            Max: lambda self, v: days_of_month(year=v['year'], month=v['month'])
            },
        'hour': {
            Min: lambda self, v: 0,
            Max: lambda self, v: 23
            },
        'minute': {
            Min: lambda self, v: 0,
            Max: lambda self, v: 59
            },
        'second': {
            Min: lambda self, v: 0,
            Max: lambda self, v: 59
            }
        }

    _raw_data_format = "%(year)04d-%(month)02d-%(day)02d %(hour)02d:%(minute)02d:%(second)02d"

    def __init__(self, _form=None, hide_on_new=False, label=None, validators=None, format='%Y-%m-%d %H:%M:%S', value_defaults=None, missing_value_defaults=None, allow_two_digit_year=True, **kwargs):
        super(OurDateTimeFieldBase, self).__init__(label, validators, **kwargs)
        self.form = _form
        self.hide_on_new = hide_on_new
        self.name_prefix = self.name + u'.'
        self.id_prefix = self.id + u'.'
        self.format = format
        self.value_defaults = value_defaults
        self.missing_value_defaults = missing_value_defaults or dict(self._missing_value_defaults)
        self.allow_two_digit_year = allow_two_digit_year
        self._values = dict((k, u'') for k in self._fields)

    def process_data(self, data):
        pass

    def process_datetime_formdata(self):
        values = dict()
        for k in self._fields:
            try:
                v = self._values[k] or self.missing_value_defaults[k]
                if isinstance(v, basestring):
                    if k == 'year' and self.allow_two_digit_year:
                        if len(v) == 2:
                            v = unicode(date.today().year // 100) + v
                    _v = int(v)
                else:
                    _v = self._min_max[k][v](self, values)
                values[k] = _v
            except ValueError:
                values[k] = None
                self.process_errors.append(self.gettext('Invalid value for %(field)s') % dict(field=self.gettext(k)))
        self.data = self._create_data(values)

    def process(self, formdata, data=fields._unset_value):
        self.process_errors = []
        if data is fields._unset_value:
            try:
                data = self.default()
            except TypeError:
                data = self.default

        self.object_data = data

        try:
            self.process_data(data)
        except ValueError as e:
            self.process_errors.append(e.args[0])

        if formdata:
            self.data = None
            if self.name in formdata:
                value = ' '.join(formdata.getlist(self.name))
                try:
                    self.process_data(datetime.strptime(value, self.format))
                except ValueError as e:
                    # XXX: for now we accept the following format '%Y-%m-%d %H:%M:%s' in addition for compatibility
                    warnings.warn(DeprecationWarning("OurDateTimeField's unwanted feature utilized"))
                    try:
                        self.process_data(datetime.strptime(value, '%Y-%m-%d %H:%M:%S'))
                    except ValueError as e:
                        self.process_errors.append(self.gettext('Not a valid datetime value'))
            else:
                missing_fields = []
                missing_fields_exist_intermittently = False
                for k in self._fields:
                    v = u' '.join(formdata.getlist(self.name_prefix + k)).strip()
                    if not v:
                        missing_fields.append(k)
                        self._values[k] = u''
                    else:
                        self._values[k] = v
                        if missing_fields:
                            for _k in missing_fields:
                                self.process_errors.append(self.gettext("Required field `%(field)s' is not supplied") % dict(field=self.gettext(_k)))
                                missing_fields_exist_intermittently = True
                            missing_fields = []
                if len(missing_fields) == len(self._fields) or \
                   missing_fields_exist_intermittently:
                    self.data = None
                    self.raw_data = None
                else:
                    self.process_datetime_formdata()
                    # XXX: This is needed because "Optional" validator
                    # depends on self.raw_data being set within this method.
                    if self.data is not None:
                        self.raw_data = [
                            # strftime() cannot be used here because
                            # the method doesn't deal with any datetime
                            # before 1900/1/1
                            self._raw_data_format % dict(
                                year=getattr(self.data, 'year', None),
                                month=getattr(self.data, 'month', None),
                                day=getattr(self.data, 'day', None),
                                hour=getattr(self.data, 'hour', None),
                                minute=getattr(self.data, 'minute', None),
                                second=getattr(self.data, 'second', None)
                                )
                            ]
        else:
            try:
                value_defaults = self.value_defaults()
            except TypeError:
                value_defaults = self.value_defaults
            if value_defaults:
                for k in self._fields:
                    self._values[k] = value_defaults.get(k, u'')

        for filter in self.filters:
            try:
                self.data = filter(self.data)
            except ValueError as e:
                self.process_errors.append(e.args[0])

class OurDateTimeField(OurDateTimeFieldBase):
    widget = OurDateTimeWidget()
    _fields = ['year', 'month', 'day', 'hour', 'minute', 'second']

    def process_data(self, data):
        if data is None:
            for k in self._fields:
                self._values[k] = u''
        else:
            if not isinstance(data, datetime):
                raise TypeError()
            for k in self._fields:
                self._values[k] = getattr(data, k) 
        self.data = data

    def _create_data(self, values):
        try:
            return datetime(**values)
        except (TypeError, ValueError):
            self.process_errors.append(self.gettext('Not a valid datetime value'))

    def __call__(self, widget=None, **kwargs):
        if widget is None:
            widget = self.widget
        omit_second = self.format == '%Y-%m-%d %H:%M' # XXX
        return widget(self, omit_second=omit_second, **kwargs)

DateTimeField = OurDateTimeField # for compatibility

class OurDateField(OurDateTimeFieldBase):
    widget = OurDateWidget()
    _fields = ['year', 'month', 'day']

    _raw_data_format = "%(year)04d-%(month)02d-%(day)02d 00:00:00"

    def process_data(self, data):
        if data is None:
            for k in self._fields:
                self._values[k] = u''
        else:
            if isinstance(data, datetime):
                data = data.date()
            elif not isinstance(data, date):
                raise TypeError()
            for k in self._fields:
                self._values[k] = getattr(data, k) 
        self.data = data

    def _create_data(self, values):
        try:
            return date(**values)
        except (TypeError, ValueError):
            self.process_errors.append(self.gettext('Not a valid date value'))

    def __call__(self, widget=None, **kwargs):
        if widget is None:
            widget = self.widget
        return widget(self, **kwargs)

DateField = OurDateField

class OurTimeField(OurDateTimeFieldBase):
    widget = OurTimeWidget()

    _min_max = {
        'hour': {
            Min: _raise_undefined_minimum_error('hour'),
            Max: _raise_undefined_maximum_error('hour')
            },
        'minute': {
            Min: lambda self, v: 0,
            Max: lambda self, v: 59
            },
        'second': {
            Min: lambda self, v: 0,
            Max: lambda self, v: 59
            }
        }

    _fields = ['hour', 'minute', 'second']

    _raw_data_format = "%(hour)02d:%(minute)02d:%(second)02d"

    def process_data(self, data):
        if data is None:
            for k in self._fields:
                self._values[k] = u''
        else:
            if isinstance(data, datetime):
                data = data.date()
            elif not isinstance(data, date):
                raise TypeError()
            for k in self._fields:
                self._values[k] = getattr(data, k) 
        self.data = data

    def _create_data(self, values):
        try:
            return time(**values)
        except (TypeError, ValueError):
            self.process_errors.append(self.gettext('Not a valid time value'))

    def __call__(self, widget=None, **kwargs):
        if widget is None:
            widget = self.widget
        return widget(self, **kwargs)

TimeField = OurTimeField

