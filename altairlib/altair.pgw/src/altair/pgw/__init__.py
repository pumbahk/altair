# -*- coding:utf-8 -*-
from pyramid.config import Configurator


def includeme(config):
    config.include('.communicator')
