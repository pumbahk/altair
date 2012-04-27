# -*- coding: utf-8 -*-
# ASP 管理系
def includeme(config):
    config.add_route('admin.index'            , '/')
    config.add_route('admin.organization'     , '/organization')
    config.add_route('admin.super'            , '/super')
