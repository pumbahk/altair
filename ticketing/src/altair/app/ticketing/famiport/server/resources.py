# -*- coding: utf-8 -*-
from pyramid.traversal import DefaultRootFactory


def famiport_resource_factory(request):
    """Famiポート用のリソースを返す"""
    return DefaultRootFactory(request)
