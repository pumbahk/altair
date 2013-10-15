# -*- coding: utf-8 -*-

from pyramid.config import Configurator

from sqlalchemy import engine_from_config
import sqlahelper

import logging

logger = logging.getLogger(__name__)

def includeme(config):
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
    config.include('.', "/altair/sej/")
    config.scan()

    return config.make_wsgi_app()


