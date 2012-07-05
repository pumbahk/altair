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
    config.set_request_property("altaircms.auth.api.get_allowable_query", "allowable", reify=True)
    iquery = config.maybe_dotted(".auth.interfaces.IAllowableQueryFactory")
    query_factory = config.maybe_dotted(".auth.api.AllowableQueryFactory")
    def register_allowable(modelname, callname):
        """ request.allowable("<call-name>")で呼べるようにモデルを登録する"""
        allowable_query_factory = query_factory(config.maybe_dotted(modelname))
        config.registry.registerUtility(allowable_query_factory, iquery, name=callname)

    register_allowable(".asset.models.Asset", "Asset")
    register_allowable(".asset.models.ImageAsset", "ImageAsset")
    register_allowable(".asset.models.MovieAsset", "MovieAsset")
    register_allowable(".asset.models.FlashAsset", "FlashAsset")
    register_allowable(".event.models.Event", "Event")
    register_allowable(".page.models.Page", "Page")
    register_allowable(".page.models.PageSet", "PageSet")
    register_allowable(".widget.models.WidgetDisposition", "WidgetDisposition")
    register_allowable(".layout.models.Layout", "Layout")
    register_allowable(".plugins.widget.promotion.models.PromotionUnit", "PromotionUnit")
    register_allowable(".plugins.widget.promotion.models.Promotion", "Promotion")
    register_allowable(".models.Category", "Category")
    register_allowable(".topic.models.Topic", "Topic")
    register_allowable(".topic.models.Topcontent", "Topcontent")
    register_allowable(".tag.models.HotWord", "HotWord")
    register_allowable(".tag.models.PageTag", "PageTag")
    register_allowable(".tag.models.AssetTag", "AssetTag")
    register_allowable(".tag.models.ImageAssetTag", "ImageAssetTag")
    register_allowable(".tag.models.MovieAssetTag", "MovieAssetTag")
    register_allowable(".tag.models.FlashAssetTag", "FlashAssetTag")
    register_allowable(".auth.models.Operator", "Operator")


    
    config.add_static_view('static', 'altaircms:static', cache_max_age=3600)
    config.add_static_view('plugins/static', 'altaircms:plugins/static', cache_max_age=3600)
    config.add_static_view("staticasset", settings["altaircms.asset.storepath"], cache_max_age=3600)

    engine = engine_from_config(settings, 'sqlalchemy.')
    sqlahelper.get_session().remove()
    sqlahelper.add_engine(engine)

    return config.make_wsgi_app()
