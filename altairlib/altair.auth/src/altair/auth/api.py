from __future__ import absolute_import

import os
import logging
from pyramid.interfaces import IRequest
from repoze.who.interfaces import IIdentifier
from .interfaces import IWhoAPIDecider, IWhoAPIFactoryRegistry

logger = logging.getLogger(__name__)

__all__ = [
    'get_current_request',
    'decide',
    'get_who_api_factory_registry',
    'who_api_factory',
    'list_who_api_factory',
    'who_api',
    'resolve_api_name',
    ]

def get_current_request(environ):
    from . import REQUEST_KEY
    return environ.get(REQUEST_KEY)

def decide(request):
    api_name = request.environ.get('altair.auth.who_api_name')
    if api_name is None:
        decider = request.registry.getAdapter(request, IWhoAPIDecider)
        request.environ['altair.auth.who_api_name'] = api_name = decider.decide()
    return api_name

def get_who_api_factory_registry(request_or_registry):
    if IRequest.providedBy(request_or_registry):
        registry = request_or_registry.registry
    else:
        registry = request_or_registry
    return registry.queryUtility(IWhoAPIFactoryRegistry)

def who_api_factory(request, name):
    return get_who_api_factory_registry(request).lookup(name)

def list_who_api_factory(request):
    return list(get_who_api_factory_registry(request))

def who_api(request, api_name=None):
    cache = request.environ.get('altair.auth.who_api_cache')
    if cache is None:
        request.environ['altair.auth.who_api_cache'] = cache = {}
    if api_name is None:
        api_name = decide(request)
    if api_name is None:
        raise ValueError('could not determine Who API')
    api = cache.get(api_name)
    if api is None:
        identifier = request.registry.queryUtility(IIdentifier, name='altair.auth.default_identifier')
        try:
            del request.environ['repoze.who.api']
        except KeyError:
            pass
        factory = who_api_factory(request, name=api_name)
        if factory is not None:
            api = factory(request, [('default', identifier)])
            cache[api_name] = api
    request.environ['repoze.who.api'] = api
    return api, api_name

def resolve_api_name(request, api):
    return get_who_api_factory_registry(request).reverse_lookup(api.factory)
