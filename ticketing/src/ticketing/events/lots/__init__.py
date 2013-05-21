# -*- coding:utf-8 -*-
from pyramid.interfaces import IRequest

from ticketing import newRootFactory

def includeme(config):
    lot_resource_factory = newRootFactory(config.maybe_dotted('.resources.LotResource'))

    
    # 抽選内容管理
    config.add_route('lots.index', '/{event_id}',
                     factory=lot_resource_factory)
    config.add_route('lots.new', '/new/{event_id}',
                     factory=lot_resource_factory)
    config.add_route('lots.show', '/show/{lot_id}',
                     factory=lot_resource_factory)
    config.add_route('lots.edit', '/edit/{lot_id}',
                     factory=lot_resource_factory)

    # 抽選商品
    config.add_route('lots.product_new', '/product_new/{lot_id}',
                     factory=lot_resource_factory)
    config.add_route('lots.product_edit', '/products_edit/{product_id}',
                     factory=lot_resource_factory)

    # 抽選申し込み管理
    config.add_route('lots.entries.index', 'entries/{lot_id}',
                     factory=lot_resource_factory)
    config.add_route('lots.entries.search', 'entries/search/{lot_id}',
                     factory=lot_resource_factory)
    config.add_route('lots.entries.export.html', 'entries/export/{lot_id}.html',
                     factory=lot_resource_factory)
    config.add_route('lots.entries.export', 'entries/export/{lot_id}',
                     factory=lot_resource_factory)
    config.add_route('lots.entries.import', 'entries/import/{lot_id}',
                     factory=lot_resource_factory)
    config.add_route('lots.entries.elect_entry_no', 'entries/elect_entry_no/{lot_id}',
                     factory=lot_resource_factory)
    config.add_route('lots.entries.reject_entry_no', 'entries/reject_entry_no/{lot_id}',
                     factory=lot_resource_factory)
    config.add_route('lots.entries.elect', 'entries/elect/{lot_id}',
                     factory=lot_resource_factory)
    config.add_route('lots.entries.reject', 'entries/reject/{lot_id}',
                     factory=lot_resource_factory)
    config.add_route('lots.entries.cancel', 'entries/cancel/{lot_id}',
                     factory=lot_resource_factory)
    config.add_route('lots.entries.cancel_electing', 'entries/cancel_electing/{lot_id}',
                     factory=lot_resource_factory)
    config.add_route('lots.entries.cancel_rejecting', 'entries/cancel_rejecting/{lot_id}',
                     factory=lot_resource_factory)

    # adapters
    reg = config.registry
    settings = reg.settings
    from .interfaces import ILotEntryStatus
    from ticketing.lots.adapters import LotEntryStatus
    from ticketing.lots.models import Lot
    from ticketing.lots.electing import Electing
    from ticketing.lots.interfaces import IElecting
    from altair.mq.interfaces import IPublisher
    from altair.mq.publisher import Publisher

    reg.registerAdapter(LotEntryStatus, [Lot, IRequest], 
                        ILotEntryStatus)
    reg.registerAdapter(Electing, [Lot, IRequest],
                        IElecting)
    reg.registerUtility(Publisher(settings.get('altair.ticketing.lots.mq.url',
                                               'amqp://guest:guest@localhost:5672/%2F')),
                        IPublisher)
    config.include("ticketing.lots.sendmail")
    config.scan('ticketing.lots.subscribers')
