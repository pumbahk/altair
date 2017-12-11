# -*- coding: utf-8 -*-
from altair.app.ticketing import newRootFactory


def includeme(config):
    from .resources import DiscountCodeSettingResource, DiscountCodeCodesResource, DiscountCodeTargetResource
    dcs_factory = newRootFactory(DiscountCodeSettingResource)
    dcc_factory = newRootFactory(DiscountCodeCodesResource)
    dct_factory = newRootFactory(DiscountCodeTargetResource)

    # クーポン・割引コード設定
    config.add_route('discount_code.settings_index', '/settings/', factory=dcs_factory)
    config.add_route('discount_code.settings_new', '/settings/new', factory=dcs_factory)
    config.add_route('discount_code.settings_edit', '/settings/edit/{setting_id}', factory=dcs_factory)
    config.add_route('discount_code.settings_delete', '/settings/delete/{setting_id}', factory=dcs_factory)
    config.add_route('discount_code.settings_target', '/settings/target/{setting_id}', factory=dcs_factory)

    # コード一覧
    config.add_route('discount_code.codes_index', '/codes/{setting_id}/', factory=dcc_factory)
    config.add_route('discount_code.codes_add', '/codes/{setting_id}/add_codes', factory=dcc_factory)
    config.add_route('discount_code.codes_delete_all', '/codes/{setting_id}/delete_all', factory=dcc_factory)
    config.add_route('discount_code.codes_csv_export', '/codes/{setting_id}/csv_export', factory=dcc_factory)

    # 適用対象
    config.add_route('discount_code.target_index', '/target/{setting_id}', factory=dct_factory)
    config.add_route('discount_code.target_confirm', '/target/{setting_id}/confirm', factory=dct_factory)
    config.add_route('discount_code.target_register', '/target/{setting_id}/register', factory=dct_factory)

    config.scan('.')
