# -*- coding: utf-8 -*-

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig

from sqlalchemy import engine_from_config
from sqlalchemy.pool import NullPool
from resources import RootFactory, groupfinder
import sqlahelper

try:
    import pymysql_sa
    pymysql_sa.make_default_mysql_dialect()
except:
    pass

import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

def main(global_config, **local_config):
    """ This function returns a Pyramid WSGI application.
    """
    settings = dict(global_config)
    settings.update(local_config)

    engine = engine_from_config(settings, 'sqlalchemy.', poolclass=NullPool)
    sqlahelper.add_engine(engine)

    authn_policy = AuthTktAuthenticationPolicy('secretstring', callback=groupfinder)
    authz_policy = ACLAuthorizationPolicy()

    config = Configurator(
        settings=settings,
        root_factory='newsletter.resources.RootFactory',
        authentication_policy=authn_policy,
        authorization_policy=authz_policy,
        )
    config.include('altair.httpsession.pyramid')
    config.include('altair.browserid')
    config.include('altair.exclog')

    config.add_static_view('static', 'newsletter:static', cache_max_age=3600)
    config.add_view('pyramid.view.append_slash_notfound_view',
                    context='pyramid.httpexceptions.HTTPNotFound')

    config.include('newsletter.newsletters' , route_prefix='/')

    config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')
    config.add_renderer('json'  , 'newsletter.renderers.json_renderer_factory')
    config.add_renderer('csv'   , 'newsletter.renderers.csv_renderer_factory')

    config.scan('newsletter')

    return config.make_wsgi_app()

