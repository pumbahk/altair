import six
import hmac
import uuid
import time
import json
import logging
import urllib
import urllib2
import urlparse
import hashlib
import socket
from zope.interface import implementer
from datetime import datetime

from .interfaces import IRakutenOAuth, IRakutenIDAPI, IRakutenIDAPIFactory, IRakutenIDAPI2, IRakutenIDAPI2Factory

logger = logging.getLogger(__name__)

def create_signature_base(method, url, oauth_consumer_key, oauth_token, oauth_signature_method, oauth_timestamp, oauth_nonce, oauth_version, form_params):
    params = sorted(form_params + [
        (u"oauth_consumer_key", oauth_consumer_key),
        (u"oauth_token", oauth_token),
        (u"oauth_signature_method", oauth_signature_method),
        (u"oauth_timestamp", oauth_timestamp),
        (u"oauth_nonce", oauth_nonce),
        (u"oauth_version", oauth_version),
    ])
    logger.debug('params: %r' % params)
    msg = '&'.join(urllib.quote(c, safe='') for c in [method.encode('utf-8'), url.encode('utf-8'), urllib.urlencode([(k.encode('utf-8'), v.encode('utf-8')) for k, v in params])])
    logger.debug("oauth base: %s" % msg)
    return msg


def create_oauth_signature(method, url, oauth_consumer_key, secret, oauth_token, oauth_signature_method, oauth_timestamp, oauth_nonce, oauth_version, form_params):
    logger.debug("consumer_key=%s, consumer_secret=%s" % (oauth_consumer_key, secret))
    msg = create_signature_base(method, url, oauth_consumer_key, oauth_token, oauth_signature_method, oauth_timestamp, oauth_nonce, oauth_version, form_params)
    if isinstance(secret, six.text_type):
        secret = secret.encode('utf-8')
    oauth_signature = hmac.new(secret, msg, hashlib.sha1).digest().encode('base64')
    return oauth_signature.strip()


class RakutenOAuthNegotiationError(Exception):
    pass


class RakutenIDAPIError(Exception):
    pass


@implementer(IRakutenOAuth)
class RakutenOAuth(object):
    @staticmethod
    def parse_access_token_response(response):
        return dict([(key, value[0]) for key, value in urlparse.parse_qs(response).items()])

    def __init__(self, endpoint, consumer_key, secret, timeout=10):
        self.endpoint = endpoint
        self.consumer_key = consumer_key
        self.secret = secret
        self.timeout = int(timeout)

    def get_access_token(self, request, oauth_token):
        method = u'GET'
        oauth_timestamp = six.text_type(int(time.time() * 1000))
        oauth_nonce = uuid.uuid4().hex
        oauth_signature_method = u'HMAC-SHA1'
        oauth_version = u'1.0'
        consumer_key = self.consumer_key
        if callable(consumer_key):
            consumer_key = consumer_key(request)
        secret = self.secret
        if callable(secret):
            secret = secret(request)
        oauth_signature = create_oauth_signature(
            method,
            self.endpoint,
            consumer_key,
            secret + '&',
            oauth_token,
            oauth_signature_method,
            oauth_timestamp,
            oauth_nonce,
            oauth_version,
            []
            )

        params = [
            (u'oauth_consumer_key', consumer_key),
            (u'oauth_token', oauth_token),
            (u'oauth_signature_method', oauth_signature_method),
            (u'oauth_timestamp', oauth_timestamp),
            (u'oauth_nonce', oauth_nonce),
            (u'oauth_version', oauth_version),
            (u'oauth_signature', oauth_signature),
            ]

        request_url = self.endpoint + '?' + urllib.urlencode([(k.encode('utf-8'), v.encode('utf-8')) for k, v in params])
        logger.debug("getting access token: %s" % request_url)
        logger.debug("request to %s timeout=%d" % (request_url, self.timeout))
        request_start_time = datetime.now()
        try:
            f = urllib2.urlopen(request_url, timeout=self.timeout)
            try:
                response_body = f.read()
            except socket.timeout:
                logger.warn(u'socket timeout occuued dureing reading %s' %  request_url)
            finally:
                f.close()
        except urllib2.HTTPError as e:
            logger.warn(u'get_access_token urlopen error: %s %s %s' % (request_url, e.code, e.reason))
        except urllib2.URLError as e:
            logger.warn(u'get_access_token urlopen error: %s %s' % (request_url, e.reason))
        except socket.timeout:
            logger.warn(u'get_access_token socket timeout occured: %s' % request_url)

        finally:
            elapsed = datetime.now() - request_start_time
            logger.info('[Elapsed] %ss : get_access_token : request to %s completed' % (elapsed.total_seconds(), request_url))

        logger.debug('raw access token : %s' % response_body)
        retval = self.parse_access_token_response(response_body)
        if 'oauth_token' not in retval:
            raise RakutenOAuthNegotiationError(retval)
        return retval

@implementer(IRakutenIDAPI)
class RakutenIDAPI(object):
    def __init__(self, endpoint, consumer_key, secret, access_token, encoding='utf-8', timeout=10):
        self.endpoint = endpoint
        self.consumer_key = consumer_key
        self.secret = secret
        self.oauth_token = access_token['oauth_token']
        self.oauth_token_secret = access_token['oauth_token_secret']
        self.timeout = int(timeout)
        self.encoding = encoding

    def parse_rakutenid_basicinfo(self, response):
        return dict([tuple(six.text_type(c, self.encoding) for c in line.split(":", 1)) for line in response.split("\n")])

    def parse_rakutenid_pointaccount(self, response):
        return dict([tuple(six.text_type(c, self.encoding) for c in line.split(":", 1)) for line in response.split("\n")])

    def call_rakutenid_api(self, rakuten_oauth_api):
        method = "GET"
        oauth_timestamp = six.text_type(int(time.time() * 1000))
        oauth_nonce = uuid.uuid4().hex
        oauth_signature_method = 'HMAC-SHA1'
        oauth_version = '1.0'
        oauth_signature = create_oauth_signature(
            method,
            self.endpoint,
            self.consumer_key,
            self.secret + '&' + self.oauth_token_secret,
            self.oauth_token,
            oauth_signature_method,
            oauth_timestamp,
            oauth_nonce,
            oauth_version,
            [(u'rakuten_oauth_api', rakuten_oauth_api)]
            )

        params = [
            (u'oauth_consumer_key', self.consumer_key),
            (u'oauth_token', self.oauth_token),
            (u'oauth_signature_method', oauth_signature_method),
            (u'oauth_timestamp', oauth_timestamp),
            (u'oauth_nonce', oauth_nonce),
            (u'oauth_version', oauth_version),
            (u'oauth_signature', oauth_signature),
            (u'rakuten_oauth_api', rakuten_oauth_api),
            ]

        request_url = self.endpoint + '?' + urllib.urlencode([(k.encode('utf-8'), v.encode('utf-8')) for k, v in params])
        logger.debug("get user_info: %s" % request_url)
        logger.debug("request to %s timeout=%d" % (request_url, self.timeout))
        request_start_time = datetime.now()
        try:
            f = urllib2.urlopen(request_url, timeout=self.timeout)
            try:
                response_body = f.read()
            except socket.timeout:
                logger.warn('socket timeout occured in reading: %s' % (request_url))
        except urllib2.HTTPError as e:
            try:
                response_body = e.read()
                raise RakutenIDAPIError('error occurred during calling %s; code=%s, payload=%r' % (request_url, e.code, response_body))
            finally:
                e.close()
        except urllib2.URLError as e:
            raise RakutenIDAPIError('error occurred during calling %s; reason=%r' % (request_url, e.reason))
        except socket.timeout:
            RakutenIDAPIError('socket timeout occured: %s' % (request_url))
        finally:
            f.close()
            elapsed = datetime.now() - request_start_time
            logger.info('[Elapsed] %ss : call_rakutenid_api : request to %s completed' % (elapsed.total_seconds(), request_url))

        return response_body

    def get_basic_info(self):
        return self.parse_rakutenid_basicinfo(self.call_rakutenid_api('rakutenid_basicinfo'))

    def get_contact_info(self):
        return self.parse_rakutenid_basicinfo(self.call_rakutenid_api('rakutenid_contactinfo'))

    def get_point_account(self):
        return self.parse_rakutenid_pointaccount(self.call_rakutenid_api('rakutenid_pointaccount'))


@implementer(IRakutenIDAPI2)
class RakutenIDAPI2(object):
    def __init__(self, access_token, encoding='utf-8', timeout=10):
        self.access_token = access_token
        self.encoding = encoding
        self.timeout = int(timeout)

    def call_oauth2_api(self, url, additional_params=None):
        params = {u'access_token': self.access_token}
        if additional_params:
            params.update(additional_params)
        req = urllib2.Request(url, urllib.urlencode([(six.text_type(k).encode(self.encoding), six.text_type(v).encode(self.encoding)) for k, v in params.items()]))
        data = payload = res = None
        try:
            request_start_time = datetime.now()
            logger.debug("request to %s timeout=%d", (url, self.timeout))
            try:
                res = urllib2.urlopen(req, timeouti = self.timeout)
                payload = res.read()
                data = json.loads(payload, encoding=self.encoding)
            except urllib2.HTTPError as res:
                payload = res.read()
                data = json.loads(payload, encoding=self.encoding)
            except urllib2.URLError as res:
                raise RakutenIDAPIError("error occurred during calling %s: reason=%s" % (url, e.reason))
            except socket.timeout:
                raise RakutenIDAPIError("socket timeout occurred during calling %s:" % (url))
            finally:
                res.close()
                elapsed = datetime.now() - request_start_time
                logger.info('[Elapsed] %ss : call_oauth2_api : request to %s completed' % (elapsed.total_seconds(), url))
        except Exception as e:
            raise RakutenIDAPIError("error occurred during calling %s: payload=%r, original_exception=%r" % (url, data or payload, e))
        if isinstance(res, urllib2.HTTPError):
            raise RakutenIDAPIError("error occurred during calling %s: code=%s, payload=%r" % (url, res.code, data or payload))
        return data

    def get_open_id(self):
        result = self.call_oauth2_api(u'https://app.rakuten.co.jp/services/api/IdInformation/GetOpenID/20110601')
        if "openId" in result:
            return result["openId"]
        else:
            raise RakutenIDAPIError("Not supported")

    def get_basic_info(self):
        return self.call_oauth2_api(u'https://app.rakuten.co.jp/engine/api/MemberInformation/GetBasicInfo/20110901')

    def get_user_info(self):
        return self.call_oauth2_api(u'https://app.rakuten.co.jp/engine/api/MemberInformation/GetUserInfo/20130831')

    def get_point_accounts(self, term_point_summary_type=1):
        result = self.call_oauth2_api(u'https://app.rakuten.co.jp/engine/api/MemberInformation/GetPointSummary/20130110', dict(term_point_summary_type=term_point_summary_type))
        return result[u'data']


def get_oauth_consumer_key_from_config(config, prefix):
    settings = config.registry.settings
    consumer_key_builder = settings.get(prefix + 'oauth.consumer_key_builder')
    if consumer_key_builder is not None:
        consumer_key_builder = consumer_key_builder.strip()
    if not consumer_key_builder:
        consumer_key = settings[prefix + 'oauth.consumer_key']
    else:
        consumer_key = config.maybe_dotted(consumer_key_builder)
    return consumer_key

def get_oauth_consumer_secret_from_config(config, prefix):
    settings = config.registry.settings
    consumer_secret_builder = settings.get(prefix + 'oauth.consumer_secret_builder')
    if consumer_secret_builder is not None:
        consumer_secret_builder = consumer_secret_builder.strip()
    if not consumer_secret_builder:
        consumer_secret = settings[prefix + 'oauth.secret']
    else:
        consumer_secret = config.maybe_dotted(consumer_secret_builder)
    return consumer_secret

def rakuten_oauth_from_config(config, prefix):
    settings = config.registry.settings
    consumer_key = get_oauth_consumer_key_from_config(config, prefix)
    consumer_secret = get_oauth_consumer_secret_from_config(config, prefix)
    return RakutenOAuth(
        endpoint=settings[prefix + 'oauth.endpoint.access_token'],
        consumer_key=consumer_key,
        secret=consumer_secret,
        timeout=settings[prefix + 'timeout']
        )

def rakuten_id_api_factory_from_config(config, prefix):
    settings = config.registry.settings
    _consumer_key = get_oauth_consumer_key_from_config(config, prefix)
    _consumer_secret = get_oauth_consumer_secret_from_config(config, prefix)
    def factory(request, access_token):
        consumer_key = _consumer_key
        consumer_secret = _consumer_secret
        if callable(consumer_key):
            consumer_key = consumer_key(request)
        if callable(consumer_secret):
            consumer_secret = consumer_secret(request)
        return RakutenIDAPI(
            endpoint=settings[prefix + 'oauth.endpoint'],
            consumer_key=consumer_key,
            secret=consumer_secret,
            access_token=access_token,
            encoding=settings.get(prefix + 'oauth.encoding', 'utf-8'),
            timeout=settings[prefix + 'timeout']
            )
    return factory

def rakuten_id_api2_factory_from_config(config, prefix):
    settings = config.registry.settings
    def factory(request, access_token):
        return RakutenIDAPI2(
            access_token=access_token,
            encoding=settings.get(prefix + 'oauth.encoding', 'utf-8'),
            timeout=settings[prefix + 'timeout']
            )
    return factory

def includeme(config):
    from . import CONFIG_PREFIX
    config.registry.registerUtility(
        rakuten_oauth_from_config(config, CONFIG_PREFIX),
        IRakutenOAuth
        )
    config.registry.registerUtility(
        rakuten_id_api_factory_from_config(config, CONFIG_PREFIX),
        IRakutenIDAPIFactory
        )
    config.registry.registerUtility(
        rakuten_id_api2_factory_from_config(config, CONFIG_PREFIX),
        IRakutenIDAPI2Factory
        )
