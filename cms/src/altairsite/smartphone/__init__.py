# -*- coding:utf-8 -*-
import functools
import sqlahelper
from pyramid.tweens import INGRESS
from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from altairsite import PC_ACCESS_COOKIE_NAME

def includeme(config):
    #tweenはmobile.__init__で登録されているので追加しない
    config.include(install_app)

def install_app(config):
    ##ここに追加
    settings = config.registry.settings
    config.include("altairsite.config")
    add_route = functools.partial(config.add_route, factory=".resources.TopPageResource")
    add_route("smartphone.main", "/")
    config.smartphone_site_add_view(".views.main", route_name='smartphone.main',request_type="altairsite.tweens.ISmartphoneRequest", 
                             renderer='altairsite.smartphone:templates/top.html')
    config.smartphone_site_add_view(".views.main", route_name='smartphone.main',request_param=PC_ACCESS_COOKIE_NAME, 
                             renderer='altairsite.smartphone:templates/top.html')
    add_route("smartphone.goto_pc_page", "/goto_pc")
    add_route("smartphone.goto_sp_page", "/goto_sp")

    config.include("altair.cdnpath")
    from altair.cdnpath import S3StaticPathFactory
    config.add_cdn_static_path(S3StaticPathFactory(
            settings["s3.bucket_name"],
            exclude=config.maybe_dotted(settings.get("s3.static.exclude.function")),
            prefix="/usersite"))

    config.include('altairsite.smartphone.genre')
    config.include('altairsite.smartphone.search')
    config.include('altairsite.smartphone.detail')
    config.include('altairsite.smartphone.page')
    config.scan(".")

def main(config, **settings):
    """ don't use this on production. this is development app."""    
    engine = engine_from_config(settings, 'sqlalchemy.', pool_recycle=3600)
    sqlahelper.get_session().remove()
    sqlahelper.add_engine(engine)

    config = Configurator(settings=settings)
    config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')
    config.add_static_view('static', 'altaircms:static', cache_max_age=3600)
    config.add_static_view('plugins/static', 'altaircms:plugins/static', cache_max_age=3600)
    config.add_static_view("staticasset", settings["altaircms.asset.storepath"], cache_max_age=3600)
    OrganizationMapping = config.maybe_dotted("altaircms.auth.api.OrganizationMapping")
    OrganizationMapping(settings["altaircms.organization.mapping.json"]).register(config)

    config.include('altairsite.separation')
    config.include('altaircms.solr')
    config.include('altaircms.tag.install_tagmanager')
    config.include('altaircms.topic.install_topic_searcher')
    config.include('altaircms.asset.install_virtual_asset')    
    config.include("altaircms.widget:install_has_widget_page_finder")
    config.include("altaircms.lib.crud") # todo: remove
    config.include("altaircms.plugins")
    config.set_request_property("altaircms.auth.api.get_allowable_query", "allowable", reify=True)
    search_utility = settings.get("altaircms.solr.search.utility")
    config.add_fulltext_search(search_utility)
    config.include(install_app)
    config.smartphone_site_add_view(".views.main_pc", route_name='smartphone.main',renderer="altairsite.smartphone:templates/pcsite.mock.html")
    config.include("altairsite.config.install_convinient_request_properties")
    ## all requests are treated as mobile request
    config._add_tween("altairsite.tweens.smartphone_request_factory", under=INGRESS)
    return config.make_wsgi_app()
