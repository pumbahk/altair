# -*- coding: utf-8 -*-
import re
import urllib2
import hashlib
import logging
from datetime import datetime

from .exceptions import SejRequestError
from .models import SejTicketType, SejPaymentType
from .utils import JavaHashMap

logger = logging.getLogger(__name__)
ascii_regex = re.compile(r'[^\x20-\x7E]')

def make_sej_response(params):
    def make_senb_data(data):
        return '<SENBDATA>%s</SENBDATA>' % data

    return make_senb_data('&'.join(["%s=%s" % (k, urllib2.quote(v)) for k, v in params.items()]) + '&') + \
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

    buffer = ["%s=%s" % (name, urllib2.quote(unicode(param).encode('shift_jis', 'xmlcharrefreplace'))) for name, param in request_params.iteritems()]
    data = "&".join(buffer)

    logger.info("[request]\n%s" % data)
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
            _param = str(param)
            result = ascii_regex.search(_param)
            if result:
                raise SejRequestError(u"%s must be ascii (%s)" % (name, _param))

            falsify_props[name] = _param

    hash = create_md5hash_from_dict(falsify_props, secret_key)

    return hash

def create_request_params(params, secret_key):
    xcode = create_hash_from_x_start_params(params, secret_key)
    params['xcode'] = xcode
    return params


def build_sej_datetime(dt):
    return '%04d%02d%02d%02d%02d%02d' % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second) if dt is not None else ''
