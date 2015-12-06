# encoding: utf-8
import logging
import pyramid.config
from pyramid.authorization import ACLAuthorizationPolicy
import sqlalchemy as sa
import sqlalchemy.pool as sa_pool

logger = logging.getLogger(__name__)
    
ENDPOINT_PATH = {
    u'get_user_info_v0': u'/v0/user',
    }

def empty_resource_factory(request):
    return None

def setup_auth(config):
    config.include('altair.auth')
    config.include('altair.rakuten_auth')
    config.include('.internal_auth')

    config.set_who_api_decider(lambda request, classification: None)
    from altair.auth import set_auth_policy
    from .rakuten_auth import add_claimed_id_to_principals
    set_auth_policy(config, add_claimed_id_to_principals)
    config.set_authorization_policy(ACLAuthorizationPolicy())

    from pyramid.httpexceptions import HTTPFound
    from .resources import ExtAuthSubTypeResource
    from urlparse import urlparse, urlunparse
    from urllib import urlencode
    from cgi import parse_qsl
    def forbidden_handler(context, request):
        params = None
        redirect_uri = None
        if request.organization is not None:
            redirect_uri = request.organization.emergency_exit_url
        if redirect_uri is None:
            redirect_uri = u'/'
        if request.context is not None and \
           isinstance(request.context, ExtAuthSubTypeResource):
            params = { u'altair.extauth.subtype': request.context.subtype }
        if params is not None:
            parsed_redirect_uri = urlparse(redirect_uri)
            if parsed_redirect_uri.query:
                query = parse_qsl(parsed_redirect_uri.query, keep_blank_values=True)
            else:
                query = []
            query.extend((k.encode('utf-8'), v.encode('utf-8')) for k, v in params.items())
            redirect_uri = urlunparse((
                parsed_redirect_uri.scheme,
                parsed_redirect_uri.netloc,
                parsed_redirect_uri.path,
                parsed_redirect_uri.params,
                urlencode(query, doseq=True).decode('utf-8') if query else None,
                parsed_redirect_uri.fragment
                ))
        logger.debug('forbidden_handler: %s', redirect_uri)
        return HTTPFound(redirect_uri)
    config.set_forbidden_handler(forbidden_handler)

    # 楽天認証URL
    config.add_route('rakuten_auth.verify', '/.openid/verify', factory=empty_resource_factory)
    config.add_route('rakuten_auth.verify2', '/.openid/verify2', factory=empty_resource_factory)
    config.add_route('rakuten_auth.error', '/.openid/error', factory=empty_resource_factory)

def setup_beaker_cache(config):
    from pyramid_beaker import set_cache_regions_from_settings
    set_cache_regions_from_settings(config.registry.settings)

def setup_oauth_provider(config):
    from pyramid_dogpile_cache import get_region
    from altair.oauth.interfaces import IOAuthProvider, IOpenIDProvider
    from altair.oauth.provider import OAuthProvider
    from altair.oauth.openid_provider import OpenIDProvider
    from altair.oauth.random import RandomStringGenerator
    from altair.oauth.dogpile_backend import DogpileBackedPersistentStore
    from datetime import datetime
    from .oauth import ClientRepository
    from altair.oauth.basic_impl import BasicScopeManager
    client_repository = ClientRepository()
    scope_manager = BasicScopeManager(['user_info'])
    oauth_provider = OAuthProvider(
        client_repository=client_repository,
        scope_manager=scope_manager,
        now_getter=datetime.now,
        code_store=DogpileBackedPersistentStore(get_region('altair_extauth_oauth_code')),
        code_generator=RandomStringGenerator(32),
        access_token_store=DogpileBackedPersistentStore(get_region('altair_extauth_oauth_access_token')),
        access_token_generator=RandomStringGenerator(64),
        refresh_token_store=None,
        refresh_token_generator=None
        )
    secret = config.registry.settings.get('altair.extauth.openid_secret')
    openid_provider = OpenIDProvider(
        oauth_provider=oauth_provider,
        id_token_store=DogpileBackedPersistentStore(get_region('altair_extauth_openid_id_token')),
        issuer=lambda client_id, identity: identity.get('host_name', 'altair.extauth'),
        token_expiration_time=900,
        secret=secret,
        jws_algorithm='HS256' if secret else None
        )
    config.registry.registerUtility(
        oauth_provider,
        IOAuthProvider
        )
    config.registry.registerUtility(
        openid_provider,
        IOpenIDProvider
        )

def register_template_globals(event):
    from altair.viewhelpers import Namespace
    from .helpers import Helpers
    class CombinedNamespace(object):
        def __init__(self, namespaces):
            self.namespaces = namespaces

        def __getattr__(self, k):
            for ns in self.namespaces:
                v = getattr(ns, k, None)
                if v is not None:
                    return v
            return object.__getattr__(self, k)

    h = CombinedNamespace([
        Helpers(event['request']),
        Namespace(event['request']),
        ])
    event.update(h=h)

def key_mangler_oauth_code(key):
    return b'oauth_authz_code:' + bytes(key)

def key_mangler_oauth_access_token(key):
    return b'oauth_token:' + bytes(key)

def key_mangler_openid_id_token(key):
    return b'openid_token:' + bytes(key)

def webapp_main(global_config, **local_config):
    settings = dict(global_config)
    settings.update(local_config)

    config = pyramid.config.Configurator(
        settings=settings,
        root_factory='.resources.ExtAuthRoot'
        )

    config.include('pyramid_mako')
    config.add_mako_renderer('.txt')
    config.add_mako_renderer('.mako')
    config.include('pyramid_tm')
    config.include('pyramid_fanstatic')
    config.include('pyramid_dogpile_cache')
    config.include('altair.pyramid_dynamic_renderer')
    config.include('altair.httpsession.pyramid')
    config.include('altair.browserid')
    config.include('altair.exclog')
    config.include('altair.sqlahelper')
    config.include('altair.mobile')
    config.include(setup_auth)
    config.include(setup_beaker_cache)
    config.include('.view_context')
    config.include('.rendering')
    config.include('.request')
    config.include('.eagles_communicator')
    config.include(setup_oauth_provider)
    config.add_route('extauth.reset_and_continue', '/reset/*path', factory=empty_resource_factory)
    config.add_route('extauth.entry', '/{subtype}/', traverse='/{subtype}')
    config.add_route('extauth.rakuten.entry', '/{subtype}/rid', traverse='/{subtype}')
    config.add_route('extauth.unknown_user', '/{subtype}/unknown', traverse='/{subtype}')
    config.add_route('extauth.select_account', '/{subtype}/select_account', traverse='/{subtype}')
    config.add_route('extauth.authorize', '/{subtype}/authz', traverse='/{subtype}')
    config.add_route('extauth.login', '/{subtype}/login', traverse='/{subtype}')
    config.add_route('extauth.logout', '/{subtype}/logout', traverse='/{subtype}')
    config.add_subscriber(register_template_globals, 'pyramid.events.BeforeRender')
    config.scan('.views')
    return config.make_wsgi_app()

def api_main(global_config, **local_config):
    settings = dict(global_config)
    settings.update(local_config)

    config = pyramid.config.Configurator(
        settings=settings,
        root_factory=empty_resource_factory
        )
    from altair.httpsession.pyramid import register_utilities as register_httpsession_utilities
    register_httpsession_utilities(config, skip_http_backend_registration=True)

    from altair.pyramid_extra_renderers.json import JSON
    config.add_renderer('json', JSON())
    config.include('pyramid_tm')
    config.include('pyramid_dogpile_cache')
    config.include('altair.browserid')
    config.include('altair.exclog')
    config.include('altair.sqlahelper')
    config.include('.request')
    config.include(setup_oauth_provider)
    config.add_route('extauth.api.issue_oauth_access_token', '/token', request_method='POST')
    config.add_route('extauth.api.revoke_oauth_access_token', '/token/{access_token:.*}', request_method='DELETE')
    config.add_route('extauth.api.openid_end_session', '/session/{id_token:.*}', request_method='DELETE')
    config.add_route('extauth.api.v0.user', ENDPOINT_PATH['get_user_info_v0'])
    config.scan('.api_views')
    return config.make_wsgi_app()
