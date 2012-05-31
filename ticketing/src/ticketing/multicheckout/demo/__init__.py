# -*- coding:utf-8 -*-

""" TBA
"""
import logging

logger = logging.getLogger(__name__)
def includeme(config):
    config.add_route('top', '/')
    config.scan()
