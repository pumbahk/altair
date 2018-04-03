# encoding: utf-8

import sqlahelper

from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from sqlalchemy.pool import NullPool

def main(global_config, **local_config):
    settings = dict(global_config)
    settings.update(local_config)

    engine = engine_from_config(settings, poolclass=NullPool, isolation_level='READ COMMITTED')
    sqlahelper.add_engine(engine)

    config = Configurator(
        settings=settings,
    )
    config.include('pyramid_dogpile_cache')
    config.include('altair.httpsession.pyramid')
    config.include('altair.sqlahelper')

    config.include('.api', route_prefix='/api')
    config.scan('.')

    return config.make_wsgi_app()