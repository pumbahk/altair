# encoding: utf-8
import logging
import sys
from urllib import urlencode
from urlparse import urljoin
from zope.interface import implementer
from pyramid_dogpile_cache import get_region
from pyramid.view import view_config
from altair.mobile.session import HybridHTTPBackend, merge_session_restorer_to_url
from altair.auth.interfaces import IChallenger, IAuthenticator, IMetadataProvider, ILoginHandler, IRequestInterceptor
from altair.auth.api import get_auth_api
from altair.browserid import get_browserid
from altair.oauth_auth.api import get_api_factory
from altair.mobile.interfaces import IMobileRequest

logger = logging.getLogger(__name__)

ROUTE_NAME = '%s.auth_cb' % __name__

def generate_verification_token():
    import os
    from hashlib import md5
    return md5(__name__ + os.urandom(64)).hexdigest()

@implementer(IAuthenticator, ILoginHandler, IChallenger, IMetadataProvider, IRequestInterceptor)
class OAuthAuthPlugin(object):
    ACCESS_TOKEN_KEY = 'access_token'
    METADATA_KEY = '%s.metadata' % __name__
    DEFAULT_CACHE_REGION_NAME = '%s_metadata' % __name__.replace('.', '_')
    SESSION_RETURN_TO_URL_KEY = '%s.return_to_url' % __name__
    SESSION_VERIFICATION_TOKEN_KEY = '%s.verification_token' % __name__

    def __init__(self, client_id, authz_endpoint, api_endpoint, callback_path, error_url, cache_region=None, on_login=None):
        self.client_id = client_id
        self.name = '%s.%s' % (__name__, self.__class__.__name__)
        self.authz_endpoint = authz_endpoint
        self.api_endpoint = api_endpoint
        self.callback_path = callback_path
        self.error_url = error_url
        if cache_region is None:
            cache_region = self.DEFAULT_CACHE_REGION_NAME
        self.cache_region = cache_region
        self.on_login = on_login

    def _get_cache(self):
        return get_region(self.cache_region)

    def _get_extras(self, request, auth_factors):
        access_token = auth_factors['access_token']
        api_endpoint = self.api_endpoint
        if callable(api_endpoint):
            api_endpoint = api_endpoint(request)
        _api = get_api_factory(request, self.name).create_oauth_api(access_token, api_endpoint)
        user_info = _api.get_user_info(request)
        return user_info

    # ILoginHandler
    def get_auth_factors(self, request, auth_context, credentials):
        return credentials

    # IAuthenticator
    def authenticate(self, request, auth_context, auth_factors):
        logger.debug('authenticate (request.path_url=%s, auth_factors=%s)' % (request.path_url, auth_factors))

        auth_factors_provided_on_login = auth_factors.get(self.name)
        if auth_factors_provided_on_login is not None:
            # ログインの場合
            auth_factors_for_this_plugin = auth_factors_provided_on_login
        else:
            # loginでない場合
            auth_factors_for_this_plugin = {}
            for session_keeper in auth_context.session_keepers:
                auth_factors_for_session_keeper = auth_factors.get(session_keeper.name)
                if auth_factors_for_session_keeper:
                    auth_factors_for_this_plugin.update(auth_factors_for_session_keeper)
        if not 'access_token' in auth_factors_for_this_plugin:
            logger.debug('no access_token in auth_factors')
            return None, None
        # extra_verify もしくは普通のリクエストで通る
        # ネガティブキャッシュなので、not in で調べる
        logger.debug('metadata=%r' % request.environ.get(self.METADATA_KEY, '*not set*'))
        if self.METADATA_KEY not in request.environ:
            cache = self._get_cache()

            def get_extras():
                retval = self._get_extras(request, auth_factors_for_this_plugin)
                browserid = get_browserid(request)
                retval['browserid'] = browserid
                return retval

            extras = None
            try:
                extras = cache.get_or_create(bytes(auth_factors_for_this_plugin['access_token']), get_extras)
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
        return extras['identifiers'], { session_keeper.name: auth_factors_for_this_plugin for session_keeper in auth_context.session_keepers }

    def _flush_cache(self, id):
        try:
            self._get_cache().delete(id)
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

    def get_redirect_uri(self, request):
        return urljoin(request.application_url.rstrip(u'/') + u'/', self.callback_path.lstrip(u'/'))

    # IChallenger
    def challenge(self, request, auth_context, response):
        logger.debug('challenge')
        return_url = request.url
        _session = request.session # Session gets created here!
        if _session is not None and IMobileRequest.providedBy(request):
            key = HybridHTTPBackend.get_query_string_key(request)
            session_restorer = HybridHTTPBackend.get_session_restorer(request)
            if key and session_restorer:
                return_url = merge_session_restorer_to_url(return_url, key, session_restorer)
        _session[self.SESSION_RETURN_TO_URL_KEY] = return_url
        verification_token = generate_verification_token()
        _session[self.SESSION_VERIFICATION_TOKEN_KEY] = verification_token
        authz_endpoint = self.authz_endpoint
        if callable(authz_endpoint):
            authz_endpoint = authz_endpoint(request)
        client_id = self.client_id
        if callable(client_id):
            client_id = client_id(request)
        redirect_to = urljoin(
            authz_endpoint,
            '?' + urlencode({
                u'response_type': u'code',
                u'client_id': client_id,
                u'state': verification_token,
                u'redirect_uri': self.get_redirect_uri(request),
                })
            )
        logger.debug('redirect from %s to %s' % (request.url, redirect_to))
        response.location = redirect_to
        response.status = 302
        return True

    # IRequestInterceptor
    def intercept(self, request):
        if request.path_info != self.callback_path:
            return None
        authorization_code = request.GET.getone('code')
        verification_token = request.GET.getone('state')
        expected_verification_token = request.session[self.SESSION_VERIFICATION_TOKEN_KEY]
        if verification_token != expected_verification_token:
            logger.warning('state does not match (%s != %s)' % (verification_token, expected_verification_token))
            error_url = self.error_url
            if callable(error_url):
                error_url = error_url(request)
            return HTTPFound(location=error_url)
        access_token, aux = get_api_factory(request, self.name).create_oauth_negotiator().get_access_token(request, authorization_code, self.get_redirect_uri(request))
        logger.debug('access_token=%r, aux=%s' % (access_token, aux))
        auth_api = get_auth_api(request)
        response = request.response
        identities, _, metadata = auth_api.login(request, response, { 'access_token': access_token }, auth_factor_provider_name=self.name)
        if self.on_login is not None:
            self.on_login(request, identities[self.name], metadata)
        response.location = request.session[self.SESSION_RETURN_TO_URL_KEY]
        response.status = 302
        return response
