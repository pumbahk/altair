# -*- coding:utf-8 -*-
from standardenum import StandardEnum
from urlparse import uses_relative, uses_netloc, urlparse
from decimal import Decimal
from pyramid.threadlocal import get_current_registry
from ticketing.mobile.interfaces import IMobileCarrierDetector
from ticketing.mobile.api import _detect_from_email_address

class DigitCodec(object):
    def __init__(self, digits):
        self.digits = digits

    def encode(self, num):
        l = len(self.digits)
        retval = []
        n = num
        while True:
            rem = n % l
            quo = n // l
            retval.insert(0, self.digits[rem])
            if quo == 0:
                break
            n = quo
        return ''.join(retval)

    def decode(self, s):
        i = 0
        sl = len(s)
        l = len(self.digits)
        retval = 0
        while i < sl:
            c = s[i]
            d = self.digits.find(c)
            if d < 0:
                raise ValueError("Invalid digit: " + c)
            retval *= l
            retval += d
            i += 1
        return retval

encoder = DigitCodec("0123456789ACFGHJKLPRSUWXYZ")
sensible_alnum_encode = encoder.encode
sensible_alnum_decode = encoder.decode

class URLHandler(object):
    def __init__(self, uses_relative=uses_relative, uses_netloc=uses_netloc):
        self.uses_relative = uses_relative
        self.uses_netloc = uses_netloc

    def unsplit(self, data):
        scheme, netloc, url, query, fragment = data
        if netloc or (scheme and self.uses_netloc is not None and scheme in self.uses_netloc and url[:2] != '//'):
            if url and scheme and self.uses_relative is not None and scheme in self.uses_relative and url[:1] != '/': url = '/' + url
            url = '//' + (netloc or '') + url
        if scheme:
            url = scheme + ':' + url
        if query:
            url = url + '?' + query
        if fragment:
            url = url + '#' + fragment
        return url

    def unparse(self, data):
        scheme, netloc, url, params, query, fragment = data
        if params:
            url = "%s;%s" % (url, params)
        return self.unsplit((scheme, netloc, url, query, fragment))

    def join(self, base, url, allow_fragments=True):
        if not base:
            return url
        if not url:
            return base
        bscheme, bnetloc, bpath, bparams, bquery, bfragment = \
                urlparse(base, '', allow_fragments)
        scheme, netloc, path, params, query, fragment = \
                urlparse(url, bscheme, allow_fragments)
        if scheme != bscheme or (
            self.uses_relative is not None and \
                scheme not in self.uses_relative):
            return url
        if self.uses_netloc is None or scheme in self.uses_netloc:
            if netloc:
                return self.unparse((scheme, netloc, path,
                                   params, query, fragment))
            netloc = bnetloc
        if path[:1] == '/':
            return self.unparse((scheme, netloc, path,
                               params, query, fragment))
        if not path:
            path = bpath
            if not params:
                params = bparams
            else:
                path = path[:-1]
                return self.unparse((scheme, netloc, path,
                                    params, query, fragment))
            if not query:
                query = bquery
            return self.unparse((scheme, netloc, path,
                               params, query, fragment))
        segments = bpath.split('/')[:-1] + path.split('/')
        # XXX The stuff below is bogus in various ways...
        if segments[-1] == '.':
            segments[-1] = ''
        while '.' in segments:
            segments.remove('.')
        while 1:
            i = 1
            n = len(segments) - 1
            while i < n:
                if (segments[i] == '..'
                    and segments[i-1] not in ('', '..')):
                    del segments[i-1:i+1]
                    break
                i = i+1
            else:
                break
        if segments == ['', '..']:
            segments[-1] = ''
        elif len(segments) >= 2 and segments[-1] == '..':
            segments[-2:] = ['']
        return self.unparse((scheme, netloc, '/'.join(segments),
                            params, query, fragment))

urlhandler = URLHandler(None, None)
myurljoin = urlhandler.join
myurlunparse = urlhandler.unparse
myurlunsplit = urlhandler.unsplit

def json_safe_coerce(value, encoding='utf-8'):
    if isinstance(value, dict):
        return dict((k, json_safe_coerce(v)) for k, v in value.iteritems())
    elif isinstance(value, (unicode, int, long, float, type(None))):
        return value
    elif isinstance(value, str):
        return value.decode(encoding)
    elif isinstance(value, Decimal):
        return float(value)
    else:
        i = None
        try:
            i = iter(value)
        except:
            pass
        if i is not None:
            return list(json_safe_coerce(v) for v in i)
    return unicode(value)

def is_nonmobile_email_address(mail_address):
    detector = get_current_registry().queryUtility(IMobileCarrierDetector)
    try:
        return _detect_from_email_address(detector, mail_address).is_nonmobile
    except ValueError:
        return True
