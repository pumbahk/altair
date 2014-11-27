from pyramid.config import Configurator
import sqlahelper
from sqlalchemy import engine_from_config

def main(global_config, **local_config):
    settings = dict(global_config)
    settings.update(local_config)
    from sqlalchemy.pool import NullPool
    engine = engine_from_config(settings, poolclass=NullPool, isolation_level='READ COMMITTED')
    sqlahelper.add_engine(engine)
    from altair.app.ticketing import install_ld
    config = Configurator(
        settings=settings,
        root_factory='.resources.root_factory'
        )
    config.include('altair.exclog')
    config.include('altair.sqlahelper')
    config.include('pyramid_tm')
    config.include('pyramid_mako')
    config.include('pyramid_fanstatic')
    config.add_mako_renderer('.mako') 
    config.include('.resources')
    config.scan('.')
    return config.make_wsgi_app() 
