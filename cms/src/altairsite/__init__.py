# -*- encoding:utf-8 -*-
from pyramid.config import Configurator
from pyramid_beaker import session_factory_from_settings
from pyramid_beaker import set_cache_regions_from_settings
from sqlalchemy import engine_from_config
import sqlahelper

from altaircms.models import Base
from altair.mobile import PC_ACCESS_COOKIE_NAME #dont't delete it
from altair.extracodecs import register_codecs

def install_fetcher(config):
    settings = config.registry.settings
    config.include("altaircms:install_upload_file") #xxx:
    config.include("altaircms.page.staticupload:install_static_page_utility")
    config.include("altaircms.page.staticupload:install_static_page_cache")
    from altairsite.fetcher import ICurrentPageFetcher
    from altairsite.fetcher import CurrentPageFetcher
    fetcher = CurrentPageFetcher(settings["altaircms.static.pagetype.pc"], 
                                 settings["altaircms.static.pagetype.mobile"], 
                                 settings["altaircms.static.pagetype.smartphone"], 
    )
    config.registry.registerUtility(fetcher, ICurrentPageFetcher)

def install_tracking_image_generator(config):
    settings = config.registry.settings
    from .tracking import ITrackingImageGenerator
    TrackingImage = config.maybe_dotted(settings["altaircms.tracking.image.impl"])
    config.registry.registerUtility(TrackingImage.from_settings(settings, prefix="altaircms.tracking.image."), 
                                    ITrackingImageGenerator)

def main(global_config, **local_config):
    """ This function returns a Pyramid WSGI application.
    """
    settings = dict(global_config)
    settings.update(local_config)
    session_factory = session_factory_from_settings(settings)
    set_cache_regions_from_settings(settings) 
    from sqlalchemy.pool import NullPool
    engine = engine_from_config(settings, poolclass=NullPool,
                                pool_recycle=60)
    sqlahelper.set_base(Base)
    sqlahelper.add_engine(engine)

    register_codecs()

    config = Configurator(settings=settings, session_factory=session_factory)

    config.include("altair.browserid")
    config.include("altair.exclog")

    config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')

    config.include("altair.now")
    # config.include("altaircms.templatelib")

    config.include("altaircms.tag:install_tagmanager")
    config.include("altaircms.topic:install_topic_searcher")
    config.include("altaircms.page:install_pageset_searcher")
    config.include("altaircms.widget:install_has_widget_page_finder")
    config.include("altaircms.asset:install_virtual_asset")
    config.include(install_fetcher)

    ## organization mapping
    OrganizationMapping = config.maybe_dotted("altaircms.auth.api.OrganizationMapping")
    OrganizationMapping(settings["altaircms.organization.mapping.json"]).register(config)
    config.include("altaircms.lib.crud") # todo: remove
    config.include("altaircms.plugins")
    config.include("altaircms.solr") ## for fulltext search
    search_utility = settings.get("altaircms.solr.search.utility", "altaircms.solr.api.DummySearch")
    config.add_fulltext_search(search_utility)

    ## first:
    config.include("altairsite.front")

    ## tween: [encodingfixer, mobile-tween]. the order is important
    # config.include("altair.encodingfixer")
    config.include("altairsite.mobile", route_prefix="/mobile")
    config.include("altairsite.smartphone", route_prefix="/smartphone")
    config.add_tween('altair.encodingfixer.EncodingFixerTween', under='altairsite.tweens.mobile_encoding_convert_factory')

    config.include("altairsite.feature")
    config.include("altairsite.errors")
    config.include("altairsite.search", route_prefix="/search")
    config.include("altairsite.inquiry")
    config.include("altairsite.order")
    config.include("altairsite.preview")

    config.add_static_view('static', 'altaircms:static', cache_max_age=3600)
    config.add_static_view('plugins/static', 'altaircms:plugins/static', cache_max_age=3600)
    config.add_static_view("staticasset", settings["altaircms.asset.storepath"], cache_max_age=3600)


    ## organizationごとのseparate
    config.include(".separation")

    ## front
    config.add_route('front', '/{page_name:.*}', factory=".front.resources.PageRenderingResource") # fix-url after. implemnt preview
    
    config.add_subscriber(".subscribers.add_renderer_globals", 
                          "pyramid.events.BeforeRender")

    # layout
    config.include("pyramid_layout")
    config.add_layout(".pyramidlayout.MyLayout", 'altaircms:templates/usersite/base.html') #this is pyramid-layout's layout

    # tracking
    config.include(install_tracking_image_generator)

    app = config.make_wsgi_app()
    from pyramid.interfaces import IRouter
    config.registry.registerUtility(app, IRouter)
    return app

