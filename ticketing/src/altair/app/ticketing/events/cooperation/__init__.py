# -*- coding:utf-8 -*-
from pyramid.interfaces import IRequest
from altair.app.ticketing import newRootFactory
from .resources import CooperationEventResource

def includeme(config):
    #resource_factory = newRootFactory(config.maybe_dotted('.resources.LotResource'))
    # 全体
    factory = newRootFactory(CooperationEventResource)
    config.add_route('cooperation.index', '/{event_id}', factory=factory)
    # パフォーマンス連携
    config.add_route('cooperation.performances', '/{event_id}/performances')
    # 席種連携
    config.add_route('cooperation.seat_types', '/{event_id}/seat_types')
    # 追券処理
    config.add_route('cooperation.distribution', '/{event_id}/distribution')
    # 返券処理
    config.add_route('cooperation.putback', '/{event_id}/putback', factory=factory)
    # 販売実績
    config.add_route('cooperation.achievement', '/{event_id}/achievement')
