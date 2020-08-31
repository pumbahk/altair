# -*- coding:utf-8 -*-

def includeme(config):
    config.add_route("performances.rakuten_tv_setting.index", "/events/performances/rakuten_tv_setting/index/{performance_id}", factory=".resources.RakutenTvSettingResource")
    config.scan(".")
