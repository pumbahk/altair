from pyramid.config import Configurator
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

    config.include('cmsmobile.event')
    config.include('altaircms.tag')
    config.include('altaircms.topic')

    config.add_route("home", "/")
    config.scan()

    return config.make_wsgi_app()
