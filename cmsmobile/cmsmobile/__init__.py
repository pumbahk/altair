from pyramid.config import Configurator
import altaircms.layout.models
import altaircms.widget.models
import altaircms.page.models
import altaircms.event.models
import altaircms.asset.models
import altaircms.tag.models
import altaircms.auth.models
import sqlahelper
from sqlalchemy import engine_from_config


def main(global_config, **settings):

    engine = engine_from_config(settings, 'sqlalchemy.', pool_recycle=3600)
    sqlahelper.get_session().remove()
    sqlahelper.add_engine(engine)

    config = Configurator(settings=settings)
    config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')
    config.add_static_view('static', 'static', cache_max_age=3600)

    config.set_request_property("altaircms.auth.api.get_allowable_query", "allowable", reify=True)

    config.include('cmsmobile.event.company')
    config.include('cmsmobile.event.detailsearch')
    config.include('cmsmobile.event.eventdetail')
    config.include('cmsmobile.event.genre')
    config.include('cmsmobile.event.help')
    config.include('cmsmobile.event.hotword')
    config.include('cmsmobile.event.information')
    config.include('cmsmobile.event.search')

    config.include('altaircms.solr')
    config.include('altaircms.tag')
    config.include('altaircms.topic')
    config.include('altairsite.separation')
    search_utility = settings.get("altaircms.solr.search.utility")
    #search_utility = settings.get("altaircms.solr.search.utility", "altaircms.solr.api.DummySearch")
    config.add_fulltext_search(search_utility)

    config.add_route("home", "/")

    config.scan()

    return config.make_wsgi_app()
