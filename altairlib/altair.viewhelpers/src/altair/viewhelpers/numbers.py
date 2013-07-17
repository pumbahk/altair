# encoding: utf-8

from decimal import Decimal
from .string import RawText

def _format_number(buf, sep, dec, quantum=0):
    sign, digits, exp = Decimal(dec).quantize(Decimal(10) ** quantum).as_tuple()
    i = len(digits)
    c = 0
    while i > 0:
        i -= 1
        buf.append(unicode(digits[i]))
        c += 1
        if c % 3 == 0 and i != 0:
            buf.append(sep) 
    return sign

class DefaultNumberFormatter(object):
    sep = u','

    def format_number(self, dec, quantum=2, **flavor):
        buf = []
        if _format_number(buf, self.sep, dec, quantum):
            buf.append(u'-')
        buf.reverse()
        return u''.join(buf)

    def format_currency(self, dec, **flavor):
        buf = []
        if 'prefer_post_symbol' in flavor:
            buf.append(u'円')
        sign = _format_number(buf, self.sep, dec, 0)
        if 'prefer_post_symbol' not in flavor:
            buf.append(u'\u00a5')
        if sign:
            buf.append(u'-')
        buf.reverse()
        return u''.join(buf)

    def format_currency_html(self, dec, **flavor):
        return RawText(self.format_currency(dec).replace(u'\u00a5', '&yen;'))

class NumberHelper(object):
    def __init__(self, formatter):
        self.formatter = formatter 

    def number(self, dec):
        return self.formatter.format_number(dec) 

    def price(self, dec):
        return self.formatter.format_currency_html(dec)

def create_number_formatter(request):
    return DefaultNumberFormatter()
