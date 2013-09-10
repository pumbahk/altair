from pyramid.config import Configurator
from pyramid.tweens import INGRESS
import altaircms.layout.models
import altaircms.widget.models
import altaircms.page.models
import altaircms.event.models
import altaircms.asset.models
import altaircms.tag.models
import altaircms.auth.models
import sqlahelper
from sqlalchemy import engine_from_config
from core.helper import log_info

def includeme(config):
    config._add_tween("altairsite.tweens.mobile_encoding_convert_factory", under=INGRESS)
    config.include(install_app)

def install_app(config):
    config.include("altair.mobile.install_detector")
    config.include("altair.mobile.install_mobile_request_maker")
    config.include("altairsite.config.install_convinient_request_properties")
    config.include("altairsite.mobile.event")
    config.include('altairsite.mobile.staticpage')
    config.add_route("home", "/")
    config.set_request_property("altairsite.mobile.api.mobile_static_url", "mobile_static_url")
    config.scan(".")

def main(global_config, **settings):
    """ don't use this on production. this is development app."""
    engine = engine_from_config(settings, 'sqlalchemy.', pool_recycle=3600)
    sqlahelper.get_session().remove()
    sqlahelper.add_engine(engine)

    log_info("main", "initialize start.")
    config = Configurator(settings=settings)
    config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')
    config.add_static_view('static', 'altaircms:static', cache_max_age=3600)
    config.add_static_view('plugins/static', 'altaircms:plugins/static', cache_max_age=3600)
    config.add_static_view("staticasset", settings["altaircms.asset.storepath"], cache_max_age=3600)
    config.include("altairsite.install_fetcher")
    config.include('altairsite.separation')
    config.include('altaircms.solr')
    config.include('altaircms.tag.install_tagmanager')
    config.include('altaircms.topic.install_topic_searcher')
    config.set_request_property("altaircms.auth.api.get_allowable_query", "allowable", reify=True)
    config.set_request_property("altairsite.mobile.api.mobile_static_url", "mobile_static_url", reify=True)
    search_utility = settings.get("altaircms.solr.search.utility")
    config.add_fulltext_search(search_utility)
    config.include(install_app)

    ## all requests are treated as mobile request
    config._add_tween("altairsite.tweens.mobile_request_factory", under=INGRESS)

    log_info("main", "initialize end.")
    return config.make_wsgi_app()
