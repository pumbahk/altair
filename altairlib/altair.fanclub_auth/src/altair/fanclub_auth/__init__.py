# -*- coding:utf-8 -*-
import logging
from pyramid.httpexceptions import HTTPFound
from string import Template
from pyramid import security
from pyramid.config import Configurator

logger = logging.getLogger(__name__)

CONFIG_PREFIX = 'altair.fanclub_auth.'
IDENT_METADATA_KEY = 'altair.fanclub_auth.metadata'
AUTH_PLUGIN_NAME = 'pollux'

def includeme(config):
    # openid設定
    settings = config.registry.settings
    config.include(".plugin")
    config.include(".oauth")

    config.add_view('.views.RootView', attr="verify", route_name="fanclub_auth.verify")
    config.add_view('.views.RootView', attr="verify2", route_name="fanclub_auth.verify2")
