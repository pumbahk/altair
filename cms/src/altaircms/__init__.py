# coding:utf-8
import logging
logger = logging.getLogger(__name__)

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



def main(global_config, **local_config):
    """ apprications main
    """
    from pyramid.config import Configurator
    from pyramid.session import UnencryptedCookieSessionFactoryConfig

    import sqlahelper
    from sqlalchemy import engine_from_config


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
    config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')

    ## organization mapping
    OrganizationMapping = config.maybe_dotted(".auth.api.OrganizationMapping")
    OrganizationMapping(settings["altaircms.organization.mapping.json"]).register(config)

    ## bind authenticated user to request.user
    config.set_request_property("altaircms.auth.helpers.get_authenticated_user", "user", reify=True)
    config.set_request_property("altaircms.auth.helpers.get_authenticated_organization", "organization", reify=True)

    config.include("pyramid_layout")
    config.include("altaircms.lib.crud")    
    config.include("altaircms.filelib")


    ## include 
    from altairsite.pyramidlayout import MyLayout as LayoutBase
    class MyLayout(LayoutBase):
        class color:
            event = "#dfd"
            page = "#ffd"
            item = "#ddd"
            asset = "#fdd"
            master = "#ddf"

        def __init__(self, context, request):
            self.context = context
            self.request = request
    config.add_layout(MyLayout, 'altaircms:templates/layout.html') #this is pyramid-layout's layout

    config.include("altaircms.auth", route_prefix='/auth')
    config.include("altaircms.front", route_prefix="/front")
    config.include("altaircms.widget")
    config.include("altaircms.plugins")
    config.include("altaircms.event")
    config.include("altaircms.layout")
    config.include("altaircms.page")
    config.include("altaircms.topic")
    config.include("altaircms.widget")
    config.include("altaircms.asset", route_prefix="/asset")
    config.include("altaircms.base")
    config.include("altaircms.tag")

    config.include("altaircms.viewlet")
    config.include("altaircms.panels")
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

    engine = engine_from_config(settings, 'sqlalchemy.', pool_recycle=3600)
    sqlahelper.get_session().remove()
    sqlahelper.add_engine(engine)
    config.add_tween("altaircms.tweens.cms_request_factory")
    app = config.make_wsgi_app()
    from pyramid.interfaces import IRouter
    config.registry.registerUtility(app, IRouter)
    return app
