from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from cmsmobile.core.models import (
    DBSession,
    Base,
    )


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')

    config.include('cmsmobile.detail')
    config.include('cmsmobile.genre')
    config.include('cmsmobile.order')
    config.include('cmsmobile.injury')
    config.include('cmsmobile.search')
    config.include('cmsmobile.top')

    config.scan()
    return config.make_wsgi_app()
