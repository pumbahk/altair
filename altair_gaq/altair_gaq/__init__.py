# -*- coding:utf-8 -*-
from .fanstatic_resources import bj89ers, nh

def includeme(config):
    # fanstaticよりも先
    config.add_tween(".gaq_tween_factory",
        under='pyramid_fanstatic.tween_factory')    


def gaq_tween_factory(handler, registry):
    def tween(request):
        # ドメインによってneedを変える
        # TODO: Domainモデルなど作ってそこにまとめる
        if request.host.startswith('89ers'):
            bj89ers.need()
        if request.host.startswith('secure'):
            bj89ers.need()
        if request.host.startswith('happinets'):
            nh.need()
        return handler(request)
    return tween
