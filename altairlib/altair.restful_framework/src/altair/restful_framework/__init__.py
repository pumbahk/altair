# -*- coding: utf-8 -*-
from .settings import reload_api_settings

def includeme(config):
    reload_api_settings(config.registry.settings)
