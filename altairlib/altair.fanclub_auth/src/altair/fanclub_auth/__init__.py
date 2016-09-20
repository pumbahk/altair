# -*- coding:utf-8 -*-
import logging
from pyramid.httpexceptions import HTTPFound
from string import Template
from pyramid import security
from pyramid.config import Configurator

logger = logging.getLogger(__name__)

CONFIG_PREFIX = 'altair.fanclub_auth.'
IDENT_METADATA_KEY = 'altair.fanclub_auth.metadata'
AUTH_PLUGIN_NAME = 'fanclub'

def includeme(config):
    # openid設定
    settings = config.registry.settings
    config.include(".oauth")
