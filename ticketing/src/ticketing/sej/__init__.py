# -*- coding: utf-8 -*-

from pyramid.config import Configurator

from sqlalchemy import engine_from_config
import sqlahelper

import logging

logger = logging.getLogger(__name__)

def includeme(config):
    config.add_route('sej.callback'                 , '/callback')
    config.add_route('sej.callback.form'            , '/callback/form')

def main(global_config, **settings):
    engine = engine_from_config(settings)
    sqlahelper.add_engine(engine)

    config = Configurator(settings=settings)
    config.set_root_factory('.resources.TicketingApiResource')
    config.registry['sa.engine'] = engine

    config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')

    config.include('.', "/altair/sej/")
    config.scan()

    return config.make_wsgi_app()


