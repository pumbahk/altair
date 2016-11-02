# -*- coding:utf-8 -*-
import logging
import sys
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
from pyramid.httpexceptions import HTTPFound, HTTPUnauthorized
from pyramid.request import Request
from pyramid.response import Response
from pyramid.path import DottedNameResolver

from altair.browserid import get_browserid
from altair.auth.api import get_who_api
from altair.auth.interfaces import IChallenger, IAuthenticator, IMetadataProvider, ILoginHandler
from altair.httpsession.api import HTTPSession
from altair.httpsession.idgen import _generate_id
from . import AUTH_PLUGIN_NAME
from .interfaces import IFanclubAuth
from .api import get_fanclub_oauth, get_fanclub_api_factory
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
        return bool(self.extra_verify_url)

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
    SESSION_IDENT_KEY = '%s.identity' % __name__
    EXTRA_VERIFY_KEY = '%s.raw_identifier' % __name__
    IDENT_PARAMS_KEY = '%s.params' % __name__
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

    def get_session_id(self, request):
        return request.params.get('ak')

    def get_session(self, request):
        session = getattr(request, self.SESSION_KEY, None)
        if session is None:
            id = self.get_session_id(request)
            if id is not None:
                session = self.session_factory(request, id=id)
                setattr(request, self.SESSION_KEY, session)
        return session

    def get_redirect_url(self, request, session):
        """ ユーザの認可リクエストエンドポイントを返す """
        return_to = self.url_builder.build_return_to_url(request)
        return_to = self.combine_session_id(request, session, return_to)
        oauth_request_token, oauth_request_secret = get_fanclub_oauth(request).get_request_token(return_to)
        # access_token取得時に使用
        session['oauth_request_token'] = oauth_request_token
        session['oauth_request_secret'] = oauth_request_secret
        # xoauth_memberships_requiredは求められる会員資格を指定する場合に設定
        # カンマ区切りで複数指定可能
        query = [
            (u'oauth_token', oauth_request_token),
            (u'xoauth_memberships_required', urllib.urlencode(u''))
        ]
        return self.build_endpoint_request_url(query)

    def get_return_url(self, session):
        return session.get(self.__class__.__name__ + '.return_url')

    def set_return_url(self, session, url):
        session[self.__class__.__name__ + '.return_url'] = url

    # IAuthenticator
    def authenticate(self, request, auth_context, auth_factors):
        logger.debug('[pollox] authenticate (request.path_url=%s, auth_factors=%s)' % (request.path_url, auth_factors))

        auth_factors_for_this_plugin = auth_factors.get(self.name)
        identity = {}
        if auth_factors_for_this_plugin is not None:
            received_params = auth_factors_for_this_plugin.get(self.IDENT_PARAMS_KEY, None)
            stored_identity = auth_factors_for_this_plugin.get(self.EXTRA_VERIFY_KEY, None)
        else:
            received_params = None
            stored_identity = None
            for session_keeper in auth_context.session_keepers:
                # セッションから取得したauth_factorがセットされていればidentityとして使う
                auth_factors_for_session_keeper = auth_factors.get(session_keeper.name)
                if auth_factors_for_session_keeper:
                    identity.update(auth_factors_for_session_keeper)
        if received_params is not None:
            assert self.AUTHENTICATED_KEY not in request.environ
            if not self.verify_authentication(request, received_params):
                logger.debug('authentication failed')
                return None, None
            identity['oauth_request_verifier'] = received_params['oauth_verifier']
            identity['oauth_request_token'] = received_params['oauth_request_token']
            identity['oauth_request_secret'] = received_params['oauth_request_secret']
            # temporary session や rememberer には リクエスト限りの received_params は渡さない
            # これいるのか不明
            del auth_factors_for_this_plugin[self.IDENT_PARAMS_KEY]
        elif stored_identity is not None:
            # extra_verify後ここに入って来る可能性がある
            identity = stored_identity
            del auth_factors_for_this_plugin[self.EXTRA_VERIFY_KEY]

        # 認証情報を取得するのに必要なパラメタが足りていない場合は認証失敗
        # verifierがあればrequest_tokenもあるしaccess_tokenも取得できるのでverifierがあるかを確認
        if 'oauth_request_verifier' not in identity:
            logger.debug("no oauth_request_verifier in identity: %r" % identity)
            return None, None

        # extra_verify もしくは普通のリクエストで通る
        # ネガティブキャッシュなので、not in で調べる
        logger.debug('metadata=%r' % request.environ.get(self.METADATA_KEY, '*not set*'))
        if self.METADATA_KEY not in request.environ:
            cache = self._get_cache()

            def get_extras():
                retval = self._get_extras(request, identity)
                browserid = get_browserid(request)
                retval['browserid'] = browserid
                return retval

            extras = None
            try:
                extras = cache.get(
                    key=identity['oauth_request_token'],
                    createfunc=get_extras
                )
                logger.debug("retrieved extra information ({})".format(extras))
            except Exception as e:
                logger.warning("Failed to retrieve extra information", exc_info=sys.exc_info())
            request.environ[self.METADATA_KEY] = extras
        else:
            # ネガティブキャッシュなので extras is None になる可能性
            extras = request.environ[self.METADATA_KEY]
        if extras is None:
            # ユーザ情報が取れないので認証失敗
            logger.info("Could not retrieve extra information")
            return None, None

        request.environ[self.AUTHENTICATED_KEY] = identity
        return { 'pollux_member_id': extras['member_id'] }, { session_keeper.name: identity for session_keeper in auth_context.session_keepers }

    def _get_cache(self):
        return self.cache_manager.get_cache_region(
            __name__ + '.' + self.__class__.__name__,
            self.cache_region
            )

    def _get_extras(self, request, identity):
        if 'oauth_access_token' not in identity:
            logger.info('new request to get access token')
            access_token, access_secret = get_fanclub_oauth(request).get_access_token(request, identity['oauth_request_token'], identity['oauth_request_secret'], identity['oauth_request_verifier'])
            identity['oauth_access_token'] = access_token
            identity['oauth_access_secret'] = access_secret
        else:
            logger.info('pickup access token from session')
            access_token = identity.get('oauth_access_token')
            access_secret = identity.get('oauth_access_secret')
        logger.debug('got access_token={} & secret={}'.format(access_token, access_secret))
        api = get_fanclub_api_factory(request)(request, access_token, access_secret)
        logger.debug('api: {}, token={}, secret={}'.format(api, api.access_token, api.access_secret))
        member_info = api.get_member_info()
        return dict(
            member_id=member_info['external_member_id'],
            first_name=member_info['first_name'],
            last_name=member_info['last_name'],
            email=member_info['email_address'],
            tel_1=member_info['phone_number'],
            tel_2=member_info['mobile_phone_number'],
            zip=member_info['postcode'],
            prefecture_code=member_info['prefecture_code'],
            city=member_info['city'],
            street=member_info['address1'],
            memberships=member_info['memberships']
            )


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
        identity = identities.get(self.name)
        if identity is not None and self.METADATA_KEY in request.environ:
            return request.environ.pop(self.METADATA_KEY)
        else:
            return None

    def on_verify(self, request):
        received_params = dict(
            oauth_request_token=request.GET.get('oauth_token'),
            oauth_verifier=request.GET.get('oauth_verifier')
        )
        session = self.get_session(request)
        if session is None:
            logger.info('could not retrieve the temporary session')
            return HTTPFound(location=self.url_builder.build_error_to_url(request))
        if session.get('oauth_request_secret'):
            received_params.update(dict(oauth_request_secret=session.get('oauth_request_secret')))
        # request_tokenの正当性を確認
        self._check_oauth_token(session, received_params['oauth_request_token'])
        auth_api = get_who_api(request)
        identities, auth_factors, metadata, response = auth_api.login(
            credentials={ self.IDENT_PARAMS_KEY: received_params },
            auth_factor_provider_name=self.name
            )
        if identities:
            if self.url_builder.extra_verify_url_exists(request):
                session[self.SESSION_IDENT_KEY] = auth_factors
                session.save()
                return HTTPFound(
                    self.combine_session_id(
                        request, session,
                        self.url_builder.build_extra_verify_url(request)))
            else:
                identity = identities.get(AUTH_PLUGIN_NAME)
                if identity is not None:
                    return self._on_success(request, session, identity, metadata, response)
                else:
                    logger.info('authentication failure on verify. temporary session timeout, oauth API failures etc.')
                    return HTTPFound(location=self.url_builder.build_error_to_url(request))
        else:
            logger.info('who_api.login failed')
            return HTTPFound(location=self.url_builder.build_error_to_url(request))

    def _check_oauth_token(self, session, received_request_token):
        if session.get('oauth_request_token') != received_request_token:
            # 一連の認証リクエストであることを確認
            # raiseするか保留
            logger.error('received invalid request_token')

    def _on_success(self, request, session, identity, metadata, response):
        if identity is None:
            return HTTPUnauthorized()
        if self.challenge_success_callback is not None:
            self.challenge_success_callback(request, plugin=self, identity=identity, metadata=metadata)
        return_url = self.get_return_url(session)
        if not return_url:
            # TODO: デフォルトURLをHostからひいてくる
            return_url = "/"
        session.invalidate()
        return HTTPFound(location=return_url, headers=response.headers)

    def on_extra_verify(self, request):
        pass

    def verify_authentication(self, request, params):
        # paramsが正当（有効）なものであることを検証
        return True


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
