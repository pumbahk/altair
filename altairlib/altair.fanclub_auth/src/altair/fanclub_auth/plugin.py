# -*- coding:utf-8 -*-
import logging
import time
import uuid
import six
import re
import urllib
import urllib2
import json
from urlparse import urlparse, urlunparse, urljoin
from zope.interface import implementer
from beaker.cache import Cache, CacheManager, cache_regions
from .interfaces import IFanclubAuth
from altair.auth.interfaces import IChallenger, IAuthenticator, IMetadataProvider, ILoginHandler
from altair.httpsession.api import HTTPSession
from altair.httpsession.idgen import _generate_id
from . import AUTH_PLUGIN_NAME
from .api import get_fanclub_oauth
from pyramid.path import DottedNameResolver

from altair.mobile.interfaces import IMobileRequest
from altair.mobile.session import HybridHTTPBackend, merge_session_restorer_to_url

logger = logging.getLogger(__name__)

cache_manager = CacheManager(cache_regions=cache_regions)

class FanclubAuthHTTPSessionContext(object):
    http_backend = None

    def __init__(self, persistence_backend):
        self.persistence_backend = persistence_backend

    def on_load(self, id_, data):
        pass

    def on_new(self, id_, data):
        pass

    def on_save(self, id_, data):
        pass

    def on_delete(self, id_, data):
        pass

    def generate_id(self):
        return _generate_id()


class FanclubAuthHTTPSessionFactory(object):
    def __init__(self, persistence_backend, session_args):
        import altair.httpsession
        self.persistence_backend_factory = DottedNameResolver(altair.httpsession).maybe_resolve(persistence_backend)
        self.session_args = session_args

    def __call__(self, request, id=None):
        persistence_backend = self.persistence_backend_factory(request, **self.session_args)
        return HTTPSession(
            FanclubAuthHTTPSessionContext(persistence_backend),
            id
            )


class FanclubAuthURLBuilder(object):
    def __init__(self, proxy_url_pattern=None, **kwargs):
        self.proxy_url_pattern = proxy_url_pattern
        self.verify_url = kwargs.get('verify_url')
        self.extra_verify_url = kwargs.get('extra_verify_url')
        self.error_to_url = kwargs.get('error_to_url')
        self.return_to_url = kwargs.get('return_to_url')

    def extra_verify_url_exists(self, request):
        return True

    def build_base_url(self, request):
        return request.host_url

    def build_return_to_url(self, request):
        return urljoin(self.build_base_url(request).rstrip('/') + '/', request.route_path('fanclub_auth.verify').lstrip('/'))

    def build_error_to_url(self, request):
        return urljoin(self.build_base_url(request).rstrip('/') + '/', request.route_path('fanclub_auth.error').lstrip('/'))

    def build_verify_url(self, request):
        return request.route_url('fanclub_auth.verify')

    def build_extra_verify_url(self, request):
        return request.route_url('fanclub_auth.verify2')


@implementer(IFanclubAuth, IAuthenticator, IChallenger, ILoginHandler, IMetadataProvider)
class FanclubAuthPlugin(object):
    SESSION_KEY = '_%s_session' % __name__
    SESSION_IDENT_KEY = 'RakutenOpenIDPlugin.identity'
    EXTRA_VERIFY_KEY = '%s.raw_identifier' % __name__
    IDENT_OPENID_PARAMS_KEY = '%s.params' % __name__
    AUTHENTICATED_KEY = '%s.authenticated' % __name__
    METADATA_KEY = '%s.metadata' % __name__
    DEFAULT_CACHE_REGION_NAME = '%s.metadata' % __name__

    NS_OAUTHv1 = u'http://specs.openid.net/extenstions/oauth/1.0'
    NS_OPENIDv2 = u'http://specs.openid.net/auth/2.0'
    OPENID_IDENTIFIER_SELECT = u'http://specs.openid.net/auth/2.0/identifier_select'

    cache_manager = cache_manager

    def __init__(self,
                 plugin_name,
                 endpoint,
                 url_builder,
                 consumer_key,
                 consumer_secret,
                 session_factory,
                 cache_region=None,
                 oauth_scope=None,
                 encoding='utf-8',
                 timeout=10,
                 challenge_success_callback=None):
        if cache_region is None:
            cache_region = self.DEFAULT_CACHE_REGION_NAME
        self.name = plugin_name
        self.cache_region = cache_region
        self.url_builder = url_builder
        self.endpoint = urlparse(endpoint)
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.session_factory = session_factory
        self.oauth_scope = oauth_scope
        self.encoding = encoding
        self.timeout = int(timeout)
        self.challenge_success_callback = challenge_success_callback

    def build_endpoint_request_url(self, query, params=()):
        params_str = \
            (self.endpoint.params + u';' if self.endpoint.params else u'') \
            + u';'.join(
                six.text_type(urllib.quote(k.encode(self.encoding), safe='')) \
                + u'=' \
                + six.text_type(urllib.quote(v.encode(self.encoding), safe=''))
                for k, v in params
                )
        query_str = \
            (self.endpoint.query + u'&' if self.endpoint.query else u'') \
            + u'&'.join(
                six.text_type(urllib.quote(k.encode(self.encoding), safe='')) \
                + u'='
                + six.text_type(urllib.quote(v.encode(self.encoding), safe=''))
                for k, v in query
                )
        return urlunparse((
            self.endpoint.scheme,
            self.endpoint.netloc,
            self.endpoint.path,
            params_str,
            query_str,
            self.endpoint.fragment,
            ))

    def get_oauth_scope(self, request):
        if callable(self.oauth_scope):
            return self.oauth_scope(request)
        else:
            return self.oauth_scope

    def combine_session_id(self, request, session, url):
        q = u'?ak=' + urllib.quote(session.id)
        if IMobileRequest.providedBy(request):
            key = HybridHTTPBackend.get_query_string_key(request)
            session_restorer = HybridHTTPBackend.get_session_restorer(request)
            if key and session_restorer:
                # webobは"&"の他に";"文字もデリミタと見なしてくれる
                q += u';%s=%s' % (urllib.quote(key), urllib.quote(session_restorer))
        return urljoin(url, q)

    def new_session(self, request):
        return self.session_factory(request, id=None)

    def get_redirect_url(self, request, session):
        """ ユーザの認可リクエストエンドポイントを返す """
        return_to = self.url_builder.build_return_to_url(request)
        return_to = self.combine_session_id(request, session, return_to)
        oauth_request_token, oauth_request_secret = get_fanclub_oauth(request).get_request_token(return_to)
        # access_token取得時に使用
        session['oauth_request_secret'] = oauth_request_secret
        # xoauth_memberships_requiredは求められる会員資格を指定する場合に設定
        # カンマ区切りで複数指定可能
        query = [
            (u'oauth_token', oauth_request_token),
            (u'xoauth_memberships_required', urllib.urlencode(u''))
        ]
        return self.build_endpoint_request_url(query)

    def set_return_url(self, session, url):
        session[self.__class__.__name__ + '.return_url'] = url

    # IAuthenticator
    def authenticate(self, request, auth_context, auth_factors):
        logger.debug('Authenticate Pollux auth')
        return None, None

    # IChallenger
    def challenge(self, request, auth_context, response):
        logger.debug('Challenge Pollux auth')
        session = self.new_session(request)
        return_url = request.environ.get('altair.fanclub_auth.return_url', request.url)
        _session = request.session # Session gets created here!
        if _session is not None and IMobileRequest.providedBy(request):
            key = HybridHTTPBackend.get_query_string_key(request)
            session_restorer = HybridHTTPBackend.get_session_restorer(request)
            if key and session_restorer:
                return_url = merge_session_restorer_to_url(return_url, key, session_restorer)
        self.set_return_url(session, return_url)
        session.save()
        redirect_to = self.get_redirect_url(request, session)
        logger.debug('redirect from %s to %s' % (request.url, redirect_to))
        response.location = redirect_to
        response.status = 302
        return True

    # ILoginHandler
    def get_auth_factors(self, request, auth_context, credentials=None):
        logger.debug('GET Auth Factors Pollux auth')
        return credentials

    # IMetadataProvider
    def get_metadata(self, request, auth_context, identities):
        logger.debug('GET Metadata Pollux auth')
        pass

    def on_verify(self, request):
        import ipdb;ipdb.set_trace()
        pass

    def on_extra_verify(self, request):
        pass

    def verify_authentication(self, request, params):
        pass


def fanclub_auth_from_config(config, prefix):
    from .oauth import get_oauth_consumer_key_from_config, get_oauth_consumer_secret_from_config
    settings = config.registry.settings
    session_args = {}
    for k, v in settings.items():
        if k.startswith(prefix + 'session.'):
            session_args[k[len(prefix + 'session.'):]] = v
    persistence_backend = settings[prefix + 'session']

    consumer_key = get_oauth_consumer_key_from_config(config, prefix)
    consumer_secret = get_oauth_consumer_secret_from_config(config, prefix)
    url_builder_factory = settings.get(prefix + 'url_builder_factory')
    if url_builder_factory is None:
        verify_url = settings.get(prefix + 'verify_url')
        extra_verify_url = settings.get(prefix + 'extra_verify_url')
        error_to_url = settings.get(prefix + 'error_to_url')
        if error_to_url is None:
            error_to_url = settings.get(prefix + 'error_to')
        return_to_url = settings.get(prefix + 'return_to_url')
        if return_to_url is None:
            return_to_url = settings.get(prefix + 'return_to')
        logger.debug('{prefix}url.builder_factory is not given; verify_url={verify_url}, extra_verify_url={extra_verify_url}, error_to_url={error_to_url}, return_to={return_to_url}'.format(
            prefix=prefix,
            verify_url=verify_url,
            extra_verify_url=extra_verify_url,
            error_to_url=error_to_url,
            return_to_url=return_to_url
            ))
        url_builder = FanclubAuthURLBuilder(
            verify_url=verify_url,
            extra_verify_url=extra_verify_url,
            error_to_url=error_to_url,
            return_to_url=return_to_url
            )
    else:
        url_builder_factory = config.maybe_dotted(url_builder_factory)
        url_builder_factory_param_prefix = prefix + 'url_builder_factory.'
        params = {}
        for k, v in settings.items():
            if k.startswith(url_builder_factory_param_prefix):
                params[k[len(url_builder_factory_param_prefix):]] = v
        url_builder = url_builder_factory(**params)
    challenge_success_callback = settings.get(prefix + 'challenge_success_callback')
    if challenge_success_callback is not None and not callable(challenge_success_callback):
        challenge_success_callback = config.maybe_dotted(challenge_success_callback)
    return FanclubAuthPlugin(
        plugin_name=AUTH_PLUGIN_NAME,
        cache_region=None,
        endpoint=settings[prefix + 'endpoint'],
        url_builder=url_builder,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        session_factory=FanclubAuthHTTPSessionFactory(
            persistence_backend,
            session_args
            ),
        timeout=settings.get(prefix + 'timeout'),
        oauth_scope=[c.strip() for c in re.split(ur'\s*,\s*|\s+', settings.get(prefix + 'oauth.scope', u''))] or None,
        challenge_success_callback=challenge_success_callback
        )


def includeme(config):
    from . import CONFIG_PREFIX
    fanclub_auth = fanclub_auth_from_config(
        config,
        prefix=CONFIG_PREFIX
        )
    config.registry.registerUtility(fanclub_auth, IFanclubAuth)
    config.add_auth_plugin(fanclub_auth)
