# -*- coding:utf-8 -*-


def includeme(config):
    config.add_renderer('external_serial_code_csv', '.renderers.ExternalSerialCodeCSVRenderer')
    config.add_renderer('external_serial_code_sample_csv', '.renderers.ExternalSerialCodeSampleCSVRenderer')

    # シリアルコード設定
    config.add_route('external_serial_code_settings.index', '/settings/'
                     , factory='.resources.ExternalSerialCodeSettingResource')
    config.add_route('external_serial_code_settings.show', '/settings/show/{setting_id}'
                     , factory='.resources.ExternalSerialCodeSettingResource')
    config.add_route('external_serial_code_settings.edit', '/settings/edit/{setting_id}'
                     , factory='.resources.ExternalSerialCodeSettingResource')
    config.add_route('external_serial_code_settings.delete', '/settings/delete/{setting_id}'
                     , factory='.resources.ExternalSerialCodeSettingResource')

    # シリアルコード
    config.add_route('external_serial_code.index', '/code/{setting_id}'
                     , factory='.resources.ExternalSerialCodeResource')
    config.add_route('external_serial_code.delete', '/code/delete/{setting_id}/{code_id}'
                     , factory='.resources.ExternalSerialCodeResource')
    config.add_route('external_serial_code.all_delete', '/code/all_delete/{setting_id}'
                     , factory='.resources.ExternalSerialCodeResource')
    config.add_route('external_serial_code.download', '/download/{setting_id}',
                     factory='.resources.ExternalSerialCodeResource')
    config.add_route('external_serial_code.sample.download', '/sample/download',
                     factory='.resources.ExternalSerialCodeResource')
    config.add_route('external_serial_code.import', '/import/{setting_id}',
                     factory='.resources.ExternalSerialCodeResource')

    config.scan(".")
