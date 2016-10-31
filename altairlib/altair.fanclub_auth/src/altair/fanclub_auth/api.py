# -*- coding:utf-8 -*-

import logging

from pyramid.interfaces import IRequest

from .interfaces import IFanclubOAuth, IFanclubAPIFactory

logger = logging.getLogger(__name__)


def get_fanclub_oauth(request_or_registry):
    if IRequest.providedBy(request_or_registry):
        registry = request_or_registry.registry
    else:
        registry = request_or_registry
    return registry.queryUtility(IFanclubOAuth)


def get_fanclub_api_factory(request_or_registry):
    if IRequest.providedBy(request_or_registry):
        registry = request_or_registry.registry
    else:
        registry = request_or_registry
    return registry.queryUtility(IFanclubAPIFactory)
