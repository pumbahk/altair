# -*- coding:utf-8 -*-

from pyramid.config import Configurator
from sqlalchemy import engine_from_config
import sqlahelper

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

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

    config.add_route("login", "/login")
    config.add_route("logout", "/logout")

    config.add_route("misc.order.qr", "/_misc/order/qr")
    config.scan(".views")


def main(global_config, **settings):
    from ticketing.logicaldeleting import install as install_ld
    install_ld()

    engine = engine_from_config(settings, pool_recycle=3600)
    sqlahelper.add_engine(engine)

    config = Configurator(settings=settings, 
                          root_factory=".resources.PrintQRResource")
    authorization_policy = ACLAuthorizationPolicy()
    config.set_authorization_policy(authorization_policy)
    authentication_policy = AuthTktAuthenticationPolicy(secret=settings['authtkt.secret'],cookie_name='printqr.auth_tkt',
                                                        callback=config.maybe_dotted('.security.find_group'))
    config.set_authentication_policy(authentication_policy)
    config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')
    config.add_renderer('lxml'  , 'ticketing.renderers.lxml_renderer_factory')

    config.include("ticketing.qr", route_prefix="qr")
    config.include(".")
    config.add_forbidden_view(".views.login_view", renderer="ticketing.printqr:templates/login.html")
    config.add_static_view('static', 'ticketing.printqr:static', cache_max_age=3600)
    config.add_static_view('_static', 'ticketing:static', cache_max_age=10800)
    return config.make_wsgi_app()
