# -*- encoding:utf-8 -*-

from pyramid.config import Configurator
from sqlalchemy import engine_from_config
import sqlahelper

from altaircms.models import Base

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    sqlahelper.get_session().remove()
    sqlahelper.set_base(Base)
    sqlahelper.add_engine(engine)

    config = Configurator(settings=settings)

    config.include("altaircms.plugins")
    config.include("altaircms.solr") ## for fulltext search
    search_utility = settings.get("altaircms.solr.search.utility", "altaircms.solr.api.DummySearch")
    config.add_fulltext_search(search_utility)

    config.include("altairsite.mobile")
    config.add_tween("altairsite.mobile.tweens.mobile_encoding_convert_factory")

    config.include("altairsite.front")
    config.include("altairsite.errors")
    config.include("altairsite.rakuten_auth")
    config.include("altairsite.search", route_prefix="search")
    config.add_static_view('static', 'altaircms:static', cache_max_age=3600)
    config.add_static_view('plugins/static', 'altaircms:plugins/static', cache_max_age=3600)
    config.add_static_view("staticasset", settings["altaircms.asset.storepath"], cache_max_age=3600)

    ## 楽天ログイン
    config.add_route('top', '/rakuten/rauth/')
    config.add_view('altairsite.rakuten_auth.index', route_name="top")
    config.add_route('signout', '/rakuten/rauth/signout')
    config.add_view('altairsite.rakuten_auth.signout', route_name='signout')
    config.add_route('rakuten_auth.login', '/rakuten/rauth/login')
    config.add_route('rakuten_auth.verify', '/rakuten/rauth/verify')


    config.add_route('front', '/{page_name:.*}', factory=".front.resources.PageRenderingResource") # fix-url after. implemnt preview
    
    config.add_subscriber(".subscribers.add_renderer_globals", 
                          "pyramid.events.BeforeRender")
    return config.make_wsgi_app()

