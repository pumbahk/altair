# coding:utf-8

from altaircms.lib.formhelpers import datetime_pick_patch
datetime_pick_patch()

import re
import warnings

import logging
logger = logging.getLogger(__name__)

from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig

import sqlahelper
from sqlalchemy import engine_from_config

from altaircms.security import rolefinder, RootFactory

try:
    import pymysql_sa
    pymysql_sa.make_default_mysql_dialect()
    logger.info('Using PyMySQL')
except:
    pass

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
    config.set_request_property("altaircms.auth.helpers.get_authenticated_user", "user", reify=True)
    config.set_request_property("altaircms.auth.helpers.get_authenticated_organization", "organization", reify=True)
    config.set_request_property("altaircms.auth.api.get_allowable_query", "allowable", reify=True)

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
    config.add_subscriber(".subscribers.add_renderer_globals", 
                          "pyramid.events.BeforeRender")
    config.add_subscriber(".subscribers.after_form_initialize", 
                          "pyramid.events.BeforeRender")
    config.add_subscriber(".subscribers.add_choices_query_refinement", 
                          ".lib.formevent.AfterFormInitialize")

    ## allowable query(organizationごとに絞り込んだデータを提供)
    iquery = config.maybe_dotted(".auth.interfaces.IAllowableQueryFactory")
    query_factory = config.maybe_dotted(".auth.api.AllowableQueryFactory")
    
    config.registry.registerUtility(query_factory(config.maybe_dotted(".asset.models.ImageAsset")), iquery, name="ImageAsset")
    config.registry.registerUtility(query_factory(config.maybe_dotted(".asset.models.MovieAsset")), iquery, name="MovieAsset")
    config.registry.registerUtility(query_factory(config.maybe_dotted(".asset.models.FlashAsset")), iquery, name="FlashAsset")
    config.registry.registerUtility(query_factory(config.maybe_dotted(".event.models.Event")), iquery, name="Event")
    config.registry.registerUtility(query_factory(config.maybe_dotted(".page.models.Page")), iquery, name="Page")
    config.registry.registerUtility(query_factory(config.maybe_dotted(".page.models.PageSet")), iquery, name="PageSet")
    config.registry.registerUtility(query_factory(config.maybe_dotted(".widget.models.WidgetDisposition")), iquery, name="WidgetDisposition")
    config.registry.registerUtility(query_factory(config.maybe_dotted(".layout.models.Layout")), iquery, name="Layout")
    config.registry.registerUtility(query_factory(config.maybe_dotted(".plugins.widget.promotion.models.PromotionUnit")), iquery, name="PromotionUnit")
    config.registry.registerUtility(query_factory(config.maybe_dotted(".plugins.widget.promotion.models.Promotion")), iquery, name="Promotion")
    config.registry.registerUtility(query_factory(config.maybe_dotted(".models.Category")), iquery, name="Category")
    config.registry.registerUtility(query_factory(config.maybe_dotted(".topic.models.Topic")), iquery, name="Topic")
    config.registry.registerUtility(query_factory(config.maybe_dotted(".topic.models.Topcontent")), iquery, name="Topcontent")
    config.registry.registerUtility(query_factory(config.maybe_dotted(".tag.models.HotWord")), iquery, name="HotWord")
    # config.registry.registerUtility(query_factory(config.maybe_dotted("")), iquery, name="")

    
    config.add_static_view('static', 'altaircms:static', cache_max_age=3600)
    config.add_static_view('plugins/static', 'altaircms:plugins/static', cache_max_age=3600)
    config.add_static_view("staticasset", settings["altaircms.asset.storepath"], cache_max_age=3600)

    engine = engine_from_config(settings, 'sqlalchemy.')
    sqlahelper.get_session().remove()
    sqlahelper.add_engine(engine)

    return config.make_wsgi_app()
