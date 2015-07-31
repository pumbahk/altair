# encoding: utf-8
from __future__ import absolute_import
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

    def __init__(self, length, pytype=int, constraints=[]):
        self.length = length
        self.pytype = pytype
        self.constraints = []

    def marshal(self, context, pyval):
        if not isinstance(pyval, self.pytype):
            raise TypeError('%s expected, got %r (%s)' % (self.pytype.__name__, pyval, pyval.__class__.__name__))
        retval = u'{0:n}'.format(pyval)
        if self.length is not None and len(retval) > self.length:
            raise ValueError('resulting string (%r) exceeds the specified length (%d)' % (retval, self.length))
        return retval

    def unmarshal(self, context, val):
        if not isinstance(val, unicode):
            raise TypeError('unicode type expected, got %r' % val)
        if self.length is not None and len(val) > self.length:
            raise ValueError('len(%r) > %d' % (val, self.length))
        try:
            return self.pytype(val)
        except decimal.InvalidOperation as e:
            raise ValueError(e.message)


@implementer(ITabularDataColumnSpecification)
class ZeroPaddedInteger(object):
    rpad = u' '

    def __init__(self, length, pytype=int, constraints=[]):
        self.length = length
        self.pytype = pytype
        self.constraints = []

    def marshal(self, context, pyval):
        if not isinstance(pyval, self.pytype):
            raise TypeError('%s expected, got %r (%s)' % (self.pytype.__name__, pyval, pyval.__class__.__name__))
        retval = (u'{0:0%dn}' % self.length).format(pyval)
        if self.length is not None and len(retval) > self.length:
            raise ValueError('resulting string (%r) exceeds the specified length (%d)' % (retval, self.length))
        return retval

    def unmarshal(self, context, val):
        if not isinstance(val, unicode):
            raise TypeError('unicode type expected')
        if len(val) != self.length:
            raise ValueError('len(%r) != %d' % (val, self.length))
        try:
            return self.pytype(val)
        except decimal.InvalidOperation as e:
            raise ValueError(e.message)


@implementer(ITabularDataColumnSpecification)
class NumericString(object):
    rpad = u' '

    def __init__(self, length, constraints=[]):
        self.length = length
        self.constraints = []

    def marshal(self, context, pyval):
        if not isinstance(pyval, unicode):
            raise TypeError('unicode type expected, got %r (%s)' % (pyval, pyval.__class__.__name__))
        if re.match(u'[^0-9]', pyval):
            raise ValueError('non-decimal character contained in the string (%r)' % pyval)
        if len(pyval) > self.length:
            raise ValueError('resulting string (%r) exceeds the specified length (%d)' % (pyval, self.length))
        return pyval

    def unmarshal(self, context, val):
        if not isinstance(val, unicode):
            raise TypeError('unicode type expected')
        if re.match(u'[^0-9]', val):
            raise ValueError('non-decimal character contained in the string (%r)' % val)
        if len(val) != self.length:
            raise ValueError('len(%r) != %d' % (val, self.length))
        return val


@implementer(ITabularDataColumnSpecification)
class ZeroPaddedNumericString(object):
    rpad = u' '

    def __init__(self, length, constraints=[]):
        self.length = length
        self.constraints = []

    def marshal(self, context, pyval):
        if not isinstance(pyval, unicode):
            raise TypeError('unicode type expected, got %r (%s)' % (pyval, pyval.__class__.__name__))
        if re.match(u'[^0-9]', pyval):
            raise ValueError('non-decimal character contained in the string (%r)' % pyval)
        if len(pyval) > self.length:
            raise ValueError('resulting string (%r) exceeds the specified length (%d)' % (pyval, self.length))
        return pyval.rjust(self.length, u'0')

    def unmarshal(self, context, val):
        if not isinstance(val, unicode):
            raise TypeError('unicode type expected')
        if re.match(u'[^0-9]', val):
            raise ValueError('non-decimal character contained in the string (%r)' % val)
        if len(val) != self.length:
            raise ValueError('len(%r) != %d' % (val, self.length))
        return val


@implementer(ITabularDataColumnSpecification)
class Decimal(object):
    rpad = u' '

    def __init__(self, length=None, precision=11, scale=0, rounding=decimal.ROUND_HALF_UP, constraints=[]):
        if length is None:
            length = precision + 2
        self.length = length
        self.constraints = []
        self.precision = precision
        self.scale = scale
        self._context = decimal.Context(prec=self.precision, Emin=0, Emax=(self.precision - 1), rounding=rounding)

    def marshal(self, context, pyval):
        if not isinstance(pyval, (int, long, float, decimal.Decimal)):
            raise TypeError('int, long, float or Decimal type expected, got %r (%s)' % (pyval, pyval.__class__.__name__))
        pyval = self._context.create_decimal(pyval)
        if pyval.adjusted() >= self.precision - self.scale:
            pyval = self._context.create_decimal((pyval.is_signed(), (9, ) * self.precision, -self.scale))
        retval = u'{0:n}'.format(pyval)
        if self.length is not None and len(retval) > self.length:
            raise ValueError('resulting string (%r) exceeds the specified length (%d)' % (retval, self.length))
        return retval

    def unmarshal(self, context, val):
        if not isinstance(val, unicode):
            raise TypeError('unicode type expected, got %r' % val)
        if self.length is not None and len(val) > self.length:
            raise ValueError('len(%r) > %d' % (val, self.length))
        try:
            pyval = self._context.create_decimal(val)
            if pyval.adjusted() >= self.precision - self.scale:
                pyval = self._context.create_decimal((pyval.is_signed(), (9, ) * self.precision, -self.scale))
            return pyval
        except decimal.InvalidOperation as e:
            raise ValueError(e.message)


@implementer(ITabularDataColumnSpecification)
class Boolean(object):
    rpad = u' '

    def __init__(self, true_sign='y', false_sign='n', constraints=[]):
        self.true_sign = true_sign
        self.false_sign = false_sign
        self.constraints = constraints
        self.length = max(len(true_sign), len(false_sign))

    def marshal(self, context, pyval):
        if not isinstance(pyval, bool):
            raise TypeError('bool type expected')
        return self.true_sign if pyval else self.false_sign

    def unmarshal(self, context, val):
        if not isinstance(val, unicode):
            raise TypeError('unicode type expected')
        if val == self.true_sign:
            return True
        elif val == self.false_sign:
            return False
        else:
            raise ValueError('unexpected value: %s' % val)


@implementer(ITabularDataColumnSpecification)
class WideWidthString(object):
    rpad = u'　'

    def __init__(self, length, conversion=False, constraints=[]):
        self.length = length
        self.conversion = conversion
        self.constraints = []

    def marshal(self, context, pyval):
        if not isinstance(pyval, unicode):
            raise TypeError('unicode type expected')
        if self.conversion:
            pyval = hankaku2zenkaku(pyval)
        if not multibyte_in_sjis(pyval):
            raise ValueError('non-widewidth character contained in the string (%r)' % pyval)
        if len(pyval) > self.length:
            raise ValueError('resulting string (%r) exceeds the specified length (%d)' % (pyval, self.length))
        return pyval

    def unmarshal(self, context, val):
        if not isinstance(val, unicode):
            raise TypeError('unicode type expected')
        if multibyte_in_sjis(pyval):
            raise ValueError('non-widewidth character contained in the string (%r)' % val)
        if len(val) != self.length:
            raise ValueError('len(%r) != %d' % (val, self.length))


@implementer(ITabularDataColumnSpecification)
class SJISString(object):
    rpad = u' '

    def __init__(self, length, constraints=[]):
        self.length = length
        self.constraints = []

    def marshal(self, context, pyval):
        if not isinstance(pyval, unicode):
            raise TypeError('unicode type expected')
        if len_in_sjis(pyval) > self.length:
            raise ValueError('resulting string (%r) exceeds the specified length (%d)' % (pyval, self.length))
        return pyval

    def unmarshal(self, context, val):
        if not isinstance(val, unicode):
            raise TypeError('unicode type expected')
        if len_in_sjis(val) > self.length:
            raise ValueError('len(%r) > %d' % (val, self.length))
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
        self.constraints = []

    def marshal(self, context, pyval):
        if self.nullable and pyval is None:
            return self.null_value
        if not isinstance(pyval, self.pytype):
            raise TypeError('%s expected, got %r' % (self.pytype.__name__, pyval))
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
                return v
            elif self.pytype == date:
                return v.date()
            else:
                raise TypeError('unsupported type: %s' % self.pytype.__name__)


@implementer(ITabularDataColumnSpecification)
class Time(object):
    rpad = u' '

    def __init__(self, length, format=u'', nullable=False, null_value=u'', constraints=[]):
        self.length = length
        self.format = format
        self.nullable = nullable
        self.null_value = null_value
        self.constraints = []

    def marshal(self, context, pyval):
        if self.nullable and pyval is None:
            return self.null_value
        if not isinstance(pyval, time):
            raise TypeError('%s expected, got %r' % (time.__name__, pyval))
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
            return datetime.strptime(val, self.format).time()


@implementer(ITabularDataColumnSpecification)
class Duration(object):
    rpad = u' '

    def __init__(self, length, format=u'', nullable=False, null_value=u'', constraints=[]):
        self.length = length
        self.format = format
        self.nullable = nullable
        self.null_value = null_value
        self.constraints = []

    def marshal(self, context, pyval):
        if self.nullable and pyval is None:
            return self.null_value
        if not isinstance(pyval, timedelta):
            raise TypeError('%s expected, got %r' % (int.__name__, pyval))
        retval = build_duration(pyval, self.format)
        if len(retval) > self.length:
            raise ValueError('resulting string (%r) exceeds the specified length (%d)' % (retval, self.length))
        return retval

    def unmarshal(self, context, val):
        if not isinstance(val, unicode):
            raise TypeError('unicode type expected')
        if self.nullable and val == self.null_value:
            return None
        else:
            return parse_duration(val, self.format)


class MarshalError(Exception):
    pass

@implementer(ITabularDataMarshaller)
class FixedRecordMarshaller(object):
    def __init__(self, schema):
        self.schema = schema

    def __call__(self, row, out):
        rendered = []
        for name, spec in self.schema:
            pyval = row[name]
            try:
                v = spec.marshal(self, pyval)
            except Exception as e:
                raise MarshalError('%s for column "%s"' % (e.message, name))
            rv = v.ljust(spec.length, spec.rpad)
            rendered.append(rv)
        out(u''.join(rendered))

@implementer(ITabularDataMarshaller)
class CSVRecordMarshaller(object):
    def __init__(self, schema):
        self.schema = schema

    def __call__(self, row, out):
        encoded_row = []
        for name, spec in self.schema:
            pyval = row[name]
            try:
                v = spec.marshal(self, pyval)
            except Exception as e:
                raise MarshalError('%s for column "%s"' % (e.message, name))
            encoded_row.append(v.encode('utf-8'))
        x = io.BytesIO()
        w = csv.writer(x)
        w.writerow(encoded_row)
        out(six.text_type(x.getvalue(), 'utf-8'))

@implementer(ITabularDataUnmarshaller)
class RecordUnmarshaller(object):
    def __init__(self, schema):
        self.schema = schema

    def __call__(self, in_):
        for row in in_:
            yield dict((name, spec.unmarshal(self, v)) for (name, spec), v in zip(self.schema, row))
