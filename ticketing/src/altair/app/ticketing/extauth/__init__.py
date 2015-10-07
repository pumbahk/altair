# encoding: utf-8
import logging
from urlparse import urljoin
import pyramid.config
from pyramid.authorization import ACLAuthorizationPolicy
import sqlalchemy as sa
import sqlalchemy.pool as sa_pool
import sqlahelper
from zope.interface import implementer
from altair.rakuten_auth.interfaces import IRakutenOpenIDURLBuilder

logger = logging.getLogger(__name__)
    
ENDPOINT_PATH = {
    u'get_user_info_v0': u'/v0/user',
    }

def empty_resource_factory(request):
    return None

@implementer(IRakutenOpenIDURLBuilder)
class URLBuilder(object):
    extra_verify_url_exists = True

    def __init__(self, proxy_url_pattern):
        self.proxy_url_pattern = proxy_url_pattern

    def build_base_url(self, request):
        subdomain = request.host.split('.', 1)[0]
        return self.proxy_url_pattern.format(
            subdomain=subdomain
            )

    def build_return_to_url(self, request):
        return urljoin(self.build_base_url(request).rstrip('/') + '/', request.route_path('rakuten_auth.verify').lstrip('/'))

    def build_error_to_url(self, request):
        return urljoin(self.build_base_url(request).rstrip('/') + '/', request.route_path('rakuten_auth.error').lstrip('/'))

    def build_verify_url(self, request):
        return request.route_url('rakuten_auth.verify')

    def build_extra_verify_url(self, request):
        return request.route_url('rakuten_auth.verify2')

def setup_auth(config):
    config.include('altair.auth')
    config.include('altair.rakuten_auth')

    config.set_who_api_decider(lambda request, classification: 'rakuten')
    from altair.auth import set_auth_policy
    from .rakuten_auth import add_claimed_id_to_principals
    set_auth_policy(config, add_claimed_id_to_principals)
    config.set_authorization_policy(ACLAuthorizationPolicy())

    # 楽天認証URL
    config.add_route('rakuten_auth.verify', '/.openid/verify', factory=empty_resource_factory)
    config.add_route('rakuten_auth.verify2', '/.openid/verify2', factory=empty_resource_factory)
    config.add_route('rakuten_auth.error', '/.openid/error', factory=empty_resource_factory)

def setup_beaker_cache(config):
    from pyramid_beaker import set_cache_regions_from_settings
    set_cache_regions_from_settings(config.registry.settings)

def setup_oauth_provider(config):
    from pyramid_dogpile_cache import get_region
    from altair.oauth.interfaces import IOAuthProvider
    from altair.oauth.provider import OAuthProvider
    from altair.oauth.random import RandomStringGenerator
    from altair.oauth.dogpile_backend import DogpileBackedPersistentStore
    from datetime import datetime
    from .oauth import ClientRepository
    from altair.oauth.basic_impl import BasicScopeManager
    client_repository = ClientRepository()
    scope_manager = BasicScopeManager(['user_info'])
    config.registry.registerUtility(
        OAuthProvider(
            client_repository=client_repository,
            scope_manager=scope_manager,
            now_getter=datetime.now,
            code_store=DogpileBackedPersistentStore(get_region('altair_extauth_oauth_code')),
            code_generator=RandomStringGenerator(32),
            access_token_store=DogpileBackedPersistentStore(get_region('altair_extauth_oauth_access_token')),
            access_token_generator=RandomStringGenerator(64),
            refresh_token_store=None,
            refresh_token_generator=None
            ),
        IOAuthProvider
        )

def webapp_main(global_config, **local_config):
    settings = dict(global_config)
    settings.update(local_config)

    engine = sa.engine_from_config(settings, poolclass=sa_pool.NullPool, isolation_level='READ COMMITTED')
    sqlahelper.add_engine(engine)

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
    config.add_route('extauth.rakuten.index', '/{subtype}/rid/', traverse='/{subtype}')
    config.add_route('extauth.rakuten.login', '/{subtype}/rid/login', traverse='/{subtype}')
    config.scan('.views')
    return config.make_wsgi_app()

def api_main(global_config, **local_config):
    settings = dict(global_config)
    settings.update(local_config)

    engine = sa.engine_from_config(settings, poolclass=sa_pool.NullPool, isolation_level='READ COMMITTED')
    sqlahelper.add_engine(engine)

    config = pyramid.config.Configurator(
        settings=settings,
        root_factory=empty_resource_factory
        )

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
    config.add_route('extauth.api.v0.user', ENDPOINT_PATH['get_user_info_v0'])
    config.scan('.api_views')
    return config.make_wsgi_app()
