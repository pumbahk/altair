# encoding: utf-8
from __future__ import absolute_import
import re
from decimal import Decimal, InvalidOperation
from zope.interface import implementer
from datetime import date, datetime
from .interfaces import ITabularDataColumn, ITabularDataColumnSpecification, ITabularDataMarshaller, ITabularDataUnmarshaller
from collections import namedtuple

Column = implementer(ITabularDataColumn)(namedtuple('Column', ('name', 'spec')))


def sjis_iterator(v):
    s = 0
    for c in v:
        if c.__class__ != int:
            c = ord(c)
        if s == 0:
            if (c >= 0x81 and c <= 0x9f) or (c >= 0xe0 and c <= 0xfc):
                s = c << 8
                continue
        else:
            c = s | c
            s = 0
        yield c

def multibyte_in_sjis(v):
    return all(c >= 0x100 for c in sjis_iterator(v.encode('cp932')))

@implementer(ITabularDataColumnSpecification)
class Integer(object):
    rpad = u' '

    def __init__(self, length, constraints=[]):
        self.length = length
        self.constraints = []

    def marshal(self, context, pyval):
        if not isinstance(pyval, (int, long, Decimal)):
            raise TypeError('int, long or Decimal type expected, got %r (%s)' % (pyval, pyval.__class__.__name__))
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
            return Decimal(val)
        except InvalidOperation as e:
            raise ValueError(e.message)


@implementer(ITabularDataColumnSpecification)
class ZeroPaddedInteger(object):
    rpad = u' '

    def __init__(self, length, constraints=[]):
        self.length = length
        self.constraints = []

    def marshal(self, context, pyval):
        if not isinstance(pyval, (int, long, Decimal)):
            raise TypeError('int, long or Decimal type expected')
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
            return Decimal(val)
        except InvalidOperation as e:
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

    def __init__(self, length, constraints=[]):
        self.length = length
        self.constraints = []

    def marshal(self, context, pyval):
        if not isinstance(pyval, unicode):
            raise TypeError('unicode type expected')
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
class DateTime(object):
    rpad = u' '

    def __init__(self, length, pytype=datetime, format=u'', constraints=[]):
        self.length = length
        self.format = format
        self.pytype = pytype
        self.constraints = []

    def marshal(self, context, pyval):
        if not isinstance(pyval, self.pytype):
            raise TypeError('date type expected')
        retval = unicode(pyval.strftime(self.format))
        if len(retval) > self.length:
            raise ValueError('resulting string (%r) exceeds the specified length (%d)' % (retval, self.length))
        return retval

    def unmarshal(self, context, val):
        if not isinstance(val, unicode):
            raise TypeError('unicode type expected')
        return self.pytype.strptime(val, self.format)


class MarshalError(Exception):
    pass

@implementer(ITabularDataMarshaller)
class FixedRecordMarshaller(object):
    def __init__(self, schema):
        self.schema = schema

    def __call__(self, row):
        rendered = []
        for name, spec in self.schema:
            pyval = row[name]
            try:
                v = spec.marshal(self, pyval)
            except Exception as e:
                raise MarshalError('%s for column "%s"' % (e.message, name))
            rv = v.ljust(spec.length, spec.rpad)
            rendered.append(rv)
        return u''.join(rendered)

