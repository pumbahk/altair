# -*- coding: utf-8 -*-
from .interfaces import ICommunicator
from pyramid.interfaces import IRequest


def get_communicator(request_or_registry, name):
    if IRequest.providedBy(request_or_registry):
        registry = request_or_registry.registry
    else:
        registry = request_or_registry
    return registry.queryUtility(ICommunicator, name=name)