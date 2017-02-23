# -*- coding:utf-8 -*-
import sqlahelper

from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from sqlalchemy.pool import NullPool


def empty_resource_factory(request):
    return None


def main(global_config, **local_config):
    settings = dict(global_config)
    settings.update(local_config)

    engine = engine_from_config(settings, poolclass=NullPool, isolation_level='READ COMMITTED')
    sqlahelper.add_engine(engine)

    config = Configurator(
        settings=settings,
        root_factory=empty_resource_factory
        )

    from altair.httpsession.pyramid import register_utilities as register_httpsession_utilities
    register_httpsession_utilities(config, skip_http_backend_registration=True)

    from altair.pyramid_extra_renderers.json import JSON
    config.add_renderer('json', JSON())
    config.include('pyramid_tm')
    config.include('pyramid_dogpile_cache')
    config.include('altair.browserid')
    config.include('altair.exclog')
    config.include('altair.sqlahelper')
    config.add_route('cart.api.index', '/api/v1/', request_method='GET')

    config.scan('.views')

    return config.make_wsgi_app()
