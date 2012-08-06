# coding:utf-8

from altaircms.helpers.formhelpers import datetime_pick_patch
datetime_pick_patch()

import logging
logger = logging.getLogger(__name__)

from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig

import sqlahelper
from sqlalchemy import engine_from_config

from altaircms.security import RootFactory

try:
    import pymysql_sa
    pymysql_sa.make_default_mysql_dialect()
    logger.info('Using PyMySQL')
except:
    pass

def _get_policies(settings):
    from altaircms.security import rolefinder
    from pyramid.authentication import AuthTktAuthenticationPolicy
    from pyramid.authorization import ACLAuthorizationPolicy
    import re
    skip_rx = re.compile("^(?:/static|/fanstatic|/staticasset|/plugins/static)/")

    def static_path_skiped(userid, request):
        if skip_rx.search(request.path):
            return []
        else:
            return rolefinder(userid, request)
    authentication = AuthTktAuthenticationPolicy(settings.get('authtkt.secret'), callback=static_path_skiped, cookie_name='cmstkt')
    authorization = ACLAuthorizationPolicy()
    return authentication, authorization


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

    ## organization mapping
    OrganizationMapping = config.maybe_dotted(".auth.api.OrganizationMapping")
    OrganizationMapping(settings["altaircms.organization.mapping.json"]).register(config)

    ## bind authenticated user to request.user
    config.set_request_property("altaircms.auth.helpers.get_authenticated_user", "user", reify=True)
    config.set_request_property("altaircms.auth.helpers.get_authenticated_organization", "organization", reify=True)

    config.include("altaircms.lib.crud")    

    ## include
    config.include("altaircms.auth", route_prefix='/auth')
    config.include("altaircms.front", route_prefix="/front")
    config.include("altaircms.widget")
    config.include("altaircms.plugins")
    config.include("altaircms.event")
    config.include("altaircms.layout")
    config.include("altaircms.page")
    config.include("altaircms.widget")
    config.include("altaircms.asset", route_prefix="/asset")
    config.include("altaircms.base")
    config.include("altaircms.tag")

    config.include("altaircms.viewlet")
    ## slack-off
    config.include("altaircms.slackoff")

    ## fulltext search
    config.include("altaircms.solr")
    search_utility = settings.get("altaircms.solr.search.utility", "altaircms.solr.api.DummySearch")
    config.add_fulltext_search(search_utility)

    ## bind event
    config.add_subscriber(".subscribers.add_request_organization_id",
                          ".subscribers.ModelCreate")
    config.add_subscriber(".subscribers.add_renderer_globals", 
                          "pyramid.events.BeforeRender")
    config.add_subscriber(".subscribers.after_form_initialize", 
                          "pyramid.events.BeforeRender")
    config.add_subscriber(".subscribers.add_choices_query_refinement", 
                          ".subscribers.AfterFormInitialize")

    ## allowable query(organizationごとに絞り込んだデータを提供)
    config.set_request_property("altaircms.auth.api.get_allowable_query", "allowable", reify=True)
    
    config.add_static_view('static', 'altaircms:static', cache_max_age=3600)
    config.add_static_view('plugins/static', 'altaircms:plugins/static', cache_max_age=3600)
    config.add_static_view("staticasset", settings["altaircms.asset.storepath"], cache_max_age=3600)

    engine = engine_from_config(settings, 'sqlalchemy.')
    sqlahelper.get_session().remove()
    sqlahelper.add_engine(engine)
    
    return config.make_wsgi_app()
