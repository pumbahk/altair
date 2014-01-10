# -*- coding: utf-8 -*-

from pyramid.config import Configurator

from sqlalchemy import engine_from_config
import sqlahelper

import logging

from .interfaces import ISejTenant

logger = logging.getLogger(__name__)

def includeme(config):
    from .models import ThinSejTenant
    registry = config.registry
    default_sej_tenant = ThinSejTenant(
        shop_id=registry.settings.get('altair.sej.shop_id') or registry.settings.get('sej.shop_id'),
        api_key=registry.settings.get('altair.sej.api_key') or registry.settings.get('sej.api_key'),
        inticket_api_url=registry.settings.get('altair.sej.inticket_api_url') or registry.settings.get('sej.inticket_api_url')
        )
    config.registry.registerUtility(default_sej_tenant, ISejTenant)
    config.include('.communicator')

def setup_routes(config):
    config.add_route('sej.callback'                 , '/callback/')
    config.add_route('sej.callback.form'            , '/callback/form')

def main(global_config, **local_config):
    settings = dict(global_config)
    settings.update(local_config)

    from sqlalchemy.pool import NullPool
    engine = engine_from_config(settings, poolclass=NullPool)
    sqlahelper.add_engine(engine)

    config = Configurator(settings=settings)
    config.set_root_factory('.resources.TicketingApiResource')
    config.registry['sa.engine'] = engine

    config.add_tween('.tweens.encoding_converter_tween_factory')
    config.include(setup_routes, "/altair/sej/")
    config.scan()

    return config.make_wsgi_app()


