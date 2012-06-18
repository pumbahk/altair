# -*- encoding:utf-8 -*-

from pyramid.config import Configurator
from sqlalchemy import engine_from_config
import sqlahelper

from altaircms.models import Base
import altaircms.models as models
import altaircms.auth.models
import altaircms.asset.models
import altaircms.widget.models
import altaircms.page.models
import altaircms.usersetting.models
import altaircms.event.models
import altaircms.topic.models
import altaircms.layout.models

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    sqlahelper.get_session().remove()
    sqlahelper.set_base(Base)
    sqlahelper.add_engine(engine)

    config = Configurator(settings=settings)
    config.include("altaircms.solr")

    ##
    search_utility = settings["altaircms.solr.search.utility"]
    config.add_fulltext_search(search_utility)


    config.add_static_view('static', 'altaircms:static', cache_max_age=3600)
    config.add_static_view('plugins/static', 'altaircms:plugins/static', cache_max_age=3600)
    config.add_static_view("staticasset", settings["altaircms.asset.storepath"], cache_max_age=3600)
    config.add_subscriber("altairsite.subscribers.add_renderer_globals", 
                          "pyramid.events.BeforeRender")

    config.add_route("mobile_detail", "/mobile/detail/{pageset_id}")
    config.add_route("mobile_index", "/mobile/index")
    config.add_route("mobile_category", "/mobile/genre/{category}")
    config.add_route("mobile_purchase", "/mobile/purchase/event/{event_id}", static=True)
    config.add_route("mobile_search", "/mobile/search")

    config.scan(".views")
    return config.make_wsgi_app()
