import re
import hashlib
import logging
import urllib
import urllib2
from datetime import datetime

from .exceptions import SejRequestError
from .utils import JavaHashMap

logger = logging.getLogger(__name__)

def create_request_params(params, secret_key):
    xcode = create_hash_from_x_start_params(params, secret_key)
    params['xcode'] = xcode
    return params

ascii_regex = re.compile(r'[^\x20-\x7E]')

def make_sej_response(params):
    def make_senb_data(data):
        return '<SENBDATA>%s</SENBDATA>' % data

    return make_senb_data('&'.join(["%s=%s" % (k, urllib.quote(v)) for k, v in params.items()]) + '&') + \
           make_senb_data('DATA=END')

def parse_sej_response(body, tag_name):
    regex_tags = re.compile(r"<" + tag_name + ">([^<>]+)</"+tag_name+">")
    regex_params = re.compile(r"([^&=]+)=([^&=]+)")
    matches = regex_tags.findall(body)
    key_value = {}
    for match in matches:
        for key,val in regex_params.findall(match):
            key_value[key] = val
    return key_value

def create_sej_request(url, request_params):
    req = urllib2.Request(url)

    buffer = ["%s=%s" % (name, urllib.quote(unicode(param).encode('shift_jis', 'xmlcharrefreplace'))) for name, param in request_params.iteritems()]
    data = "&".join(buffer)

    logger.info("[request]\n%s\t%s" % (url, data))
    req.add_data(data)
    req.add_header('User-Agent', 'SejPaymentForJava/2.00')
    req.add_header('Connection', 'close')

    return req

def create_md5hash_from_dict(kv, secret_key):
    tmp_keys = JavaHashMap()
    key_array = list(kv.iterkeys())
    for key, value in kv.iteritems():
        tmp_keys[key.lower()] = value
    key_array.sort()
    buffer = [tmp_keys[key.lower()] for key in key_array]
    buffer.append(secret_key)
    buffer = u','.join(buffer)
    logger.debug('hash:' + buffer)
    return hashlib.md5(buffer.encode(encoding="UTF-8")).hexdigest()

def create_hash_from_x_start_params(params, secret_key):

    falsify_props = dict()
    for name,param in params.iteritems():
        if name.startswith('X_'):
            if not isinstance(param, basestring):
                raise SejRequestError(u"%s must be a string (got %s)" % (name, type(param)))
            _param = None
            try:
                _param = str(param)
            except (UnicodeDecodeError, UnicodeEncodeError):
                pass
            if _param is None or ascii_regex.search(_param):
                raise SejRequestError(u"%s must be ascii (%r)" % (name, param))
            falsify_props[name] = _param

    hash = create_md5hash_from_dict(falsify_props, secret_key)

    return hash

def build_sej_date(d):
    return '%04d%02d%02d' % (d.year, d.month, d.day) if d is not None else ''

def build_sej_datetime_without_second(dt):
    return '%04d%02d%02d%02d%02d' % (dt.year, dt.month, dt.day, dt.hour, dt.minute) if dt is not None else ''

def build_sej_datetime(dt):
    return '%04d%02d%02d%02d%02d%02d' % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second) if dt is not None else ''
