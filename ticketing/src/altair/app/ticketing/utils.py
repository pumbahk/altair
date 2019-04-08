# -*- coding:utf-8 -*-
import functools

import six
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, padding, ciphers
from cryptography.hazmat.primitives.ciphers import algorithms, modes

import pytz
import random
import re
import sys
import urllib

from csv import writer as csv_writer, QUOTE_ALL
from datetime import date, datetime
from urlparse import uses_relative, uses_netloc, urlparse
from decimal import Decimal
from standardenum import StandardEnum

from pyramid.response import Response
from pyramid.threadlocal import get_current_registry

from altair.mobile.interfaces import IMobileCarrierDetector
from altair.mobile.api import _detect_from_email_address


__all__ = [
    'DigitCodec',
    'encoder',
    'sensible_alnum_encode',
    'sensible_alnum_decode',
    'URLHandler',
    'urlhandler',
    'myurljoin',
    'myurlunparse',
    'myurlunsplit',
    'json_safe_coerce',
    'is_nonmobile_email_address',
    'dereference',
    'iterpairs',
    'is_sequence',
    'uniurlencode',
    'memoize',
    'Crypto',
]

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

def dereference(object, key, return_none_unless_feasible=False):
    tokens = re.finditer(ur'([a-zA-Z_][a-zA-Z0-9_]*)|([0-9]+)|([[\].])', key)

    try:
        token = tokens.next()
    except StopIteration:
        raise ValueError('empty expression')

    # state 0: expecting identifier or number
    identifier_or_number = token and (token.group(1) or (token.group(2) and int(token.group(2))))
    if identifier_or_number is None:
        raise ValueError('identifier or number expected')

    try:
        object = object[identifier_or_number]
    except KeyError:
        if return_none_unless_feasible:
            return None
        else:
            raise

    while True:
        try:
            token = tokens.next()
        except StopIteration:
            break

        # state 1: expecting dot or lbrace
        delimiter = token.group(3)
        if delimiter == u'.':
            try:
                token = tokens.next()
            except StopIteration:
                token = None

            identifier = token and token.group(1)
            if identifier is None:
                raise ValueError('identifier expected')

            try:
                object = getattr(object, identifier)
            except AttributeError:
                if return_none_unless_feasible:
                    return None
                else:
                    raise
        elif delimiter == u'[':
            # state 2: expecting identifier or number
            identifier_or_number = []

            while True:
                try:
                    token = tokens.next()
                except StopIteration:
                    token = None
                if token is not None:
                    identifier = token.group(1)
                    number = token.group(2)
                    delimiter = token.group(3)
                else:
                    identifier = number = None
                    delimiter = u''

                if identifier is not None:
                    identifier_or_number.append((1, identifier))
                elif number is not None:
                    identifier_or_number.append((2, number))
                elif delimiter == u'.':
                    identifier_or_number.append((3, delimiter))
                elif delimiter == u']':
                    break
                else:
                    raise ValueError('] expected')

            if identifier_or_number:
                if len(identifier_or_number) == 1:
                    if identifier_or_number[0][0] == 2:
                        identifier_or_number = int(identifier_or_number[0][1])
                    else:
                        identifier_or_number = identifier_or_number[0][1]
                else:
                    identifier_or_number = u''.join(c[1] for c in identifier_or_number)

            if not identifier_or_number:
                raise ValueError('identifier or number expected')

            try:
                object = object[identifier_or_number]
            except KeyError:
                if return_none_unless_feasible:
                    return None
                else:
                    raise
        else:
            raise ValueError('. or [ expected')

    return object

def iterpairs(dictlike):
    if hasattr(dictlike, 'iteritems'):
        return dictlike.iteritems()
    elif hasattr(dictlike, 'items'):
        return dictlike.items()
    else:
        return iter(dictlike)

def is_sequence(obj):
    try:
        return len(obj)
    except TypeError:
        return False

def uniurlencode(dictlike, method='plus', encoding=None):
    if callable(method):
        quote = method
    elif method == 'raw':
        quote = urllib.quote
    elif method == 'plus':
        quote = urllib.quote_plus
    encoding = encoding or sys.getdefaultencoding()
    chunks = []
    first = True
    for pair in iterpairs(dictlike):
        try:
            if len(pair) != 2:
                raise TypeError
        except:
            raise TypeError('not a valid pairs or mapping object')
        if isinstance(pair[1], basestring):
            if not first:
                chunks.append('&')
            chunks.append(quote(pair[0].encode(encoding)))
            chunks.append('=')
            chunks.append(quote(pair[1].encode(encoding)))
            first = False
        else:
            if is_sequence(pair[1]):
                for v in pair[1]:
                    if not first:
                        chunks.append('&')
                    chunks.append(quote(pair[0].encode(encoding)))
                    if v is not None:
                        chunks.append('=')
                        chunks.append(quote(v.encode(encoding)))
                    first = False
            else:
                if not first:
                    chunks.append('&')
                chunks.append(quote(pair[0].encode(encoding)))
                if pair[1] is not None:
                    chunks.append('=')
                    chunks.append(quote(unicode(pair[1]).encode(encoding)))
                first = False
    return ''.join(chunks)

def uniurldecode(buf, method='plus', encoding=None):
    if callable(method):
        unquote = method
    elif method == 'raw':
        unquote = urllib.unquote
    elif method == 'plus':
        unquote = urllib.unquote_plus
    encoding = encoding or sys.getdefaultencoding()
    retval = []
    for _pair in buf.split('&'):
        pair = _pair.split('=', 2)
        if len(pair) == 2:
            retval.append((
                unquote(pair[0]).decode(encoding),
                unquote(pair[1]).decode(encoding)
                ))
        else:
            retval.append((
                unquote(pair[0]).decode(encoding),
                None
                ))
    return retval

def tristate(bool_or_none):
    return bool(bool_or_none) if bool_or_none is not None else None

def toutc(dt, default_tz=None):
    if dt.tzinfo is None:
        if default_tz is None:
            raise ValueError('default_tz is not given')
        dt = dt.replace(tzinfo=default_tz)
    return dt.astimezone(pytz.utc)

def todatetime(d):
    if isinstance(d, datetime):
        return d
    if not isinstance(d, date):
        raise TypeError()
    return datetime.fromordinal(d.toordinal())

def todate(d):
    if not isinstance(d, date):
        raise TypeError()
    if isinstance(d, datetime):
        return d.date()
    else:
        return d

def clear_exc(fn):
    def _(*args, **kwargs):
        sys.exc_clear()
        return fn(*args, **kwargs)
    functools.update_wrapper(_, fn)
    return _

# https://wiki.python.org/moin/PythonDecoratorLibrary#Memoize
class memoize(object):
    def __init__(self, cache_attr_name=None):
        self.cache_attr_name = cache_attr_name

    def __call__(self, fn):
        if self.cache_attr_name is None:
            cache_attr_name = '_cache_%s' % fn.__name__
        else:
            cache_attr_name = self.cache_attr_name
        @functools.wraps(fn)
        def memoizer(_self, *args, **kwargs):
            cache = getattr(_self, cache_attr_name, None)
            if cache is None:
                cache = {}
                setattr(_self, cache_attr_name, cache)
            key = (args, tuple(kwargs.items()))
            if key not in cache:
                cache[key] = fn(_self, *args, **kwargs)
            return cache[key]
        return memoizer

def moderate_name_candidates(name, max=100):
    yield name
    for i in range(0, max):
        yield u'%s (%d)' % (name, i + 1)

class DateTimeRange(object):
    def __init__(self, start, end):
        if start is not None:
            self.start = start
        else:
            self.start = datetime.min # Set min datetime in case of None

        if end is not None:
            self.end = end
        else:
            self.end = datetime.max # Set max datetime in case of None

    def __str__(self):
        return str(self.start) + " - " + str(self.end)

    def overlap(self, date_range):
        # not (self.start > date_range.end or self.end < date_range.start) <=> not (self.start > date_range.end) and not (self.end < date_range.start)
        if self.start <= date_range.end and self.end >= date_range.start:
            return True
        else:
            return False

def get_safe_filename(s):
    # euc-jpにしてから処理
    # 全角はスペース/クォート記号以外全部OK、半角は大半の記号がNG
    s = re.sub(u'[　”“’]', u'_', s)
    return re.sub(r'[^-_0-9a-zA-Z\x80-\xFF]', '_', s.encode('euc-jp', 'replace').replace('?', '_')).decode('euc-jp')

def parse_content_type(header_value):
    from email.message import Message
    m = Message()
    m['Content-Type'] = header_value
    return m.get_content_type(), m.get_charsets()[0]


def rand_string(seed, length):
    return "".join([random.choice(seed) for i in range(length)])


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    """
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)

    補足:
    数字と文字列混在のリストを人の目で見て自然な並びにソートするキー。
    Macにfinderでファイル名による昇順ソートをかけるようなイメージ。

    https://stackoverflow.com/questions/5967500/how-to-correctly-sort-a-string-with-a-number-inside
    """
    return [atoi(c) for c in re.split('(\d+)', text)]


class CSVExporter(object):
    """
    簡単のCSVファイルを出力するクラス
    シンプルな内容をCSVで出力する場合は使える

    Initialization:
        fields:List 出力内容の項目。
        filename:string は出力ファイル名（.csvを含まない）。
        filename_timestamp:bool は出力ファイル名にTime Stampを付けるかどうかのフラグ。

    Required:
        data:List 出力内容。

    Optional:
        headers:List 出力内容のヘッダー。

    Return:
        Response:pyramid.Response 戻り値はpyramidのResponseですので直接viewsの戻り値として使える

    Quick Start:

        @view_config(route_name='error_list.download')
        def download_error_list(self):
            csv_exporter = CSVExporter(fields=['order_no', 'errors'], filnename='error_list', filename_timestamp=True)

            data = [{'order_no': 'RT00000001', 'errors': u'決済方法が間違います。'},
                    {'order_no': 'RT00000002', 'errors': u'決済方法が間違います。'}]
            headers = [u'予約番号', u'エラーメッセージ']

            resp = csv_exporter(data, headers)

            return resp
    """
    def __init__(self, fields, filename=None, filename_timestamp=False):
        self.fields = fields
        self.filename = self._remove_extension(filename)
        self.filename_timestamp = filename_timestamp

    def _remove_extension(self, filename):
        if filename.endswith('.csv'):
            filename = filename.replace('.csv', '')
        return filename

    def _encode_to_cp932(self, data):
        if not hasattr(data, "encode"):
            return str(data)
        try:
            # unicode typeの文字列のみcp932の文字コードに変換られる
            if not isinstance(data, unicode):
                data = data.decode('utf-8')
            return data.replace('\r\n', '').encode('cp932')
        except UnicodeEncodeError:
            print 'cannot encode character %s to cp932' % data
            if data is not None and len(data) > 1:
                return ''.join([self._encode_to_cp932(d) for d in data])
            else:
                return '?'

    def _render_data(self, data):
        for record in data:

            items = [record[field] for field in self.fields]
            yield map(self._encode_to_cp932, items)

    def _write_file(self, body, data, headers):
        writer = csv_writer(body, delimiter=',', quoting=QUOTE_ALL)
        if headers:
            writer.writerow(map(self._encode_to_cp932, headers))

        for row in self._render_data(data):
            writer.writerow(row)

    def _build_filename(self):
        if self.filename_timestamp:
            filename = self.filename + '_{timestamp}.csv'.format(timestamp=datetime.now().strftime(u'%Y%m%d%H%M%S'))
        else:
            filename = self.filename + '.csv'
        return filename

    def __call__(self, data, headers=None):

        filename = self._build_filename()

        resp = Response(status=200, headers=[
            ('Content-Type', 'text/csv'),
            ('Content-Disposition',
             'attachment; filename={}'.format(filename))
        ])
        self._write_file(resp.body_file, data, headers)

        return resp


class Crypto(object):
    def __init__(self, key, iv, backend=None):
        self.key = key
        self.iv = iv
        self.backend = backend if backend is not None else default_backend()

    def md5_hash(self, data):
        hasher = hashes.Hash(hashes.MD5(), backend=self.backend)
        hasher.update(data)
        return hasher.finalize()

    def pad(self, data):
        p = padding.PKCS7(128).padder()
        return p.update(data) + p.finalize()

    def unpad(self, data):
        p = padding.PKCS7(128).unpadder()
        return p.update(data) + p.finalize()

    def encrypt(self, data):
        """
        メッセージを公開鍵暗号標準 PKCS#7 でパディングし、AES128-CBC 方式で暗号化します。
        """
        c = ciphers.Cipher(algorithms.AES(self.key), modes.CBC(self.iv), backend=self.backend)
        e = c.encryptor()
        return e.update(self.pad(data)) + e.finalize()

    def decrypt(self, data):
        c = ciphers.Cipher(algorithms.AES(self.key), modes.CBC(self.iv), backend=self.backend)
        e = c.decryptor()
        return self.unpad(e.update(data) + e.finalize())

    def gen_key_from_special_field_value(self, v):
        return b''.join(b'%02x' % six.byte2int(c) for c in self.md5_hash(v.encode('ASCII')))[0:16]
