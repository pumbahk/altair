# -*- coding:utf-8 -*-
from pyramid.interfaces import IRequest

from altair.app.ticketing import newRootFactory

def includeme(config):
    lot_collection_resource_factory = newRootFactory(config.maybe_dotted('.resources.LotCollectionResource'))
    lot_resource_factory = newRootFactory(config.maybe_dotted('.resources.LotResource'))
    lot_product_resource_factory = newRootFactory(config.maybe_dotted('.resources.LotProductResource'))
    lot_entry_resource_factory = newRootFactory(config.maybe_dotted('.resources.LotEntryResource'))
    lot_report_setting_resource_factory = newRootFactory(config.maybe_dotted('.resources.LotEntryReportSettingResource'))

    # 抽選内容管理
    config.add_route('lots.index', '/{event_id}',
                     factory=lot_collection_resource_factory)
    config.add_route('lots.new', '/new/{event_id}',
                     factory=lot_collection_resource_factory)
    config.add_route('lots.show', '/show/{lot_id}',
                     factory=lot_resource_factory)
    config.add_route('lots.edit', '/edit/{lot_id}',
                     factory=lot_resource_factory)

    # 抽選商品
    config.add_route('lots.product_new', '/product_new/{lot_id}',
                     factory=lot_resource_factory)
    config.add_route('lots.product_edit', '/products_edit/{product_id}',
                     factory=lot_product_resource_factory)

    # 抽選申し込み管理
    config.add_route('lots.entries.search', 'entries/search/{lot_id}',
                     factory=lot_resource_factory)
    config.add_route('lots.entries.show', 'entries/search/{lot_id}/entry/{entry_no}',
                     factory=lot_entry_resource_factory)
    config.add_route('lots.entries.shipping_address.edit', 'entries/search/{lot_id}/entry/{entry_no}/shipping_address/edit',
                     factory=lot_entry_resource_factory)
    config.add_route('lots.entries.delete', 'entries/delete/{lot_id}/entry/{entry_no}',
                     factory=lot_entry_resource_factory)
    config.add_route('lots.entries.export.html', 'entries/export/{lot_id}.html',
                     factory=lot_resource_factory)
    config.add_route('lots.entries.export', 'entries/export/{lot_id}',
                     factory=lot_resource_factory)
    config.add_route('lots.entries.import', 'entries/import/{lot_id}',
                     factory=lot_resource_factory)
    config.add_route('lots.entries.elect_entry_no', 'entries/elect_entry_no/{lot_id}',
                     factory=lot_resource_factory)
    config.add_route('lots.entries.elect_all', 'entries/elect_all/{lot_id}',
                     factory=lot_resource_factory)
    config.add_route('lots.entries.reject_remains', 'entries/reject_remains/{lot_id}',
                     factory=lot_resource_factory)
    config.add_route('lots.entries.reject_entry_no', 'entries/reject_entry_no/{lot_id}',
                     factory=lot_resource_factory)
    config.add_route('lots.entries.close', 'entries/close/{lot_id}',
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
    config.add_route('lots.entries.index', 'entries/{lot_id}',
                     factory=lot_resource_factory)

    # レポートメール設定
    config.add_route('lot.entries.new_report_setting',
                     'entries/{lot_id}/new_report',
                     factory=lot_resource_factory)
    config.add_route('lot.entries.edit_report_setting',
                     'entries/{lot_id}/edit_report/{setting_id}',
                     factory=lot_report_setting_resource_factory)
    config.add_route('lot.entries.delete_report_setting',
                     'entries/{lot_id}/delete_report/{setting_id}',
                     factory=lot_report_setting_resource_factory)
    config.add_route('lot.entries.send_report_setting',
                     'entries/{lot_id}/send_report/{setting_id}',
                     factory=lot_report_setting_resource_factory)

    config.include(".mailinfo", route_prefix="/lots/mailinfo/")
    config.include("altair.mq")
    # adapters
    reg = config.registry
    settings = reg.settings
    from .interfaces import ILotEntryStatus
    from altair.app.ticketing.lots.adapters import LotEntryStatus
    from altair.app.ticketing.lots.models import Lot
    from altair.app.ticketing.lots.electing import Electing
    from altair.app.ticketing.lots.interfaces import IElecting

    reg.registerAdapter(LotEntryStatus, [Lot, IRequest],
                        ILotEntryStatus)
    reg.registerAdapter(Electing, [Lot, IRequest],
                        IElecting)
    config.include("altair.app.ticketing.lots")
