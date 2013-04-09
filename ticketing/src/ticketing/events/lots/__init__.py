# -*- coding:utf-8 -*-
from pyramid.interfaces import IRequest

def includeme(config):
    
    # 抽選内容管理
    config.add_route('lots.index', '/{event_id}',
                     factory=".resources.LotResource")
    config.add_route('lots.new', '/new/{event_id}',
                     factory=".resources.LotResource")
    config.add_route('lots.show', '/show/{lot_id}',
                     factory=".resources.LotResource")
    config.add_route('lots.edit', '/edit/{lot_id}',
                     factory=".resources.LotResource")

    config.add_route('lots.product_new', '/product_new/{lot_id}',
                     factory=".resources.LotResource")

    # 抽選申し込み管理
    config.add_route('lots.entries.index', 'entries/{lot_id}',
                     factory=".resources.LotResource")
    config.add_route('lots.entries.export.html', 'entries/export/{lot_id}.html',
                     factory=".resources.LotResource")
    config.add_route('lots.entries.export', 'entries/export/{lot_id}',
                     factory=".resources.LotResource")
    config.add_route('lots.entries.import', 'entries/import/{lot_id}',
                     factory=".resources.LotResource")
    config.add_route('lots.entries.elect_entry_no', 'entries/elect_entry_no/{lot_id}',
                     factory=".resources.LotResource")
    config.add_route('lots.entries.elect', 'entries/elect/{lot_id}',
                     factory=".resources.LotResource")

    # adapters
    reg = config.registry
    from .interfaces import ILotEntryStatus
    from ticketing.lots.adapters import LotEntryStatus
    from ticketing.lots.models import Lot

    reg.registerAdapter(LotEntryStatus, [Lot, IRequest], 
                        ILotEntryStatus)
