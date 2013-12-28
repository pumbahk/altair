# -*- coding:utf-8 -*-

from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from sqlalchemy.pool import NullPool
import sqlahelper

import logging
logger = logging.getLogger(__name__)
from zope.interface import Interface, implementer

class IAPIEndpointCollector(Interface):
    def add(name):
        pass
    def get_endpoints(request):
        pass

@implementer(IAPIEndpointCollector)
class APIEndpointRouteCollector(object):
    def __init__(self):
        self.routes = set()

    def add(self, name):
        self.routes.add(name)

    def get_endpoints(self, request):
        return {k:request.route_url(k) for k in self.routes}

def add_endpoint_route(config, name, *args, **kwargs):
    collector = config.registry.queryUtility(IAPIEndpointCollector)
    if collector is None:
        collector = APIEndpointRouteCollector()
        config.registry.registerUtility(collector, IAPIEndpointCollector)
    config.add_route(name, *args, **kwargs)
    collector.add(name)

def includeme(config):
    config.add_directive("add_endpoint_route", add_endpoint_route)
    config.add_endpoint_route("login.status", "/login/status")
    config.add_endpoint_route("performance.list", "/performance/list")
    config.add_endpoint_route("qr.ticketdata", "/qr/ticketdata")
    config.add_endpoint_route("qr.svgsource.one", "/qr/svgsource/one")
    config.add_endpoint_route("qr.svgsource.all", "/qr/svgsource/all")
    config.scan(".views")

"""
/login
/logout
"""

def find_group(user_id, request):
    return ["group:sales_counter"]

def main(global_config, **local_config):
    settings = dict(global_config)
    settings.update(local_config)

    engine = engine_from_config(settings, poolclass=NullPool)
    sqlahelper.add_engine(engine)

    config = Configurator(settings=settings, 
                          root_factory=".resources.CheckinStationResource")
    config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')
    config.add_renderer('lxml'  , 'altair.app.ticketing.renderers.lxml_renderer_factory')

    ## login/logout
    config.include('altair.app.ticketing.login.internal')
    config.use_internal_login(secret=settings['authtkt.secret'], cookie_name='checkinstation.auth_tkt', auth_callback=find_group)
    config.setup_internal_login_api_views(factory=".resources.CheckinStationResource")

    ## svg builder
    config.include('altair.app.ticketing.tickets.setup_svg')
    config.include('altair.app.ticketing.qr', route_prefix='qr')
    config.include(".")
    config.add_static_view('static', 'altair.app.ticketing.checkinstation:static', cache_max_age=3600)
    config.add_static_view('_static', 'altair.app.ticketing:static', cache_max_age=10800)
    return config.make_wsgi_app()
