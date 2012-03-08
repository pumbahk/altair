# coding:utf-8
import re
import warnings

import logging
logger = logging.getLogger(__name__)

from . monkeypatch import config_scan_patch
config_scan_patch()
from pyramid.authentication import AuthTktAuthenticationPolicy, SessionAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.settings import asbool

import sqlahelper
from sqlalchemy import engine_from_config

from altaircms.security import rolefinder, RootFactory
from altaircms.models import initialize_sql

try:
    import pymysql_sa
    pymysql_sa.make_default_mysql_dialect()
    logger.info('Using PyMySQL')
except:
    pass


def cms_include(config):
    config.add_route('event', '/event/{id}')
    config.add_route('event_list', '/event/')

    config.add_route('layout', '/layout/{layout_id}')
    config.add_route('layout_list', '/layout/')

    # config.add_route('page_list', '/page/', factory="altaircms.page.resources.SampleCoreResource")
    config.add_route('page_edit_', '/page/{page_id}', factory="altaircms.page.resources.SampleCoreResource")

    config.add_route('page_add', '/event/{event_id}/page/')
    config.add_route('page_edit', '/event/{event_id}/page/{page_id}/edit')

    config.add_route('asset_list', '/asset/')
    config.add_route('asset_form', '/asset/form/{asset_type}')
    config.add_route('asset_edit', '/asset/{asset_id}')
    config.add_route('asset_display', '/asset/display/{asset_id}')
    config.add_route('asset_view', '/asset/{asset_id}')

    config.add_route('widget', '/widget/{widget_id}')
    config.add_route('widget_add', '/widget/form/{widget_type}')
    config.add_route('widget_delete', '/widget/{widget_id}/delete')
    config.add_route('widget_list', '/widget/')


def main_app_with_strip_secret(global_config, settings):
    D = {"altaircms.debug.strip_security": True}
    settings.update(D)
    return main_app(global_config, settings)


def main_app(global_config, settings):
    """ This function returns a Pyramid WSGI application.
    """
    if asbool(settings.get("altaircms.debug.strip_security", 'false')):
        from altaircms.security import SecurityAllOK
        from altaircms.security import DummyAuthorizationPolicy
        authn_policy = AuthTktAuthenticationPolicy(settings.get('session.secret'), callback=SecurityAllOK())
        authz_policy = DummyAuthorizationPolicy()
    else:
        authn_policy = AuthTktAuthenticationPolicy(settings.get('auth.secret'), callback=rolefinder)
        authz_policy = ACLAuthorizationPolicy()

    session_factory = UnencryptedCookieSessionFactoryConfig(settings.get('session.secret'))

    config = Configurator(
        root_factory=RootFactory,
        settings=settings,
        session_factory=session_factory,
        authentication_policy=authn_policy,
        authorization_policy=authz_policy
    )

    config.include('pyramid_tm')
    config.include("pyramid_fanstatic")
    config.include("altaircms.widget")

    config.include("altaircms.auth", route_prefix='/auth')
    config.include("altaircms.front", route_prefix="f")
    config.include(cms_include, route_prefix='')
    config.include("altaircms.plugins")
    config.include("altaircms.event")
    config.include("altaircms.layout")
    config.include("altaircms.page")

    # config.include("altaircms.base")

    test_re = re.compile('tests$').search
    config.scan("altaircms.subscribers")
    config.scan('altaircms.base', ignore=[test_re])
    config.scan('altaircms.auth', ignore=[test_re])
    config.scan('altaircms.event', ignore=[test_re])
    config.scan('altaircms.page', ignore=[test_re])
    config.scan('altaircms.asset', ignore=[test_re])
    config.scan('altaircms.widget', ignore=[test_re])
    config.scan('altaircms.layout', ignore=[test_re])
    config.scan('altaircms.front', ignore=[test_re])
    config.scan("altaircms.plugins", ignore=[test_re])
    config.scan("altaircms.subscribers", ignore=[test_re])

    config.add_static_view('static', 'altaircms:static', cache_max_age=3600)
    config.add_static_view('plugins/static', 'altaircms:plugins/static', cache_max_age=3600)

    engine = engine_from_config(settings, 'sqlalchemy.')
    sqlahelper.add_engine(engine)
    
    if asbool(settings.get("altaircms.debug.start_when_dropall", "false")):
        warnings.warn("altaircms.debug.start_when_dropall is true. all table are dropped!")
        initialize_sql(engine, dropall=True)
    else:
        initialize_sql(engine)

    ## 設定ファイルを読み込んで追加でinclude.(debug用)
    if settings.get("altaircms.debug.additional_includes"):
        for m in settings.get("altaircms.debug.additional_includes").split("\n"):
            warnings.warn("------------additional include " + m)
            config.include(m)
    return config.make_wsgi_app()


def main(global_config, **settings):
    """ apprications main
    """
    return main_app(global_config, settings)

