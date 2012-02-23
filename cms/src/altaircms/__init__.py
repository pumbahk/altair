# coding:utf-8
from . monkeypatch import config_scan_patch
config_scan_patch()
from pyramid.authentication import AuthTktAuthenticationPolicy, SessionAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.security import Allow, Authenticated, Everyone, Deny
from pyramid.events import BeforeRender

import sqlahelper

from sqlalchemy import engine_from_config

from altaircms.security import groupfinder
from altaircms.models import initialize_sql



try:
    import pymysql_sa
    pymysql_sa.make_default_mysql_dialect()
    print 'Using PyMySQL'
except:
    pass



class RootFactory(object):
    __name__ = None
    __acl__ = [
        (Allow, Authenticated, 'authenticated'),
        (Allow, 'view', 'view'),
        (Allow, 'edit', 'edit')
    ]

    def __init__(self, request):
        pass

def cms_include(config):
    config.add_route('event', '/event/{id}')
    config.add_route('event_list', '/event/')

    config.add_route('layout', '/layout/{layout_id}')
    config.add_route('layout_list', '/layout/')

    config.add_route('page_list', '/page/', factory="altaircms.page.resources.SampleCoreResource")
    config.add_route('page_edit_', '/page/{page_id}', factory="altaircms.page.resources.SampleCoreResource")
    config.add_route('page_add', '/event/{event_id}/page/')
    config.add_route('page_edit', '/event/{event_id}/page/{page_id}/edit')

    config.add_route('asset_list', '/asset/')
    config.add_route('asset_form', '/asset/form/{asset_type}')
    config.add_route('asset_edit', '/asset/{asset_id}')
    config.add_route('asset_view', '/asset/{asset_id}')

    config.add_route('widget', '/widget/{widget_id}')
    config.add_route('widget_add', '/widget/form/{widget_type}')
    config.add_route('widget_delete', '/widget/{widget_id}/delete')
    config.add_route('widget_list', '/widget/')


def main_app(global_config, settings):
    """ This function returns a Pyramid WSGI application.
    """
    # authn_policy = AuthTktAuthenticationPolicy(secret='SDQGxGIhVqSr3zJWV8KvHqHtJujhJj', callback=groupfinder)
    authn_policy = SessionAuthenticationPolicy(callback=groupfinder)
    authz_policy = ACLAuthorizationPolicy()

    session_factory = UnencryptedCookieSessionFactoryConfig('itsaseekreet')

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
    # config.include(api_include, route_prefix='/api')
    config.include("altaircms.front", route_prefix="f")
    config.include(cms_include, route_prefix='')
    config.include("altaircms.plugins")
    config.include("altaircms.event")

    config.scan('altaircms.base')
    config.scan('altaircms.auth')
    config.scan('altaircms.event')
    config.scan('altaircms.page')
    config.scan('altaircms.asset')
    config.scan('altaircms.widget', ignore=["altaircms.widget.tests"])
    config.scan('altaircms.layout')
    config.scan('altaircms.front')
    config.scan("altaircms.plugins")

    config.add_static_view('static', 'altaircms:static', cache_max_age=3600)
    config.add_static_view('plugins/static', 'altaircms:plugins/static', cache_max_age=3600)

    engine = engine_from_config(settings, 'sqlalchemy.')
    sqlahelper.add_engine(engine)
    initialize_sql(engine)

    return config.make_wsgi_app()
    
def main(global_config, **settings):
    """ apprications main
    """
    return main_app(global_config, settings)

