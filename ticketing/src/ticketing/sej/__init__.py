# -*- coding: utf-8 -*-

from pyramid.config import Configurator

from sqlalchemy import engine_from_config
import sqlahelper

import logging

logger = logging.getLogger(__name__)

def includeme(config):
    config.add_route('sej.index'                    , '/')
    config.add_route('sej.request'                  , '/request')
    config.add_route('sej.callback'                 , '/callback')

def main(global_config, **settings):
    engine = engine_from_config(settings)
    sqlahelper.add_engine(engine)

    config = Configurator(settings=settings)
    config.set_root_factory('.resources.TicketingApiResource')
    config.registry['sa.engine'] = engine
    config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')
    config.add_renderer('json'  , 'ticketing.renderers.json_renderer_factory')
    config.add_renderer('csv'   , 'ticketing.renderers.csv_renderer_factory')

    config.include('.', "/altair/sej/")
    config.scan()

    return config.make_wsgi_app()


