# -*- coding:utf-8 -*-
import logging
import urllib
import urllib2
import time
import uuid
import six
import hmac
import json
import hashlib
from urlparse import urljoin
from zope.interface import implementer

from .interfaces import IFanclubOAuth, IFanclubAPI, IFanclubAPIFactory
from .exceptions import FanclubAuthError, FanclubAPIError
from . import CONFIG_PREFIX

logger = logging.getLogger(__name__)


def setting_for_stg_if_need(auth_req, request):
    import ssl
    import base64
    context = None
    username = request.registry.settings.get(CONFIG_PREFIX + 'stg_setting.basic_username', None)
    password = request.registry.settings.get(CONFIG_PREFIX + 'stg_setting.basic_password', None)
    if username and password:
        context = ssl._create_unverified_context()
        base64string = base64.b64encode('%s:%s' % (username, password))
        auth_req.add_header("Authorization", "Basic %s" % base64string)
    return auth_req, context

def create_signature_base(method, url, oauth_consumer_key, oauth_signature_method, oauth_timestamp, oauth_nonce, oauth_callback, oauth_verifier, oauth_token):
    if oauth_callback:
        logger.debug('creating signature base to get request_token...')
        params = sorted([
            (u"oauth_consumer_key", oauth_consumer_key),
            (u"oauth_signature_method", oauth_signature_method),
            (u"oauth_timestamp", oauth_timestamp),
            (u"oauth_nonce", oauth_nonce),
            (u"oauth_callback", oauth_callback),
        ])
    elif oauth_verifier and oauth_token:
        logger.debug('creating signature base to get access_token...')
        params = sorted([
            (u"oauth_consumer_key", oauth_consumer_key),
            (u"oauth_signature_method", oauth_signature_method),
            (u"oauth_timestamp", oauth_timestamp),
            (u"oauth_nonce", oauth_nonce),
            (u"oauth_verifier", oauth_verifier),
            (u"oauth_token", oauth_token)
        ])
    elif not oauth_verifier and oauth_token:
        logger.debug('creating signature base for resource API')
        params = sorted([
            (u"oauth_consumer_key", oauth_consumer_key),
            (u"oauth_signature_method", oauth_signature_method),
            (u"oauth_timestamp", oauth_timestamp),
            (u"oauth_nonce", oauth_nonce),
            (u"oauth_token", oauth_token)
        ])
    logger.debug('params: %r' % params)
    msg = '&'.join(urllib.quote(c, safe='') for c in [method.encode('utf-8'), url.encode('utf-8'), urllib.urlencode([(k.encode('utf-8'), v.encode('utf-8')) for k, v in params])])
    logger.debug("oauth base: %s" % msg)
    return msg


def create_oauth_signature(method, url, oauth_consumer_key, secret, oauth_signature_method, oauth_timestamp, oauth_nonce, oauth_callback=None, oauth_verifier=None, oauth_token=None):
    logger.debug("consumer_key=%s, consumer_secret=%s" % (oauth_consumer_key, secret))
    msg = create_signature_base(
        method,
        url,
        oauth_consumer_key,
        oauth_signature_method,
        oauth_timestamp,
        oauth_nonce,
        oauth_callback,
        oauth_verifier,
        oauth_token
    )
    if isinstance(secret, six.text_type):
        secret = secret.encode('utf-8')
    oauth_signature = hmac.new(secret, msg, hashlib.sha1).digest().encode('base64')
    return oauth_signature.strip()


@implementer(IFanclubOAuth)
class FanclubOAuth(object):
    def __init__(self, consumer_key, secret, endpoint_builder, timeout=10):
        self.consumer_key = consumer_key
        self.secret = secret
        self.timeout = int(timeout)
        self.endpoint_builder = endpoint_builder

    def get_access_token(self, request, request_token, request_token_secret, verifier):
        endpoint = self.endpoint_builder.access_token_endpoint(request)
        consumer_key = self.consumer_key
        if callable(consumer_key):
            consumer_key = consumer_key(request)
        consumer_secret = self.secret
        if callable(consumer_secret):
            consumer_secret = consumer_secret(request)

        oauth_signature_method = u'HMAC-SHA1'
        oauth_timestamp = six.text_type(int(time.time() * 1000))
        oauth_nonce = uuid.uuid4().hex

        req_signature = create_oauth_signature(
            method=u'GET',
            url=endpoint,
            oauth_consumer_key=consumer_key,
            secret=consumer_secret + '&' + request_token_secret,
            oauth_signature_method=oauth_signature_method,
            oauth_timestamp=oauth_timestamp,
            oauth_nonce=oauth_nonce,
            oauth_token=request_token,
            oauth_verifier=verifier
        )

        req_query = [
            (u'oauth_consumer_key', consumer_key),
            (u'oauth_signature_method', oauth_signature_method),
            (u'oauth_timestamp', oauth_timestamp),
            (u'oauth_nonce', oauth_nonce),
            (u'oauth_signature', req_signature),
            (u'oauth_token', request_token),
            (u'oauth_verifier', verifier)
            ]

        url = endpoint + '?' + urllib.urlencode([(k.encode('utf-8'), v.encode('utf-8')) for k, v in req_query])
        try:
            f = None
            logger.info('try request to get access token. (url={})'.format(url))
            opener = urllib2.build_opener(urllib2.HTTPSHandler())
            urllib2.install_opener(opener)
            auth_req = urllib2.Request(url)
            # FIXME: polluxSTG環境は証明書があれなのとbasic認証をくぐり抜けないといけない
            auth_req, context = setting_for_stg_if_need(auth_req, request)
            f = urllib2.urlopen(auth_req, context=context)
            res = json.loads(f.read())
        except Exception as e:
            logger.error(e.message)
            raise FanclubAuthError('failed to get access token (url={})'.format(url))
        finally:
            if f:
                f.close()

        return res['data']['oauth_token'], res['data']['oauth_token_secret']

    def get_request_token(self, request, callback_url):
        endpoint = self.endpoint_builder.request_token_endpoint(request)
        consumer_key = self.consumer_key
        if callable(consumer_key):
            consumer_key = consumer_key(request)
        consumer_secret = self.secret
        if callable(consumer_secret):
            consumer_secret = consumer_secret(request)

        oauth_signature_method = u'HMAC-SHA1'
        oauth_timestamp = six.text_type(int(time.time() * 1000))
        oauth_nonce = uuid.uuid4().hex

        req_signature = create_oauth_signature(
            method=u'GET',
            url=endpoint,
            oauth_consumer_key=consumer_key,
            secret=consumer_secret + '&',
            oauth_signature_method=oauth_signature_method,
            oauth_timestamp=oauth_timestamp,
            oauth_nonce=oauth_nonce,
            oauth_callback=callback_url
        )

        req_query = [
            (u'oauth_consumer_key', consumer_key),
            (u'oauth_signature_method', oauth_signature_method),
            (u'oauth_timestamp', oauth_timestamp),
            (u'oauth_nonce', oauth_nonce),
            (u'oauth_signature', req_signature),
            (u'oauth_callback', callback_url)
            ]

        data = urllib.urlencode([(k.encode('utf-8'), v.encode('utf-8')) for k, v in req_query])
        try:
            f = None
            url = endpoint + '?' + data
            logger.info('try request to get request token. (url={})'.format(url))
            opener = urllib2.build_opener(urllib2.HTTPSHandler())
            urllib2.install_opener(opener)
            auth_req = urllib2.Request(url)
            # FIXME:
            auth_req, context = setting_for_stg_if_need(auth_req, request)
            f = urllib2.urlopen(auth_req, context=context)
            res = json.loads(f.read())
        except Exception as e:
            logger.error(e.message)
            raise FanclubAuthError('failed to get request token (url={})'.format(url))
        finally:
            if f:
                f.close()

        return res['data']['oauth_token'], res['data']['oauth_token_secret']


@implementer(IFanclubAPI)
class FanclubAPI(object):
    def __init__(self, request, endpoint_builder, consumer_key, consumer_secret, token, secret):
        self.request = request
        self.endpoint_builder = endpoint_builder
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = token
        self.access_secret = secret

    def get_member_info(self):
        endpoint = self.endpoint_builder.member_info_endpoint(self.request)
        consumer_key = self.consumer_key
        if callable(consumer_key):
            consumer_key = consumer_key(self.request)
        consumer_secret = self.consumer_secret
        if callable(consumer_secret):
            consumer_secret = consumer_secret(self.request)

        oauth_signature_method = u'HMAC-SHA1'
        oauth_timestamp = six.text_type(int(time.time() * 1000))
        oauth_nonce = uuid.uuid4().hex

        signature = create_oauth_signature(
            method=u'GET',
            url=endpoint,
            oauth_consumer_key=consumer_key,
            secret=consumer_secret + '&' + self.access_secret,
            oauth_signature_method=oauth_signature_method,
            oauth_timestamp=oauth_timestamp,
            oauth_nonce=oauth_nonce,
            oauth_token=self.access_token
        )

        query = [
            (u'oauth_consumer_key', consumer_key),
            (u'oauth_signature_method', oauth_signature_method),
            (u'oauth_timestamp', oauth_timestamp),
            (u'oauth_nonce', oauth_nonce),
            (u'oauth_signature', signature),
            (u'oauth_token', self.access_token)
            ]

        url = endpoint + '?' + urllib.urlencode([(k.encode('utf-8'), v.encode('utf-8')) for k, v in query])
        try:
            f = None
            context = None
            logger.info('try request to get member info. (url={})'.format(url))
            opener = urllib2.build_opener(urllib2.HTTPSHandler())
            urllib2.install_opener(opener)
            auth_req = urllib2.Request(url)
            # FIXME:
            auth_req, context = setting_for_stg_if_need(auth_req, self.request)
            f = urllib2.urlopen(auth_req, context=context)
            res = json.loads(f.read())
            if res.get('code') == 200:
                res = res.get('data')
            else:
                raise FanclubAPIError('API call error (pollux member_data API error_code={})'.format(res.get('code')))
        except Exception as e:
            logger.error(e.message)
            raise FanclubAPIError('failed to get member info. (url={})'.format(url))
        finally:
            if f:
                f.close()

        return res


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


def fanclub_oauth_from_config(config, prefix):
    settings = config.registry.settings
    consumer_key = get_oauth_consumer_key_from_config(config, prefix)
    consumer_secret = get_oauth_consumer_secret_from_config(config, prefix)
    endpoint_builder_factory = config.maybe_dotted(settings[prefix + 'endpoint_builder_factory'])
    endpoint_builder = endpoint_builder_factory()
    return FanclubOAuth(
        consumer_key=consumer_key,
        secret=consumer_secret,
        timeout=settings[prefix + 'timeout'],
        endpoint_builder=endpoint_builder
        )


def fanclub_api_factory_from_config(config, prefix):
    settings = config.registry.settings

    def factory(request, access_token, access_secret):
        endpoint_builder_factory = config.maybe_dotted(settings[prefix + 'endpoint_builder_factory'])
        endpoint_builder = endpoint_builder_factory()
        return FanclubAPI(
            request=request,
            endpoint_builder=endpoint_builder,
            consumer_key=get_oauth_consumer_key_from_config(config, prefix),
            consumer_secret=get_oauth_consumer_secret_from_config(config, prefix),
            token=access_token,
            secret=access_secret
        )
    return factory


def includeme(config):
    from . import CONFIG_PREFIX
    config.registry.registerUtility(
        fanclub_oauth_from_config(config, CONFIG_PREFIX),
        IFanclubOAuth
        )
    config.registry.registerUtility(
        fanclub_api_factory_from_config(config, CONFIG_PREFIX),
        IFanclubAPIFactory
        )

