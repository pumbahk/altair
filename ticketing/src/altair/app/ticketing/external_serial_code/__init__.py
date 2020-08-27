# -*- coding:utf-8 -*-


def includeme(config):
    config.add_route('external_serial_code_settings.index', '/settings/'
                     , factory='.resources.ExternalSerialCodeSettingResource')
    config.scan(".")
