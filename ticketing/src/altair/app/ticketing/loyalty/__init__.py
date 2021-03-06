# -*- coding: utf-8 -*-
from altair.app.ticketing import newRootFactory

# 楽天チケットと一緒にポイント付与したいオルグのorgのコード
orgs_with_rakuten = ['VK', 'OD']
# 楽天ペイの場合はポイント対象外にするorgのコード
orgs_not_consider_rakutenpay = ['VK']

def includeme(config):
    from .resources import PointGrantSettingAdminResource, PointGrantHistoryEntryAdminResource, PointGrantHistoryEntryImportAdminResource
    factory = newRootFactory(PointGrantSettingAdminResource)
    config.add_route('point_grant_settings.new', '/point_grant_settings/new', factory=factory)
    config.add_route('point_grant_settings.delete_confirm', '/point_grant_settings/delete/confirm', factory=factory)
    config.add_route('point_grant_settings.delete', '/point_grant_settings/delete', factory=factory)
    config.add_route('point_grant_settings.products.remove', '/point_grant_settings/{point_grant_setting_id}/products/remove', factory=factory)
    config.add_route('point_grant_settings.edit', '/point_grant_settings/{point_grant_setting_id}/edit', factory=factory)
    config.add_route('point_grant_settings.show', '/point_grant_settings/{point_grant_setting_id}', factory=factory)
    config.add_route('point_grant_settings.index', '/point_grant_settings/', factory=factory)
    config.add_subscriber('.mail.on_point_granting_failed', '.events.PointGrantingFailed')
    pghe_factory = newRootFactory(PointGrantHistoryEntryAdminResource)
    config.add_route('point_grant_history_entry.new', '/point_grant_history_entry/new', factory=pghe_factory)
    config.add_route('point_grant_history_entry.edit', '/point_grant_history_entry/edit/{point_grant_history_entry_id}', factory=pghe_factory)
    config.add_route('point_grant_history_entry.delete', '/point_grant_history_entry/delete/{point_grant_history_entry_id}', factory=pghe_factory)
    pghei_factory = newRootFactory(PointGrantHistoryEntryImportAdminResource)
    config.add_route('loyalty.point_grant_history_entry.import', '/point_grant_history_entry/import', factory=pghei_factory)
    config.scan('.')
