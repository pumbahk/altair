# -*- coding:utf-8 -*-


def includeme(config):
    config.add_route('external_serial_code_settings.index', '/settings/'
                     , factory='.resources.ExternalSerialCodeSettingResource')
    config.add_route('external_serial_code_settings.show', '/settings/show/{setting_id}'
                     , factory='.resources.ExternalSerialCodeSettingResource')
    config.add_route('external_serial_code_settings.edit', '/settings/edit/{setting_id}'
                     , factory='.resources.ExternalSerialCodeSettingResource')
    config.add_route('external_serial_code_settings.delete', '/settings/delete/{setting_id}'
                     , factory='.resources.ExternalSerialCodeSettingResource')
    config.scan(".")
