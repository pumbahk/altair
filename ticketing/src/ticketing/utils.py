# -*- coding:utf-8 -*-

from datetime import datetime
from wtforms import DateTimeField

'''
http://blog.aodag.jp/2009/10/pythonenum.html
'''
class EnumType(type):

    def __init__(cls, name, bases, dct):
        super(EnumType, cls).__init__(name, bases, dct)
        cls._values = []

        for key, value in dct.iteritems():
            if not key.startswith('_'):
                v = cls(key, value)
                setattr(cls, key, v)
                cls._values.append(v)

    def __iter__(cls):
        return iter(cls._values)

class StandardEnum(object):

    __metaclass__ = EnumType

    def __init__(self, k, v):
        self.v = v
        self.k = k

    def __str__(self):
        return str(self.v)

    def __int__(self):
        return int(self.v)

    def __long__(self):
        return long(self.v)

    def __float__(self):
        return float(self.v)

    def __complex__(self):
        return complex(self.v)

    def __repr__(self):
        return "<%s.%s value=%s>" % (self.__class__.__name__, self.k, self.v)

'''
Customized field definition datetime format of "%Y-%m-%d %H:%M"
'''
class DateTimeField(DateTimeField):

    def _value(self):
        if self.raw_data:
            try:
                dt = datetime.strptime(self.raw_data[0], '%Y-%m-%d %H:%M:%S')
                return dt.strftime(self.format)
            except:
                return u' '.join(self.raw_data)
        else:
            return self.data and self.data.strftime(self.format) or u''

