# coding:utf-8

from altaircms.lib.formhelpers import datetime_pick_patch
datetime_pick_patch()

import re
import warnings

import logging
logger = logging.getLogger(__name__)

from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.settings import asbool

import sqlahelper
from sqlalchemy import engine_from_config

from altaircms.security import rolefinder, RootFactory

try:
    import pymysql_sa
    pymysql_sa.make_default_mysql_dialect()
    logger.info('Using PyMySQL')
except:
    pass


def main_with_strip_secret(global_config, settings):
    D = {"altaircms.debug.strip_security": True}
    settings.update(D)
    return main(global_config, **settings)


def _get_policies(settings):
    from pyramid.authentication import AuthTktAuthenticationPolicy
    from pyramid.authorization import ACLAuthorizationPolicy
    return  AuthTktAuthenticationPolicy(settings.get('authtkt.secret'), callback=rolefinder, cookie_name='cmstkt'), \
        ACLAuthorizationPolicy()

def main(global_config, **settings):
    """ apprications main
    """
    session_factory = UnencryptedCookieSessionFactoryConfig(settings.get('session.secret'))
    authn_policy, authz_policy = _get_policies(settings)
    config = Configurator(
        root_factory=RootFactory,
        settings=settings,
        session_factory=session_factory,
        authentication_policy=authn_policy,
        authorization_policy=authz_policy
    )

    ## bind authenticated user to request.user
    if asbool(settings.get("altaircms.debug.strip_security", 'false')):
        config.set_request_property("altaircms.auth.helpers.get_debug_user", "user", reify=True)
    else:
        config.set_request_property("altaircms.auth.helpers.get_authenticated_user", "user", reify=True)


    config.include("altaircms.lib.crud")    

    ## include
    config.include("altaircms.auth", route_prefix='/auth')
    config.include("altaircms.front", route_prefix="f")
    config.include("altaircms.widget")
    config.include("altaircms.plugins")
    config.include("altaircms.event")
    config.include("altaircms.layout")
    config.include("altaircms.page")
    config.include("altaircms.widget")
    config.include("altaircms.asset", route_prefix="/asset")
    config.include("altaircms.base")
    config.include("altaircms.tag")

    ## slack-off
    config.include("altaircms.slackoff")

    ## fulltext search
    config.include("altaircms.solr")
    search_utility = settings.get("altaircms.solr.search.utility", "altaircms.solr.api.DummySearch")
    config.add_fulltext_search(search_utility)

    ## bind event
    config.add_subscriber(".subscribers.add_renderer_globals", 
                          "pyramid.events.BeforeRender")
    config.add_subscriber(".subscribers.after_form_initialize", 
                          "pyramid.events.BeforeRender")
    config.add_subscriber(".subscribers.add_choices_query_refinement", 
                          ".lib.formevent.AfterFormInitialize")
    # config.scan('.subscribers')
    
    config.add_static_view('static', 'altaircms:static', cache_max_age=3600)
    config.add_static_view('plugins/static', 'altaircms:plugins/static', cache_max_age=3600)
    config.add_static_view("staticasset", settings["altaircms.asset.storepath"], cache_max_age=3600)

    engine = engine_from_config(settings, 'sqlalchemy.')
    sqlahelper.get_session().remove()
    sqlahelper.add_engine(engine)

    ## 設定ファイルを読み込んで追加でinclude.(debug用)
    if asbool(settings.get("altaircms.debug.start_when_dropall", "false")):
        from altaircms.models import initialize_sql
        warnings.warn("altaircms.debug.start_when_dropall is true. all table are dropped!")
        initialize_sql(engine, dropall=True)

    if settings.get("altaircms.debug.additional_includes"):
        for m in re.split("\s+", settings.get("altaircms.debug.additional_includes").lstrip()):
            warnings.warn("------------additional include " + m)
            config.include(m); config.scan(m)
    return config.make_wsgi_app()
