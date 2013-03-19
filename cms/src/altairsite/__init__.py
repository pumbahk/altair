# -*- encoding:utf-8 -*-

from pyramid.config import Configurator
from sqlalchemy import engine_from_config
import sqlahelper

from altaircms.models import Base

def main(global_config, **local_config):
    """ This function returns a Pyramid WSGI application.
    """
    settings = dict(global_config)
    settings.update(local_config)
    engine = engine_from_config(settings, 'sqlalchemy.', pool_recycle=3600)
    sqlahelper.get_session().remove()
    sqlahelper.set_base(Base)
    sqlahelper.add_engine(engine)

    config = Configurator(settings=settings)
    config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')
    config.include("altaircms.tag:install_tagmanager")
    config.include("altaircms.topic:install_topic_searcher")
    config.include("altaircms.page:install_pageset_searcher")
    config.include("altaircms.widget:install_has_widget_page_finder")

    ## organization mapping
    OrganizationMapping = config.maybe_dotted("altaircms.auth.api.OrganizationMapping")
    OrganizationMapping(settings["altaircms.organization.mapping.json"]).register(config)
    config.include("altaircms.lib.crud")    

    config.include("altaircms.plugins")
    config.include("altaircms.solr") ## for fulltext search
    search_utility = settings.get("altaircms.solr.search.utility", "altaircms.solr.api.DummySearch")
    config.add_fulltext_search(search_utility)

    config.include("altairsite.mobile")


    config.include("altairsite.front")
    config.include("altairsite.errors")
    config.include("altairsite.search", route_prefix="search")

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
    return config.make_wsgi_app()

