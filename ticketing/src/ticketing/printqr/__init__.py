# -*- coding:utf-8 -*-

from pyramid.config import Configurator
from sqlalchemy import engine_from_config
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

    engine = engine_from_config(settings, pool_recycle=3600)
    sqlahelper.add_engine(engine)

    config = Configurator(settings=settings, 
                          root_factory=".resources.PrintQRResource")
    config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')
    config.add_renderer('lxml'  , 'ticketing.renderers.lxml_renderer_factory')

    ## login/logout
    config.include("ticketing.login.internal")
    config.use_internal_login(secret=settings['authtkt.secret'], cookie_name='printqr.auth_tkt', auth_callback=find_group)
    config.setup_internal_login_views(factory=".resources.PrintQRResource", login_html="ticketing.printqr:templates/login.html")
    config.add_forbidden_view("ticketing.login.internal.views.login_view", renderer="ticketing.printqr:templates/login.html")

    config.include("ticketing.qr", route_prefix="qr")
    config.include(".")
    config.include(".jasmine")
    config.add_static_view('static', 'ticketing.printqr:static', cache_max_age=3600)
    config.add_static_view('_static', 'ticketing:static', cache_max_age=10800)
    return config.make_wsgi_app()
