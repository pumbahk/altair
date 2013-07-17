import hmac
import uuid
import time
import logging
import urllib
import urllib2
import urlparse
import hashlib
from zope.interface import implementer

from .interfaces import IRakutenOAuth, IRakutenIDAPI, IRakutenIDAPIFactory

logger = logging.getLogger(__name__)

def create_signature_base(method, url, oauth_consumer_key, secret, oauth_token, oauth_signature_method, oauth_timestamp, oauth_nonce, oauth_version, form_params):
    params = sorted(form_params + [
        ("oauth_consumer_key", oauth_consumer_key),
        ("oauth_token", oauth_token),
        ("oauth_signature_method", oauth_signature_method),
        ("oauth_timestamp", str(oauth_timestamp)),
        ("oauth_nonce", oauth_nonce),
        ("oauth_version", oauth_version), 
    ])

    msg = method + "&" + urllib.quote(url, safe="") + "&" + urllib.quote(urllib.urlencode(params), safe="")
    logger.debug("oauth base: %s" % msg)
    return msg


def create_oauth_signature(method, url, oauth_consumer_key, secret, oauth_token, oauth_signature_method, oauth_timestamp, oauth_nonce, oauth_version, form_params):
    msg = create_signature_base(method, url, oauth_consumer_key, secret, oauth_token, oauth_signature_method, oauth_timestamp, oauth_nonce, oauth_version, form_params)
    logger.debug("secret: %s" % secret)
    oauth_signature = hmac.new(secret, msg, hashlib.sha1).digest().encode('base64')
    return oauth_signature.strip()


@implementer(IRakutenOAuth)
class RakutenOAuth(object):
    @staticmethod
    def parse_access_token_response(response):
        return dict([(key, value[0]) for key, value in urlparse.parse_qs(response).items()])

    def __init__(self, endpoint, consumer_key, secret, timeout=10):
        self.endpoint = endpoint
        self.consumer_key = consumer_key
        self.secret = secret + '&'
        self.timeout = int(timeout)

    def get_access_token(self, oauth_token):
        method = "GET"
        oauth_timestamp = int(time.time() * 1000)
        oauth_nonce = uuid.uuid4().hex
        oauth_signature_method = 'HMAC-SHA1'
        oauth_version = '1.0'
        oauth_signature = create_oauth_signature(
            method,
            self.endpoint,
            self.consumer_key,
            self.secret, 
            oauth_token,
            oauth_signature_method,
            oauth_timestamp,
            oauth_nonce,
            oauth_version,
            []
            )

        params = [
            ("oauth_consumer_key", self.consumer_key),
            ("oauth_token", oauth_token),
            ("oauth_signature_method", oauth_signature_method),
            ("oauth_timestamp", oauth_timestamp),
            ("oauth_nonce", oauth_nonce),
            ("oauth_version", oauth_version),
            ("oauth_signature", oauth_signature),
        ]
        
        request_url = self.endpoint + '?' + urllib.urlencode(params)
        logger.debug("getting access token: %s" % request_url)
        f = urllib2.urlopen(request_url, timeout=self.timeout)
        try:
            response_body = f.read()
        finally:
            f.close()

        logger.debug('raw access token : %s' % response_body)
        return self.parse_access_token_response(response_body)


@implementer(IRakutenIDAPI)
class RakutenIDAPI(object):
    def __init__(self, endpoint, consumer_key, secret, access_token, timeout=10):
        self.endpoint = endpoint
        self.consumer_key = consumer_key
        self.access_token = access_token['oauth_token']
        self.secret = secret + '&' + access_token['oauth_token_secret']
        self.timeout = int(timeout)

    @staticmethod
    def parse_rakutenid_basicinfo(response):
        return dict([line.split(":", 1) for line in response.split("\n")])

    @staticmethod
    def parse_rakutenid_pointaccount(response):
        return dict([line.split(":", 1) for line in response.split("\n")])

    def call_rakutenid_api(self, rakuten_oauth_api):
        method = "GET"
        oauth_timestamp = int(time.time() * 1000)
        oauth_nonce = uuid.uuid4().hex
        oauth_signature_method = 'HMAC-SHA1'
        oauth_version = '1.0'
        oauth_signature = create_oauth_signature(
            method,
            self.endpoint,
            self.consumer_key,
            self.secret,
            self.access_token,
            oauth_signature_method,
            oauth_timestamp,
            oauth_nonce,
            oauth_version, 
            [("rakuten_oauth_api", rakuten_oauth_api)]
            )

        params = [
            ("oauth_consumer_key", self.consumer_key),
            ("oauth_token", self.access_token),
            ("oauth_signature_method", oauth_signature_method),
            ("oauth_timestamp", oauth_timestamp),
            ("oauth_nonce", oauth_nonce),
            ("oauth_version", oauth_version),
            ("oauth_signature", oauth_signature),
            ("rakuten_oauth_api", rakuten_oauth_api),
        ]

        request_url = self.endpoint + '?' + urllib.urlencode(params)
        logger.debug("get user_info: %s" % request_url)
        f = urllib2.urlopen(request_url, timeout=self.timeout)
        try:
            response_body = f.read()
        except urllib2.HTTPError, e:
            logger.debug("get user info error : %s" % e.read())
            raise e
        finally:
            f.close()

        return response_body

    def get_basic_info(self):
        return self.parse_rakutenid_basicinfo(self.call_rakutenid_api('rakutenid_basicinfo'))

    def get_contact_info(self):
        return self.parse_rakutenid_basicinfo(self.call_rakutenid_api('rakutenid_contactinfo'))

    def get_point_account(self):
        return self.parse_rakutenid_pointaccount(self.call_rakutenid_api('rakutenid_pointaccount'))

def rakuten_oauth_from_settings(settings, prefix):
    return RakutenOAuth(
        endpoint=settings[prefix + 'oauth.endpoint.access_token'],
        consumer_key=settings[prefix + 'oauth.consumer_key'],
        secret=settings[prefix + 'oauth.secret'],
        timeout=settings[prefix + 'timeout']
        )

def rakuten_id_api_factory_from_settings(settings, prefix):
    def factory(access_token):
        return RakutenIDAPI(
            endpoint=settings[prefix + 'oauth.endpoint'],
            consumer_key=settings[prefix + 'oauth.consumer_key'],
            secret=settings[prefix + 'oauth.secret'],
            access_token=access_token,
            timeout=settings[prefix + 'timeout']
            )
    return factory

def includeme(config):
    from . import CONFIG_PREFIX
    config.registry.registerUtility(
        rakuten_oauth_from_settings(config.registry.settings, CONFIG_PREFIX),
        IRakutenOAuth
        )
    config.registry.registerUtility(
        rakuten_id_api_factory_from_settings(
            config.registry.settings, CONFIG_PREFIX),
       IRakutenIDAPIFactory
       )
