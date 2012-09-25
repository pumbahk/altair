# -*- coding:utf-8 -*-

from pyramid.config import Configurator
from sqlalchemy import engine_from_config
import sqlahelper
from pyramid_beaker import session_factory_from_settings

import logging
logger = logging.getLogger(__name__)

def main(global_config, **settings):
    engine = engine_from_config(settings, pool_recycle=3600)
    my_session_factory = session_factory_from_settings(settings)
    sqlahelper.add_engine(engine)

    config = Configurator(settings=settings, session_factory=my_session_factory)
    config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')


    config.add_route("index", "/")
    config.scan(".views")

    # config.set_root_factory('.resources.TicketingPrintqrResource')
    config.add_static_view('static', 'ticketing.printqr:static', cache_max_age=3600)
    return config.make_wsgi_app()
