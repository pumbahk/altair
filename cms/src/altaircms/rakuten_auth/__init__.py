# -*- coding:utf-8 -*-


from .interfaces import IRakutenOpenID

def includeme(config):
    # openid設定
    reg = config.registry
    reg.adapters.register()
