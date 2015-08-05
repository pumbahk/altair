# encoding: utf-8
from __future__ import absolute_import
import sys
import re
import io
import csv
import decimal
from collections import namedtuple
from datetime import date, time, datetime, timedelta
import six
from zope.interface import implementer
from altair.timeparse import parse_duration, build_duration
from altair.jis.sjis import sjis_iterator, multibyte_in_sjis, len_in_sjis
from ..utils import hankaku2zenkaku
from .interfaces import ITabularDataColumn, ITabularDataColumnSpecification, ITabularDataMarshaller, ITabularDataUnmarshaller

Column = implementer(ITabularDataColumn)(namedtuple('Column', ('name', 'spec')))

@implementer(ITabularDataColumnSpecification)
class Integer(object):
    rpad = u' '

    def __init__(self, length, pytype=int, nullable=False, null_value=u'', constraints=[]):
        self.length = length
        self.pytype = pytype
        self.nullable = nullable
        self.null_value = null_value
        self.constraints = constraints

    def marshal(self, context, pyval):
        if self.nullable and pyval is None:
            return self.null_value
        if not isinstance(pyval, self.pytype):
            raise TypeError('%s expected, got %r (%s)' % (self.pytype.__name__, pyval, pyval.__class__.__name__))
        for constraint in self.constraints:
            constraint(pyval)
        retval = u'{0:n}'.format(pyval)
        if self.length is not None and len(retval) > self.length:
            raise ValueError('resulting string (%r) exceeds the specified length (%d)' % (retval, self.length))
        return retval

    def unmarshal(self, context, val):
        if not isinstance(val, unicode):
            raise TypeError('unicode type expected, got %r' % val)
        if self.nullable and val == self.null_value:
            return None
        if self.length is not None and len(val) > self.length:
            raise ValueError('len(%r) > %d' % (val, self.length))
        try:
            retval = self.pytype(val)
        except decimal.InvalidOperation as e:
            raise ValueError(e.message)
        for constraint in self.constraints:
            constraint(retval)
        return retval


@implementer(ITabularDataColumnSpecification)
class ZeroPaddedInteger(object):
    rpad = u' '

    def __init__(self, length, pytype=int, nullable=False, null_value=u'', constraints=[]):
        self.length = length
        self.pytype = pytype
        self.nullable = nullable
        self.null_value = null_value
        self.constraints = constraints

    def marshal(self, context, pyval):
        if self.nullable and pyval is None:
            return self.null_value
        if not isinstance(pyval, self.pytype):
            raise TypeError('%s expected, got %r (%s)' % (self.pytype.__name__, pyval, pyval.__class__.__name__))
        for constraint in self.constraints:
            constraint(pyval)
        retval = (u'{0:0%dn}' % self.length).format(pyval)
        if self.length is not None and len(retval) > self.length:
            raise ValueError('resulting string (%r) exceeds the specified length (%d)' % (retval, self.length))
        return retval

    def unmarshal(self, context, val):
        if not isinstance(val, unicode):
            raise TypeError('unicode type expected')
        if self.nullable and val == self.null_value:
            return None
        if len(val) != self.length:
            raise ValueError('len(%r) != %d' % (val, self.length))
        try:
            retval = self.pytype(val)
        except decimal.InvalidOperation as e:
            raise ValueError(e.message)
        for constraint in self.constraints:
            constraint(retval)
        return retval


@implementer(ITabularDataColumnSpecification)
class NumericString(object):
    rpad = u' '

    def __init__(self, length, nullable=False, null_value=u'', constraints=[]):
        self.length = length
        self.nullable = nullable
        self.null_value = null_value
        self.constraints = constraints

    def marshal(self, context, pyval):
        if self.nullable and pyval is None:
            return self.null_value
        if not isinstance(pyval, unicode):
            raise TypeError('unicode type expected, got %r (%s)' % (pyval, pyval.__class__.__name__))
        if re.match(u'[^0-9]', pyval):
            raise ValueError('non-decimal character contained in the string (%r)' % pyval)
        if len(pyval) > self.length:
            raise ValueError('resulting string (%r) exceeds the specified length (%d)' % (pyval, self.length))
        for constraint in self.constraints:
            constraint(pyval)
        return pyval

    def unmarshal(self, context, val):
        if not isinstance(val, unicode):
            raise TypeError('unicode type expected')
        if self.nullable and val == self.null_value:
            return None
        if re.match(u'[^0-9]', val):
            raise ValueError('non-decimal character contained in the string (%r)' % val)
        if len(val) > self.length:
            raise ValueError('len(%r) > %d' % (val, self.length))
        for constraint in self.constraints:
            constraint(val)
        return val


@implementer(ITabularDataColumnSpecification)
class ZeroPaddedNumericString(object):
    rpad = u' '

    def __init__(self, length, nullable=False, null_value=u'', constraints=[]):
        self.length = length
        self.nullable = nullable
        self.null_value = null_value
        self.constraints = constraints

    def marshal(self, context, pyval):
        if self.nullable and pyval is None:
            return self.null_value
        if not isinstance(pyval, unicode):
            raise TypeError('unicode type expected, got %r (%s)' % (pyval, pyval.__class__.__name__))
        if re.match(u'[^0-9]', pyval):
            raise ValueError('non-decimal character contained in the string (%r)' % pyval)
        if len(pyval) > self.length:
            raise ValueError('resulting string (%r) exceeds the specified length (%d)' % (pyval, self.length))
        for constraint in self.constraints:
            constraint(pyval)
        return pyval.rjust(self.length, u'0')

    def unmarshal(self, context, val):
        if not isinstance(val, unicode):
            raise TypeError('unicode type expected')
        if self.nullable and val == self.null_value:
            return None
        if re.match(u'[^0-9]', val):
            raise ValueError('non-decimal character contained in the string (%r)' % val)
        if len(val) != self.length:
            raise ValueError('len(%r) != %d' % (val, self.length))
        for constraint in self.constraints:
            constraint(val)
        return val


@implementer(ITabularDataColumnSpecification)
class Decimal(object):
    rpad = u' '

    def __init__(self, length=None, precision=11, scale=0, rounding=decimal.ROUND_HALF_UP, nullable=False, null_value=u'', constraints=[]):
        if length is None:
            length = precision + 2
        self.length = length
        self.precision = precision
        self.scale = scale
        self.nullable = nullable
        self.null_value = null_value
        self.constraints = constraints
        self._context = decimal.Context(prec=self.precision, Emin=0, Emax=(self.precision - 1), rounding=rounding)

    def marshal(self, context, pyval):
        if self.nullable and pyval is None:
            return self.null_value
        if not isinstance(pyval, (int, long, float, decimal.Decimal)):
            raise TypeError('int, long, float or Decimal type expected, got %r (%s)' % (pyval, pyval.__class__.__name__))
        pyval = self._context.create_decimal(pyval)
        if pyval.adjusted() >= self.precision - self.scale:
            pyval = self._context.create_decimal((pyval.is_signed(), (9, ) * self.precision, -self.scale))
        for constraint in self.constraints:
            constraint(pyval)
        retval = u'{0:n}'.format(pyval)
        if self.length is not None and len(retval) > self.length:
            raise ValueError('resulting string (%r) exceeds the specified length (%d)' % (retval, self.length))
        return retval

    def unmarshal(self, context, val):
        if not isinstance(val, unicode):
            raise TypeError('unicode type expected, got %r' % val)
        if self.nullable and val == self.null_value:
            return None
        if self.length is not None and len(val) > self.length:
            raise ValueError('len(%r) > %d' % (val, self.length))
        try:
            pyval = self._context.create_decimal(val)
            if pyval.adjusted() >= self.precision - self.scale:
                pyval = self._context.create_decimal((pyval.is_signed(), (9, ) * self.precision, -self.scale))
        except decimal.InvalidOperation as e:
            raise ValueError(e.message)
        for constraint in self.constraints:
            constraint(pyval)
        return pyval


@implementer(ITabularDataColumnSpecification)
class Boolean(object):
    rpad = u' '

    def __init__(self, true_sign='y', false_sign='n', nullable=False, null_value=u'', constraints=[]):
        self.true_sign = true_sign
        self.false_sign = false_sign
        self.nullable = nullable
        self.null_value = null_value
        self.constraints = constraints
        self.length = max(len(true_sign), len(false_sign))

    def marshal(self, context, pyval):
        if self.nullable and pyval is None:
            return self.null_value
        if not isinstance(pyval, bool):
            raise TypeError('bool type expected')
        for constraint in self.constraints:
            constraint(pyval)
        return self.true_sign if pyval else self.false_sign

    def unmarshal(self, context, val):
        if not isinstance(val, unicode):
            raise TypeError('unicode type expected')
        if self.nullable and val == self.null_value:
            retval = None
        if val == self.true_sign:
            retval = True
        elif val == self.false_sign:
            retval = False
        else:
            raise ValueError('unexpected value: %s' % val)
        for constraint in self.constraints:
            constraint(retval)
        return retval


@implementer(ITabularDataColumnSpecification)
class WideWidthString(object):
    rpad = u'　'

    def __init__(self, length, conversion=False, nullable=False, null_value=u'', constraints=[]):
        self.length = length
        self.conversion = conversion
        self.nullable = nullable
        self.null_value = null_value
        self.constraints = constraints

    def marshal(self, context, pyval):
        if self.nullable and pyval is None:
            return self.null_value
        if not isinstance(pyval, unicode):
            raise TypeError('unicode type expected')
        if self.conversion:
            pyval = hankaku2zenkaku(pyval)
        if not multibyte_in_sjis(pyval):
            raise ValueError('non-widewidth character contained in the string (%r)' % pyval)
        if len(pyval) > self.length:
            raise ValueError('resulting string (%r) exceeds the specified length (%d)' % (pyval, self.length))
        for constraint in self.constraints:
            constraint(pyval)
        return pyval

    def unmarshal(self, context, val):
        if not isinstance(val, unicode):
            raise TypeError('unicode type expected')
        if self.nullable and val == self.null_value:
            retval = None
        if not multibyte_in_sjis(val):
            raise ValueError('non-widewidth character contained in the string (%r)' % val)
        if len(val) > self.length:
            raise ValueError('len(%r) > %d' % (val, self.length))
        for constraint in self.constraints:
            constraint(val)
        return val


@implementer(ITabularDataColumnSpecification)
class SJISString(object):
    rpad = u' '

    def __init__(self, length, nullable=False, null_value=u'', constraints=[]):
        self.length = length
        self.nullable = nullable
        self.null_value = null_value
        self.constraints = constraints

    def marshal(self, context, pyval):
        if not isinstance(pyval, unicode):
            raise TypeError('unicode type expected')
        if self.nullable and pyval is None:
            return self.null_value
        if len_in_sjis(pyval) > self.length:
            raise ValueError('resulting string (%r) exceeds the specified length (%d)' % (pyval, self.length))
        for constraint in self.constraints:
            constraint(pyval)
        return pyval

    def unmarshal(self, context, val):
        if not isinstance(val, unicode):
            raise TypeError('unicode type expected')
        if self.nullable and val == self.null_value:
            return None
        if len_in_sjis(val) > self.length:
            raise ValueError('len(%r) > %d' % (val, self.length))
        for constraint in self.constraints:
            constraint(val)
        return val


@implementer(ITabularDataColumnSpecification)
class DateTime(object):
    rpad = u' '

    def __init__(self, length, pytype=datetime, format=u'', nullable=False, null_value=u'', constraints=[]):
        self.length = length
        self.pytype = pytype
        self.format = format
        self.nullable = nullable
        self.null_value = null_value
        self.constraints = constraints

    def marshal(self, context, pyval):
        if self.nullable and pyval is None:
            return self.null_value
        if not isinstance(pyval, self.pytype):
            raise TypeError('%s expected, got %r' % (self.pytype.__name__, pyval))
        for constraint in self.constraints:
            constraint(pyval)
        retval = unicode(pyval.strftime(self.format))
        if len(retval) > self.length:
            raise ValueError('resulting string (%r) exceeds the specified length (%d)' % (retval, self.length))
        return retval

    def unmarshal(self, context, val):
        if not isinstance(val, unicode):
            raise TypeError('unicode type expected')
        if self.nullable and val == self.null_value:
            return None
        else:
            v = datetime.strptime(val, self.format)
            if self.pytype == datetime:
                pass
            elif self.pytype == date:
                v = v.date()
            else:
                raise TypeError('unsupported type: %s' % self.pytype.__name__)
        for constraint in self.constraints:
            constraint(v)
        return v


@implementer(ITabularDataColumnSpecification)
class Time(object):
    rpad = u' '

    def __init__(self, length, format=u'', nullable=False, null_value=u'', constraints=[]):
        self.length = length
        self.format = format
        self.nullable = nullable
        self.null_value = null_value
        self.constraints = constraints

    def marshal(self, context, pyval):
        if self.nullable and pyval is None:
            return self.null_value
        if not isinstance(pyval, time):
            raise TypeError('%s expected, got %r' % (time.__name__, pyval))
        for constraint in self.constraints:
            constraint(pyval)
        retval = unicode(pyval.strftime(self.format))
        if len(retval) > self.length:
            raise ValueError('resulting string (%r) exceeds the specified length (%d)' % (retval, self.length))
        return retval

    def unmarshal(self, context, val):
        if not isinstance(val, unicode):
            raise TypeError('unicode type expected')
        if self.nullable and val == self.null_value:
            retval = None
        else:
            retval = datetime.strptime(val, self.format).time()
        for constraint in self.constraints:
            constraint(retval)
        return retval


@implementer(ITabularDataColumnSpecification)
class HHMMTime(object):
    rpad = u' '

    def __init__(self, nullable=False, null_value=u'', constraints=[]):
        self.nullable = nullable
        self.null_value = null_value
        self.constraints = constraints

    def marshal(self, context, pyval):
        if self.nullable and pyval is None:
            return self.null_value
        if not isinstance(pyval, time):
            raise TypeError('%s expected, got %r' % (time.__name__, pyval))
        for constraint in self.constraints:
            constraint(pyval)
        retval = unicode(pyval.strftime('%H%M')).lstrip(u'0')
        if len(retval) > 4:
            raise ValueError('resulting string (%r) exceeds the specified length (%d)' % (retval, self.length))
        return retval

    def unmarshal(self, context, val):
        if not isinstance(val, unicode):
            raise TypeError('unicode type expected')
        if self.nullable and val == self.null_value:
            retval = None
        else:
            retval = datetime.strptime(val.zfill(4), '%H%M').time()
        for constraint in self.constraints:
            constraint(retval)
        return retval


@implementer(ITabularDataColumnSpecification)
class Duration(object):
    rpad = u' '

    def __init__(self, length, format=u'', nullable=False, null_value=u'', constraints=[]):
        self.length = length
        self.format = format
        self.nullable = nullable
        self.null_value = null_value
        self.constraints = constraints

    def marshal(self, context, pyval):
        if self.nullable and pyval is None:
            return self.null_value
        if not isinstance(pyval, timedelta):
            raise TypeError('%s expected, got %r' % (int.__name__, pyval))
        for constraint in self.constraints:
            constraint(pyval)
        retval = build_duration(pyval, self.format)
        if len(retval) > self.length:
            raise ValueError('resulting string (%r) exceeds the specified length (%d)' % (retval, self.length))
        return retval

    def unmarshal(self, context, val):
        if not isinstance(val, unicode):
            raise TypeError('unicode type expected')
        if self.nullable and val == self.null_value:
            retval = None
        else:
            retval = parse_duration(val, self.format)
        for constraint in self.constraints:
            constraint(retval)
        return retval


@implementer(ITabularDataColumnSpecification)
class HHMMDuration(object):
    rpad = u' '

    def __init__(self, nullable=False, null_value=u'', constraints=[]):
        self.nullable = nullable
        self.null_value = null_value
        self.constraints = constraints

    def marshal(self, context, pyval):
        if self.nullable and pyval is None:
            return self.null_value
        if not isinstance(pyval, timedelta):
            raise TypeError('%s expected, got %r' % (int.__name__, pyval))
        for constraint in self.constraints:
            constraint(pyval)
        retval = build_duration(pyval, '%H%M').lstrip(u'0')
        if len(retval) > 4:
            raise ValueError('resulting string (%r) exceeds the specified length (%d)' % (retval, self.length))
        return retval

    def unmarshal(self, context, val):
        if not isinstance(val, unicode):
            raise TypeError('unicode type expected')
        if self.nullable and val == self.null_value:
            retval = None
        else:
            retval = parse_duration(val.zfill(4), u'%H%M')
        for constraint in self.constraints:
            constraint(retval)
        return retval


class MarshalErrorBase(Exception):
    @property
    def message(self):
        return self.args[0]

class RespectiveMarshalErrorBase(MarshalErrorBase):
    @property
    def field(self):
        return self.args[1]


class MarshalError(RespectiveMarshalErrorBase):
    def __init__(self, message, field, value):
        super(MarshalError, self).__init__(message, field, value)

    @property
    def value(self):
        return self.value

    def __str__(self):
        return u'%s: %s (value=%s)' % (self.field, self.message, self.value)


class UnmarshalError(RespectiveMarshalErrorBase):
    def __init__(self, message, field, value):
        super(UnmarshalError, self).__init__(message, field, value)

    @property
    def value(self):
        return self.value

    def __str__(self):
        return u'%s: %s (value=%s)' % (self.field, self.message, self.value)


class MarshalErrorCollection(MarshalErrorBase):
    def __init__(self, message, errors):
        super(MarshalErrorCollection, self).__init__(message, errors)

    @property
    def errors(self):
        return self.args[1]

    def __str__(self):
        return u'%s: %s' % (self.message, u', '.join(unicode(error) for error in self.errors))


class UnmarshalErrorCollection(MarshalErrorBase):
    def __init__(self, message, errors):
        super(UnmarshalErrorCollection, self).__init__(message, errors)

    @property
    def errors(self):
        return self.args[1]

    def __str__(self):
        print u'%s: %s' % (self.message, u', '.join(unicode(error) for error in self.errors))
        return u'%s: %s' % (self.message, u', '.join(unicode(error) for error in self.errors))


@implementer(ITabularDataMarshaller)
class FixedRecordMarshaller(object):
    def __init__(self, schema):
        self.schema = schema

    def __call__(self, row, out):
        rendered = []
        errors = []
        for name, spec in self.schema:
            pyval = row[name]
            try:
                v = spec.marshal(self, pyval)
                rv = v.ljust(spec.length, spec.rpad)
            except Exception as e:
                errors.append(MarshalError(e.message, name, pyval))
                rv = b''
            rendered.append(rv)
        if errors:
            raise MarshalErrorCollection('error occurred during marshalling data', errors=errors)
        out(u''.join(rendered))

@implementer(ITabularDataMarshaller)
class CSVRecordMarshaller(object):
    def __init__(self, schema):
        self.schema = schema

    def __call__(self, row, out):
        encoded_row = []
        errors = []
        for name, spec in self.schema:
            pyval = row[name]
            try:
                v = spec.marshal(self, pyval)
                ev = v.encode('utf-8')
            except Exception as e:
                errors.append(MarshalError(e.message, name, pyval))
                ev = b''
            encoded_row.append(ev)
        if errors:
            raise MarshalErrorCollection('error occurred during marshalling data', errors=errors)
        x = io.BytesIO()
        w = csv.writer(x)
        w.writerow(encoded_row)
        out(six.text_type(x.getvalue(), 'utf-8'))

@implementer(ITabularDataUnmarshaller)
class RecordUnmarshaller(object):
    def __init__(self, schema, exc_handler=None):
        self.schema = schema
        self.exc_handler = exc_handler

    def __call__(self, in_):
        for row in in_:
            retval = {}
            errors = []
            try:
                for (name, spec), v in zip(self.schema, row):
                    try:
                        retval[name] = spec.unmarshal(self, v)
                    except Exception as e:
                        errors.append(UnmarshalError(e.message, name, v))
                if errors:
                    raise UnmarshalErrorCollection('error occurred during unmarshalling data', errors=errors)
            except:
                if self.exc_handler is not None:
                    exc_info = sys.exc_info()
                    if self.exc_handler(exc_info):
                        raise exc_info[1], None, exc_info[2]
                else:
                    raise
            yield retval


class NotBefore(object):
    def __init__(self, datetime):
            self._datetime = datetime

    def __call__(self, pyval):
        if pyval is not None and pyval < self._datetime:
            raise ValueError(u'%s < %s' % (pyval, self._datetime))
