# -*- coding: utf-8 -*-
from altair.app.ticketing import newRootFactory


def includeme(config):
    from .resources import DiscountCodeSettingResource
    from .resources import DiscountCodeCodesResource
    dcs_factory = newRootFactory(DiscountCodeSettingResource)
    dcc_factory = newRootFactory(DiscountCodeCodesResource)
    config.add_route('discount_code.settings_index', '/settings/', factory=dcs_factory)
    config.add_route('discount_code.settings_new', '/settings/new', factory=dcs_factory)
    config.add_route('discount_code.settings_edit', '/settings/edit/{setting_id}', factory=dcs_factory)
    config.add_route('discount_code.settings_delete', '/settings/delete/{setting_id}', factory=dcs_factory)
    config.add_route('discount_code.settings_target', '/settings/target/{setting_id}', factory=dcs_factory)
    config.add_route('discount_code.codes_index', '/codes/{setting_id}/', factory=dcc_factory)
    config.add_route('discount_code.codes_add', '/codes/{setting_id}/add_codes', factory=dcc_factory)
    config.add_route('discount_code.codes_delete_all', '/codes/{setting_id}/delete_all', factory=dcc_factory)
    config.add_route('discount_code.codes_csv_export', '/codes/{setting_id}/csv_export', factory=dcc_factory)
    config.scan('.')
