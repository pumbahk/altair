# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from zope.interface import implementer
from .interfaces import IAPIEndpointCollector

@implementer(IAPIEndpointCollector)
class APIEndpointRouteCollector(object):
    def __init__(self):
        self.routes = set()
        self.extras = {}

    def add(self, name):
        self.routes.add(name)

    def add_extra(self, name, url):
        self.extras[name] = url

    def get_endpoints(self, request):
        #foo.bar -> foo_bar #for json
        endpoints = {k.replace(".", "_"):request.route_url(k) for k in self.routes}
        endpoints.update(self.extras)
        return endpoints

def add_endpoint_route(config, name, *args, **kwargs):
    collector = config.registry.queryUtility(IAPIEndpointCollector)
    if collector is None:
        collector = APIEndpointRouteCollector()
        config.registry.registerUtility(collector, IAPIEndpointCollector)
    config.add_route(name, *args, **kwargs)
    collector.add(name)

def add_endpoint_extra(config, name, url):
    collector = config.registry.queryUtility(IAPIEndpointCollector)
    if collector is None:
        collector = APIEndpointRouteCollector()
        config.registry.registerUtility(collector, IAPIEndpointCollector)
    collector.add_extra(name, url)

def includeme(config):
    config.add_directive("add_endpoint_route", add_endpoint_route)
    config.add_directive("add_endpoint_extra", add_endpoint_extra)

