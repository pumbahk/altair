# -*- coding: utf-8 -*-

RAKUTEN_OPEN_ID_REGEXP = u'^https:\/\/myid.rakuten.co.jp\/openid\/user\/.*'


def includeme(config):
    config.scan(".")
