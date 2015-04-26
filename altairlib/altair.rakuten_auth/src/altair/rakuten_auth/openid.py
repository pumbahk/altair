# encoding: utf-8

import sys
import urllib
import urllib2
from urlparse import urljoin
import logging
import uuid
import pickle
import logging
from datetime import datetime
from zope.interface import implementer
from beaker.cache import Cache, CacheManager, cache_regions
from pyramid.httpexceptions import HTTPFound, HTTPUnauthorized
from pyramid.request import Request
from pyramid.response import Response
from pyramid.path import DottedNameResolver

from altair.browserid import get_browserid
from altair.httpsession.api import (
    HTTPSession,
    BasicHTTPSessionManager,
    DummyHTTPBackend,
    )
from altair.httpsession.idgen import _generate_id

from altair.auth.api import get_auth_api
from altair.auth.interfaces import IChallenger, IAuthenticator, IMetadataProvider, ILoginHandler
from altair.mobile.interfaces import IMobileRequest
from altair.mobile.session import HybridHTTPBackend, merge_session_restorer_to_url

from . import AUTH_PLUGIN_NAME
from .events import Authenticated
from .api import get_rakuten_oauth, get_rakuten_id_api_factory
from .interfaces import IRakutenOpenID

logger = logging.getLogger(__name__)

cache_manager = CacheManager(cache_regions=cache_regions)


class RakutenOpenIDHTTPSessionContext(object):
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


class RakutenOpenIDHTTPSessionFactory(object):
    def __init__(self, persistence_backend, session_args):
        import altair.httpsession
        self.persistence_backend_factory = DottedNameResolver(altair.httpsession).maybe_resolve(persistence_backend)
        self.session_args = session_args

    def __call__(self, request, id=None):
        persistence_backend = self.persistence_backend_factory(request, **self.session_args)
        return HTTPSession(
            RakutenOpenIDHTTPSessionContext(persistence_backend),
            id
            )


def sex_no(s, encoding='utf-8'):
    if isinstance(s, str):
        s = s.decode(encoding)
    if s == u'男性':
        return 1
    elif s == u'女性':
        return 2
    else:
        return 0


@implementer(IRakutenOpenID, IAuthenticator, ILoginHandler, IChallenger, IMetadataProvider)
class RakutenOpenID(object):
    SESSION_KEY = '_%s_session' % __name__
    SESSION_IDENT_KEY = 'RakutenOpenIDPlugin.identity'
    EXTRA_VERIFY_KEY = '%s.raw_identifier' % __name__
    IDENT_OPENID_PARAMS_KEY = '%s.params' % __name__
    AUTHENTICATED_KEY = '%s.authenticated' % __name__
    METADATA_KEY = '%s.metadata' % __name__
    DEFAULT_CACHE_REGION_NAME = '%s.metadata' % __name__

    cache_manager = cache_manager

    def __init__(self,
            plugin_name,
            endpoint,
            verify_url,
            extra_verify_url,
            error_to,
            consumer_key,
            session_factory,
            cache_region=None,
            return_to=None,
            timeout=10):
        if cache_region is None:
            cache_region = self.DEFAULT_CACHE_REGION_NAME
        self.name = plugin_name
        self.cache_region = cache_region
        self.endpoint = endpoint
        self.verify_url = verify_url
        self.extra_verify_url = extra_verify_url
        self.error_to = error_to
        self.consumer_key = consumer_key
        self.session_factory = session_factory
        self.return_to = return_to or verify_url
        self.timeout = int(timeout)

    def get_session_id(self, request):
        return request.params.get('ak')

    def new_session(self, request):
        return self.session_factory(request, id=None)

    def get_session(self, request):
        session = getattr(request, self.SESSION_KEY, None)
        if session is None:
            id = self.get_session_id(request)
            if id is not None:
                session = self.session_factory(request, id=id)
                setattr(request, self.SESSION_KEY, session)
        return session

    def combine_session_id(self, request, session, url):
        q = '?ak=' + urllib.quote(session.id)
        if IMobileRequest.providedBy(request):
            key = HybridHTTPBackend.get_query_string_key(request)
            session_restorer = HybridHTTPBackend.get_session_restorer(request)
            if key and session_restorer:
                # webobは"&"の他に";"文字もデリミタと見なしてくれる
                q += ';%s=%s' % (urllib.quote(key), urllib.quote(session_restorer))
        return urljoin(url, q)

    def get_redirect_url(self, request, session):
        return self.endpoint + "?" + urllib.urlencode([
            ('openid.ns', 'http://specs.openid.net/auth/2.0'),
            ('openid.return_to', self.combine_session_id(request, session, self.return_to)),
            ('openid.claimed_id', 'http://specs.openid.net/auth/2.0/identifier_select'),
            ('openid.identity', 'http://specs.openid.net/auth/2.0/identifier_select'),
            ('openid.mode', 'checkid_setup'),
            ('openid.ns.oauth', 'http://specs.openid.net/extenstions/oauth/1.0'),
            ('openid.oauth.consumer', self.consumer_key),
            ('openid.oauth.scope', 'rakutenid_basicinfo,rakutenid_contactinfo,rakutenid_pointaccount'),
            # ('openid.ns.ax', 'http://openid.net/srv/ax/1.0'),
            # ('openid.ax.mode', 'fetch_request'),
            # ('openid.ax.type.nickname', 'http://schema.openid.net/namePerson/friendly'),
            # ('openid.ax.required', 'nickname'),
        ])

    def verify_authentication(self, request, params):
        url = self.endpoint + "?" + urllib.urlencode(
           [('openid.ns', params['ns']),
            ('openid.op_endpoint', params['op_endpoint']),
            ('openid.claimed_id', params['claimed_id']),
            ('openid.response_nonce',params['response_nonce']),
            ('openid.mode', params['mode']),
            ('openid.identity', params['identity']),
            ('openid.return_to', params['return_to']),
            ('openid.assoc_handle', params['assoc_handle']),
            ('openid.signed', params['signed']),
            ('openid.sig', params['sig']),
            ('openid.ns.oauth', params['ns_oauth']),
            ('openid.oauth.request_token', params['oauth_request_token']),
            ('openid.oauth.scope', params['oauth_scope']),
            # ('openid.ns.ax', params['ns_ax']),
            # ('openid.ax.mode', params['ax_mode']),
            # ('openid.ax.type.nickname', params['ax_type_nickname']),
            # ('openid.ax.value.nickname', params['ax_value_nickname'].encode('utf-8')),
        ])

        f = urllib2.urlopen(url, timeout=self.timeout)
        try:
            response_body = f.read()
        finally:
            f.close()

        logger.debug('authenticate result: %s' % response_body)
        is_valid = response_body.split("\n")[0].split(":")[1]

        if is_valid == "true":
            return True
        else:
            return False

    def openid_params(self, request):
        request_get = request.params
        return dict(
            ns = request_get['openid.ns'],
            op_endpoint = request_get['openid.op_endpoint'],
            claimed_id = request_get['openid.claimed_id'],
            response_nonce = request_get['openid.response_nonce'],
            mode = 'check_authentication',
            identity = request_get['openid.identity'],
            return_to = request_get['openid.return_to'],
            assoc_handle = request_get['openid.assoc_handle'],
            signed = request_get['openid.signed'],
            sig = request_get['openid.sig'],
            ns_oauth = 'http://specs.openid.net/extenstions/oauth/1.0',
            oauth_request_token = request_get['openid.oauth.request_token'],
            oauth_scope = 'rakutenid_basicinfo,rakutenid_contactinfo,rakutenid_pointaccount',
            # ns_ax = request_get['openid.ns.ax'],
            # ax_mode = request_get['openid.ax.mode'],
            # ax_type_nickname = request_get['openid.ax.type.nickname'],
            # ax_value_nickname = request_get['openid.ax.value.nickname'],
            )

    def get_return_url(self, session):
        return session.get(self.__class__.__name__ + '.return_url')

    def set_return_url(self, session, url):
        session[self.__class__.__name__ + '.return_url'] = url

    def extra_verification_phase(self, request):
        return request.path_url == self.extra_verify_url

    def extra_verification_phase_exists(self, request):
        return self.extra_verify_url is not None 

    def on_verify(self, request):
        logger.debug('openid verify GET: {0}\nPOST: {1}'.format(request.GET.items(), request.POST.items()))
        params = self.openid_params(request)
        session = self.get_session(request)
        if session is None:
            logger.info('could not retrieve the temporary session')
            return HTTPFound(location=self.error_to)
        auth_api = get_auth_api(request)
        identities, auth_factors, metadata = auth_api.login(
            request,
            request.response,
            credentials={ self.IDENT_OPENID_PARAMS_KEY: params },
            auth_factor_provider_name=self.name
            )
        response = request.response
        if identities:
            if self.extra_verification_phase_exists(request):
                session[self.SESSION_IDENT_KEY] = auth_factors
                session.save()
                return HTTPFound(
                    self.combine_session_id(
                        request, session,
                        self.extra_verify_url))
            else:
                identity = identities.get(AUTH_PLUGIN_NAME)
                if identity is not None:
                    return self._on_success(request, session, identity, metadata, response)
                else:
                    logger.info('authentication failure on verify. temporary session timeout, oauth API failures etc.')
                    return HTTPFound(location=self.error_to)
        else:
            logger.info('who_api.login failed')
            return HTTPFound(location=self.error_to)

    def on_extra_verify(self, request):
        if not self.extra_verification_phase(request):
            logger.error('authentication failure on extra_verify. request.path_url (%s) != extra_verify_url (%s)' % (request.path_url, self.extra_verify_url))
            return HTTPFound(location=self.error_to)

        session = self.get_session(request)
        if session is None:
            logging.info('could not retrieve the temporary session')
            return HTTPFound(location=self.error_to)
        auth_factors = session.get(self.SESSION_IDENT_KEY)
        if auth_factors is None:
            logging.info('no identity stored in the temporary session')
            return HTTPFound(location=self.error_to)
        auth_api = get_auth_api(request)
        identities, auth_factors, metadata = auth_api.authenticate(request, auth_factors=auth_factors, auth_factor_provider_name=self.name)
        identity = identities.get(AUTH_PLUGIN_NAME) if identities is not None else None
        if identity is not None:
            auth_api.remember(request, request.response, auth_factors)
            return self._on_success(request, session, identity, metadata, request.response)
        else:
            logger.info('authentication failure on extra_verify. temporary session timeout, oauth API failures etc.')
            return HTTPFound(location=self.error_to)

    def _on_success(self, request, session, identity, metadata, response):
        if identity is None:
            return HTTPUnauthorized()
        request.registry.notify(Authenticated(
            request,
            identity['claimed_id'],
            metadata
            ))
        return_url = self.get_return_url(session)
        if not return_url:
            # TODO: デフォルトURLをHostからひいてくる
            return_url = "/"
        session.invalidate()
        return HTTPFound(location=return_url, headers=response.headers)

    def _get_cache(self):
        return self.cache_manager.get_cache_region(
            __name__ + '.' + self.__class__.__name__,
            self.cache_region
            )

    def _get_extras(self, request, identity):
        access_token = get_rakuten_oauth(request).get_access_token(identity['oauth_request_token'])
        idapi = get_rakuten_id_api_factory(request)(access_token)
        user_info = idapi.get_basic_info()
        birthday = None
        try:
            birthday = datetime.strptime(user_info.get('birthDay'), '%Y/%m/%d')
        except (ValueError, TypeError):
            # 生年月日未登録
            pass

        contact_info = idapi.get_contact_info()
        point_account = idapi.get_point_account()

        return dict(
            email_1=user_info.get('emailAddress'),
            nick_name=user_info.get('nickName'),
            first_name=user_info.get('firstName'),
            last_name=user_info.get('lastName'),
            first_name_kana=user_info.get('firstNameKataKana'),
            last_name_kana=user_info.get('lastNameKataKana'),
            birthday=birthday,
            sex=sex_no(user_info.get('sex'), 'utf-8'),
            zip=contact_info.get('zip'),
            prefecture=contact_info.get('prefecture'),
            city=contact_info.get('city'),
            street=contact_info.get('street'),
            tel_1=contact_info.get('tel'),
            rakuten_point_account=point_account.get('pointAccount')
            )

    # ILoginHandler
    def get_auth_factors(self, request, auth_context, credentials):
        return credentials

    # IAuthenticator
    def authenticate(self, request, auth_context, auth_factors):
        logger.debug('authenticate (request.path_url=%s, auth_factors=%s)' % (request.path_url, auth_factors))

        auth_factors_for_this_plugin = auth_factors.get(self.name)
        identity = {}
        if auth_factors_for_this_plugin is not None:
            openid_params = auth_factors_for_this_plugin.get(self.IDENT_OPENID_PARAMS_KEY, None)
            stored_identity = auth_factors_for_this_plugin.get(self.EXTRA_VERIFY_KEY, None)
        else:
            openid_params = None
            stored_identity = None
            for session_keeper in auth_context.session_keepers:
                auth_factors_for_session_keeper = auth_factors.get(session_keeper.name)
                if auth_factors_for_session_keeper:
                    identity.update(auth_factors_for_session_keeper)
        if openid_params is not None:
            # verify から呼ばれた場合
            assert self.AUTHENTICATED_KEY not in request.environ
            claimed_id = openid_params['claimed_id']
            self._flush_cache(claimed_id)
            if not self.verify_authentication(request, openid_params):
                logger.debug('authentication failed')
                return None, None
            # claimed_id と oauth_request_token は、validate に成功した時のみ入る
            identity['claimed_id'] = claimed_id
            identity['oauth_request_token'] = openid_params['oauth_request_token']
            # temporary session や rememberer には OpenID parameters は渡さない
            del auth_factors_for_this_plugin[self.IDENT_OPENID_PARAMS_KEY]
        elif stored_identity is not None:
            # extra_verify; identity はセッションに保存されている
            identity = stored_identity
            del auth_factors_for_this_plugin[self.EXTRA_VERIFY_KEY]

        if 'claimed_id' not in identity:
            logger.debug("no claimed_id in identity: %r" % identity)
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
                    key=identity['claimed_id'],
                    createfunc=get_extras
                    )
            except:
                logger.warning("Failed to retrieve extra information", exc_info=sys.exc_info())
            request.environ[self.METADATA_KEY] = extras
        else:
            # ネガティブキャッシュなので extras is None になる可能性
            extras = request.environ[self.METADATA_KEY]
        if extras is None:
            # ユーザ情報が取れない→ポイント口座番号が取れない
            # →クリティカルな状況と考えられるので認証失敗
            logger.info("Could not retrieve extra information")
            return None, None

        request.environ[self.AUTHENTICATED_KEY] = identity
        return { 'claimed_id': identity['claimed_id'] }, { session_keeper.name: identity for session_keeper in auth_context.session_keepers }

    def _flush_cache(self, claimed_id):
        try:
            self._get_cache().remove_value(claimed_id)
        except:
            import sys
            logger.warning("failed to flush metadata cache for %s" % identity, exc_info=sys.exc_info())

    # IMetadataProvider
    def get_metadata(self, request, auth_context, identities):
        identity = identities.get(self.name)
        if identity is not None and self.METADATA_KEY in request.environ:
            return request.environ.pop(self.METADATA_KEY)
        else:
            return None

    # IChallenger
    def challenge(self, request, auth_context, response):
        logger.debug('challenge')
        session = self.new_session(request)
        return_url = request.url
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


def openid_consumer_from_settings(settings, prefix):
    session_args = {}
    for k, v in settings.items():
        if k.startswith(prefix + 'session.'):
            session_args[k[len(prefix + 'session.'):]] = v
    persistence_backend = settings[prefix + 'session']

    return RakutenOpenID(
        plugin_name=AUTH_PLUGIN_NAME,
        cache_region=None,
        endpoint=settings[prefix + 'endpoint'],
        verify_url=settings.get(prefix + 'verify_url'),
        extra_verify_url=settings.get(prefix + 'extra_verify_url'),
        error_to=settings.get(prefix + 'error_to'),
        consumer_key=settings[prefix + 'oauth.consumer_key'],
        session_factory=RakutenOpenIDHTTPSessionFactory(
            persistence_backend,
            session_args
            ),
        return_to=settings.get(prefix + 'return_to'),
        timeout=settings.get(prefix + 'timeout')
        )

def includeme(config):
    from . import CONFIG_PREFIX
    rakuten_auth = openid_consumer_from_settings(
        config.registry.settings,
        prefix=CONFIG_PREFIX
        )
    config.registry.registerUtility(rakuten_auth, IRakutenOpenID)
    config.add_auth_plugin(rakuten_auth)
