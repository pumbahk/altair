# -*- coding:utf-8 -*-
import logging
from pyramid.httpexceptions import HTTPFound
from string import Template
from pyramid import security
from pyramid.config import Configurator

logger = logging.getLogger(__name__)

CONFIG_PREFIX = 'altair.rakuten_auth.'
IDENT_METADATA_KEY = 'altair.rakuten_auth.metadata'
AUTH_PLUGIN_NAME = 'rakuten'

def includeme(config):
    # openid設定
    settings = config.registry.settings
    config.include(".openid")
    config.include(".oauth")

    config.add_view('.views.RootView', attr="verify", route_name="rakuten_auth.verify")
    config.add_view('.views.RootView', attr="verify2", route_name="rakuten_auth.verify2")
