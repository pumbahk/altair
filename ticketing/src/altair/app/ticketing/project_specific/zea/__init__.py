# encoding: utf-8

import codecs
from pyramid.config import Configurator
import sqlahelper
from sqlalchemy import engine_from_config
from .resources import FCAdminEventIndexResource, FCAdminEventResource

def replace_with_geta_handler(e):
    return (u'〓', e.start + 1)

def main(global_config, **local_config):
    settings = dict(global_config)
    settings.update(local_config)
    codecs.register_error('replace_with_geta', replace_with_geta_handler)
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

    config.add_route('zea.index', '/zea', factory=FCAdminEventIndexResource)
    config.add_route('zea.detail', '/zea/{event_id}', factory=FCAdminEventResource)
    config.add_route('yoshida-rinne.index', '/yoshida-rinne', factory=FCAdminEventIndexResource)
    config.add_route('yoshida-rinne.detail', '/yoshida-rinne/{event_id}', factory=FCAdminEventResource)
    config.scan('.')
    return config.make_wsgi_app()
