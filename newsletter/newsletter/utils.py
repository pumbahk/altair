# -*- coding:utf-8 -*-
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

    def __repr__(self):
        return "<%s.%s value=%s>" % (self.__class__.__name__, self.k, self.v)
