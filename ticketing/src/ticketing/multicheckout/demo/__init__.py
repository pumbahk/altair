# -*- coding:utf-8 -*-

import logging

logger = logging.getLogger(__name__)

def includeme(config):
    config.add_route('top', '/')
    config.add_route('secure3d_result', '/secure3d_result')
    config.scan()
