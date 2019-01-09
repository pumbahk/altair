# -*- coding: utf-8 -*-
from pyramid.interfaces import IRequest
from .interfaces import ICommunicator


def get_communicator(request_or_registry, name):
    if IRequest.providedBy(request_or_registry):
        registry = request_or_registry.registry
    else:
        registry = request_or_registry
    return registry.queryUtility(ICommunicator, name=name)
