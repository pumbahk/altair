import re
from datetime import timedelta
from collections import OrderedDict

parser_format_specifiers = {
    u'%D': ur'(?P<days>[0-9]+)?',
    u'%H': ur'(?P<hours>[0-9]+)?',
    u'%M': ur'(?P<minutes>[0-9]{2})',
    u'%S': ur'(?P<seconds>[0-9]{2})',
    u'%R': ur'(?P<hours>[0-9]+):(?P<minutes>[0-9]{2})',
    u'%T': ur'(?P<hours>[0-9]+):(?P<minutes>[0-9]{2}):(?P<seconds>[0-9]{2})',
    }


class DurationParser(object):
    defaults = {
        'days': 0,
        'hours': 0,
        'minutes': 0,
        'seconds': 0
        }

    def __init__(self, format, defaults=None):
        if defaults is None:
            defaults = self.__class__.defaults
        buf = ['^']
        for g in re.finditer(ur'(%[a-zA-Z%])|((?:[^%]|%[^a-zA-Z%])+)', format):
            s = g.group(1)
            if s is not None:
                if s == u'%%':
                    buf.append(u'%%')
                else:
                    regex = parser_format_specifiers.get(s)
                    if regex is None:
                        raise ValueError('unsupported format specifier: %s' % s)
                    buf.append(regex)
            else:
                s = g.group(2)
                buf.append(re.escape(s))
        buf.append(u'$')
        self.regex = re.compile(u''.join(buf))
        self.defaults = defaults

    def __call__(self, s):
        g = self.regex.match(s)
        if g is None:
            raise ValueError('given string does not match to the format')
        retval = dict(self.defaults)
        for k, v in g.groupdict().items():
            retval[k] = int(v)
        return retval

parser_cache = OrderedDict()
max_parser_cache_size = 16

def get_parser(format, defaults=None):
    pair = (format, defaults)
    parser = parser_cache.pop(pair, None)
    if parser is None:
        if len(parser_cache) >= max_parser_cache_size:
            parser_cache.popitem(last=False) # LRU
        parser = parser_cache[pair] = DurationParser(format)
    else:
        parser_cache[pair] = parser # move to the last
    return parser

def parse_duration(s, format, defaults=None):
    parser = get_parser(format, defaults)
    d = parser(s)
    return timedelta(**d)

builder_format_specifiers = {
    '%D': (True, lambda d: u'{days}'.format(**d)),
    '%H': (False, lambda d: u'{hours}'.format(**d)),
    '%M': (False, lambda d: u'{minutes:02d}'.format(**d)),
    '%S': (False, lambda d: u'{seconds:02d}s'.format(**d)),
    '%R': (False, lambda d: u'{hours}:{minutes}'.format(**d)),
    '%T': (False, lambda d: u'{hours}:{minutes}:{seconds}'.format(**d)),
    }

class DurationBuilder(object):
    def __init__(self, format):
        op = []
        days_wanted = False
        for g in re.finditer(ur'(%[a-zA-Z%])|((?:[^%]|%[^a-zA-Z%])+)', format):
            s = g.group(1)
            if s is not None:
                if s == u'%%':
                    op.append(u'%%')
                else:
                    pair = builder_format_specifiers.get(s)
                    if pair is None:
                        raise ValueError('unsupported format specifier: %s' % s)
                    days_wanted = days_wanted or pair[0]
                    op.append(pair[1])
            else:
                s = g.group(2)
                op.append(s)
        self.op = op
        self.days_wanted = days_wanted

    def __call__(self, s):
        retval = []
        for o in self.op:
            if isinstance(o, basestring):
                retval.append(o)
            else:
                retval.append(o(s))
        return u''.join(retval)

builder_cache = OrderedDict()
max_builder_cache_size = 16

def get_builder(format):
    builder = builder_cache.pop(format, None)
    if builder is None:
        if len(builder_cache) >= max_builder_cache_size:
            builder_cache.popitem(last=False) # LRU
        builder = builder_cache[format] = DurationBuilder(format)
    else:
        builder_cache[format] = builder # move to the last
    return builder

def build_duration(s, format):
    builder = get_builder(format)
    d = {}
    if builder.days_wanted:
        d['days'] = s.days
        v = s.seconds
    else:
        v = s.days * 86400 + s.seconds
    d['hours'] = v // 3600
    v = v % 3600 
    d['minutes'] = v // 60
    v = v % 60
    d['seconds'] = v
    return builder(d)
    
