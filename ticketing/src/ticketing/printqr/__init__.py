# -*- coding:utf-8 -*-

from pyramid.config import Configurator
from sqlalchemy import engine_from_config
import sqlahelper
from pyramid_beaker import session_factory_from_settings

import logging
logger = logging.getLogger(__name__)

def main(global_config, **settings):
    engine = engine_from_config(settings, pool_recycle=3600)
    sqlahelper.add_engine(engine)

    config = Configurator(settings=settings, 
                          session_factory=session_factory_from_settings(settings), 
                          root_factory=".resources.PrintQRResource")
    config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')
    config.add_renderer('lxml'  , 'ticketing.renderers.lxml_renderer_factory')

    config.include("ticketing.qr", route_prefix="qr")

    config.add_route("index", "/")
    config.add_route("api.ticket.data", "/api/ticket/data")
    config.add_route('api.applet.formats', '/api/applet/formats')
    config.add_route('api.applet.enqueue', '/api/applet/enqueue')
    config.add_route('api.applet.peek', '/api/applet/peek')
    config.add_route('api.applet.dequeue', '/api/applet/dequeue')

    config.scan(".views")

    # config.set_root_factory('.resources.TicketingPrintqrResource')
    config.add_static_view('static', 'ticketing.printqr:static', cache_max_age=3600)
    config.add_static_view('_static', 'ticketing:static', cache_max_age=10800)
    return config.make_wsgi_app()
