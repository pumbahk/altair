# -*- coding:utf-8 -*-

from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from sqlalchemy.pool import NullPool
import sqlahelper

import logging
logger = logging.getLogger(__name__)

def includeme(config):
    config.add_route("qrapp", "/qrapp/{event_id}")
    config.add_route("eventlist", "/")    
    config.add_route("api.ticket.data", "/api/ticket/data/{event_id}")
    config.add_route("api.ticket.after_printed", "/api/ticket/after_printed")
    config.add_route("api.ticket.after_printed_order", "/api/ticket/after_printed_order")
    config.add_route("api.ticket.refresh.printed_status", "/api/ticket/refresh_printed_status")
    config.add_route("api.log", "/api/log")
    config.add_route('api.applet.ticket', '/api/applet/ticket/{event_id}/{id:.*}')
    config.add_route('api.applet.ticket_data', '/api/applet/ticket_data')
    config.add_route('api.applet.ticket_data_order', '/api/applet/ticket_data_order')
    config.add_route('api.applet.history', '/api/applet/history')

    config.add_route("progress", "/progress/{event_id}")
    config.add_route('api.progress.total_result_data', '/api/progress/total_result/{event_id}')
    config.add_route("misc.order.qr", "/_misc/order/qr")
    config.scan(".views")

def find_group(user_id, request):
    return ["group:sales_counter"]

def main(global_config, **local_config):
    settings = dict(global_config)
    settings.update(local_config)

    engine = engine_from_config(settings, poolclass=NullPool)
    sqlahelper.add_engine(engine)

    config = Configurator(settings=settings, 
                          root_factory=".resources.PrintQRResource")
    config.include('altair.app.ticketing.setup_beaker_cache')
    config.include('altair.httpsession.pyramid')
    config.include('pyramid_mako')
    config.add_mako_renderer('.html')
    from altair.pyramid_extra_renderers.xml import XML

    ## login/logout
    config.include('altair.app.ticketing.login.internal')
    config.use_internal_login(secret=settings['authtkt.secret'], cookie_name='printqr.auth_tkt', auth_callback=find_group)
    config.setup_internal_login_views(factory=".resources.PrintQRResource", login_html="altair.app.ticketing.printqr:templates/login.html")
    config.add_forbidden_view("altair.app.ticketing.login.internal.views.login_view", renderer="altair.app.ticketing.printqr:templates/login.html")

    config.include('altair.app.ticketing.qr', route_prefix='qr')
    config.include("altair.exclog")
    config.include(".")
    config.include(".jasmine")
    config.add_static_view('static', 'altair.app.ticketing.printqr:static', cache_max_age=3600)
    config.add_static_view('_static', 'altair.app.ticketing:static', cache_max_age=10800)
    return config.make_wsgi_app()
