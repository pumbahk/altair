# -*- coding:utf-8 -*-
from pyramid.interfaces import IRequest
from altair.app.ticketing import newRootFactory
from .resources import CooperationEventResource

def includeme(config):
    # 全体
    factory = newRootFactory(CooperationEventResource)
    config.add_route('cooperation.index', '/{event_id}', factory=factory)
    # 返券処理
    config.add_route('cooperation.putback', '/{event_id}/putback', factory=factory)
