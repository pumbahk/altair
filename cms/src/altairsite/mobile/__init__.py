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

def install_convinient_request_properties(config):
    assert config.registry.settings["altair.orderreview.url"]
    def altair_orderreview_url(request):
        return config.registry.settings["altair.orderreview.url"]

    assert config.registry.settings["getti.orderreview.url"]
    def getti_orderreview_url(request):
        return config.registry.settings["getti.orderreview.url"]

    assert config.registry.settings["sender.mailaddress"]
    def sender_mailaddress(request):
        return config.registry.settings["sender.mailaddress"]

    assert config.registry.settings["inquiry.mailaddress"]
    def inquiry_mailaddress(request):
        return config.registry.settings["inquiry.mailaddress"]

    config.set_request_property(altair_orderreview_url, "altair_orderreview_url", reify=True)
    config.set_request_property(getti_orderreview_url, "getti_orderreview_url", reify=True)
    config.set_request_property(sender_mailaddress, "sender_mailaddress", reify=True)
    config.set_request_property(inquiry_mailaddress, "inquiry_mailaddress", reify=True)
    config.set_request_property(".dispatch.views.mobile_route_path", "mobile_route_path", reify=True)

def install_app(config):
    config.include("altair.mobile.install_detector")
    config.include(install_convinient_request_properties)

    config.include('altairsite.mobile.event.company')
    config.include('altairsite.mobile.event.detailsearch')
    config.include('altairsite.mobile.event.eventdetail')
    config.include('altairsite.mobile.event.genre')
    config.include('altairsite.mobile.event.help')
    config.include('altairsite.mobile.event.hotword')
    config.include('altairsite.mobile.event.information')
    config.include('altairsite.mobile.event.search')
    config.include('altairsite.mobile.event.orderreview')
    config.include('altairsite.mobile.event.inquiry')
    config.include('altairsite.mobile.event.privacy')
    config.include('altairsite.mobile.event.legal')
    config.add_route("home", "/")
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

    config.include('altairsite.separation')
    config.include('altaircms.solr')
    config.include('altaircms.tag.install_tagmanager')
    config.include('altaircms.topic.install_topic_searcher')
    config.set_request_property("altaircms.auth.api.get_allowable_query", "allowable", reify=True)
    search_utility = settings.get("altaircms.solr.search.utility")
    config.add_fulltext_search(search_utility)
    config.include(install_app)

    ## all requests are treated as mobile request
    config._add_tween("altairsite.tweens.mobile_request_factory", under=INGRESS)

    log_info("main", "initialize end.")
    return config.make_wsgi_app()
