#-*- coding: utf-8 -*-
from altair.app.ticketing import newRootFactory

def add_routes(config, route_url_resource):
    for route, values in route_url_resource.items():
        url, resource_class = values
        kwds = {}
        if resource_class:
            kwds['factory'] = newRootFactory(resource_class)
        config.add_route(route, url, **kwds)


import re

class DuplicateInstallError(Exception):
    pass

class RequestAccessor(object):
    in_params = {}
    in_matchdict = {}

    _regx_all = re.compile('^(?P<name>\S+)_all$')
    def __init__(self, request):
        self._validate()
        self._request = request

    def _validate(self):
        all_names = self.in_params.keys() + self.in_matchdict.keys()
        error_names = [name for name in all_names if all_names.count(name) != 1 or all_names.count(name+'_all') != 0]
        if error_names:
            raise DuplicateInstallError('Duplicate installed: {} in {}'.format(
                error_names, self.__class__.__name__))

    def __getattr__(self, name):
        if name in self.in_matchdict:
            type_ self.in_matchdict[name]
            value = self._request.matchdict[name]
            return type_(value)
        elif name in self.in_params:
            type_ self.in_params[name]
            value = self._request.params.get(name)
            return type_(value)

        match = self._regx_all.match(name)
        if match:
            name = match.group('name')

            if name in self.in_matchdict:
                type_ self.in_matchdict[name]
                values = [self._request.matchdict[name]]
                return map(type_, values)
            elif name in self.in_params:
                type_ self.in_params[name]
                values = self._request.params.getall(name)
                return map(type_, values)
        raise AttributeError(name)
