# -*- coding: utf-8 -*-
from altair.app.ticketing import newRootFactory

def includeme(config):
    from .resources import DiscountCodeSettingResource
    dcs_factory = newRootFactory(DiscountCodeSettingResource)
    config.add_route('discount_code_settings.index', '/settings/', factory=dcs_factory)
    config.add_route('discount_code_settings.new', '/settings/new', factory=dcs_factory)
    config.add_route('discount_code_settings.edit', '/settings/edit/{setting_id}', factory=dcs_factory)
    config.add_route('discount_code_settings.delete', '/settings/delete/{setting_id}', factory=dcs_factory)
    config.add_route('discount_code_settings.target', '/settings/target/{setting_id}', factory=dcs_factory)
    config.scan('.')
