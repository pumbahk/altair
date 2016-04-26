# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from pyramid_beaker import set_cache_regions_from_settings

def _get_policies(settings):
    from altaircms.security import rolefinder
    from pyramid.authentication import AuthTktAuthenticationPolicy
    from pyramid.authorization import ACLAuthorizationPolicy
    from altair.sqlahelper import get_db_session
    import re
    skip_rx = re.compile("^(?:/static|/fanstatic|/staticasset|/plugins/static)/")

    def static_path_skiped(userid, request):
        if skip_rx.search(request.path):
            return []
        else:
            return rolefinder(userid, request, session=get_db_session(request, 'slave'))
    authentication = AuthTktAuthenticationPolicy(settings.get('authtkt.secret'), callback=static_path_skiped, cookie_name='cmstkt')
    authorization = ACLAuthorizationPolicy()
    return authentication, authorization


## mako Undefined object patch. this object behaves as iteable object
def iterable_undefined_patch():
    from mako import runtime
    class IterableUndefined(object):
        def __str__(self):
            raise NameError("Undefined")
        def __nonzero__(self):
            return False
        def __iter__(self):
            return iter([])
    runtime.__dict__["Undefined"] = IterableUndefined
    runtime.__dict__["UNDEFINED"] = IterableUndefined()

def add_request_properties(config):
    from altaircms.api import get_feature_setting_manager
    def fetch_feature_setting_manager(request):
        from .auth.api import fetch_correct_organization
        organization = fetch_correct_organization(request)
        if organization is None:
            logger.error("failed to retrieve organization for user %r" % request.user)
            return None
        return get_feature_setting_manager(request, organization.id)
    config.set_request_property(fetch_feature_setting_manager, "featuresettingmanager", reify=True)
    config.set_request_property(".api.get_cart_domain", "cart_domain", reify=True)

def includeme(config):
    config.include("altaircms.auth", route_prefix='/auth')
    config.include("altairsite.search.install_get_page_tag")
    config.include("altaircms.front", route_prefix="/front")
    config.include("altaircms.widget")
    config.include("altaircms.plugins")
    config.include("altaircms.event")
    config.include("altaircms.layout")
    config.include("altaircms.page")
    config.include("altaircms.topic")
    config.include("altaircms.widget")
    config.include("altaircms.word")
    config.include("altaircms.asset", route_prefix="/asset")
    config.include("altaircms.base")
    config.include("altaircms.tag")

    config.include("altaircms.viewlet")
    config.include("altaircms.panels")
    config.include("altaircms.linklib")
    config.include("altaircms.feature_setting")

    ## slack-off
    config.include("altaircms.slackoff")
    config.include("altairsite.feature") #for sitemap

    ## fulltext search
    config.include("altaircms.solr")
    search_utility = config.registry.settings.get("altaircms.solr.search.utility", "altaircms.solr.api.DummySearch")
    config.add_fulltext_search(search_utility)

    ## request properties
    config.include(add_request_properties)

    ## bind event
    config.add_subscriber(".subscribers.add_request_organization_id",
                          ".subscribers.ModelCreate")
    config.add_subscriber(".subscribers.add_renderer_globals", 
                          "pyramid.events.BeforeRender")
    config.add_subscriber(".subscribers.after_form_initialize", 
                          "pyramid.events.BeforeRender")
    config.add_subscriber(".subscribers.add_choices_query_refinement", 
                          ".subscribers.AfterFormInitialize")

def install_pyramidlayout(config):
    config.include("pyramid_layout")
    config.add_layout(".pyramidlayout.MyLayout", 'altaircms:templates/layout.html') #this is pyramid-layout's layout
    
def install_upload_file(config):
    settings = config.registry.settings
    config.include("altaircms.filelib")
    config.include("altaircms.filelib.s3")
    s3utility = config.maybe_dotted(settings["altaircms.s3.utility"])
    config.add_s3utility(s3utility.from_settings(settings))

def install_separation(config):
    settings = config.registry.settings
    ## organization mapping
    OrganizationMapping = config.maybe_dotted(".auth.api.OrganizationMapping")
    OrganizationMapping(settings["altaircms.organization.mapping.json"]).register(config)

    ## bind authenticated user to request.user
    config.set_request_property("altaircms.auth.helpers.get_authenticated_user", "user", reify=True)
    config.set_request_property("altaircms.auth.helpers.get_authenticated_organization", "organization", reify=True)

    ## allowable query(organizationごとに絞り込んだデータを提供)
    config.set_request_property("altaircms.auth.api.get_allowable_query", "allowable", reify=True)

def exclude_js(path):
    return path.endswith(".js")

def main(global_config, **local_config):
    """ apprications main
    """
    from pyramid.config import Configurator
    from pyramid.session import UnencryptedCookieSessionFactoryConfig

    import sqlahelper
    from sqlalchemy import engine_from_config
    from sqlalchemy.pool import NullPool
    from altaircms.formhelpers import datetime_pick_patch
    datetime_pick_patch()
    from altaircms.security import RootFactory

    settings = dict(global_config)
    settings.update(local_config)
    iterable_undefined_patch()
    session_factory = UnencryptedCookieSessionFactoryConfig(settings.get('session.secret'))
    authn_policy, authz_policy = _get_policies(settings)
    config = Configurator(
        root_factory=RootFactory,
        settings=settings,
        session_factory=session_factory,
        authentication_policy=authn_policy,
        authorization_policy=authz_policy
    )
    config.include("pyramid_mako")
    config.include("altair.sqlahelper")
    set_cache_regions_from_settings(settings)
    config.include("altair.browserid")
    config.include("altair.exclog")
    config.add_mako_renderer('.html')
    config.include("altair.now")

    config.include("altaircms.lib.crud")

    ## include 
    config.include(install_upload_file)
    config.include(install_pyramidlayout)
    config.include(install_separation)
    config.include("altaircms.linklib")
    config.include("altairsite.front.install_resolver")
    config.include("altairsite.install_tracking_image_generator") #hmm.
    config.include("altair.cdnpath")
    from altair.cdnpath import S3StaticPathFactory
    config.add_cdn_static_path(S3StaticPathFactory(
            settings["s3.bucket_name"], 
            exclude=config.maybe_dotted(settings.get("s3.static.exclude.function")), 
            prefix="/usersite"))

    config.include(".")
    config.add_route("smartphone.main", "/smartphone/main")
    config.add_route("smartphone.goto_sp_page", "/smartphone/goto_sp")
    config.add_static_view('static', 'altaircms:static', cache_max_age=3600)
    config.add_static_view('plugins/static', 'altaircms:plugins/static', cache_max_age=3600)
    config.add_static_view("staticasset", settings["altaircms.asset.storepath"], cache_max_age=3600)

    engine = engine_from_config(settings, 'sqlalchemy.', poolclass=NullPool)
    sqlahelper.get_session().remove()
    sqlahelper.add_engine(engine)
    config.add_tween("altaircms.tweens.cms_request_factory")
    app = config.make_wsgi_app()
    from pyramid.interfaces import IRouter
    config.registry.registerUtility(app, IRouter)
    return app
