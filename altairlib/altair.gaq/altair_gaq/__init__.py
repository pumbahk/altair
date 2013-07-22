# -*- coding:utf-8 -*-
from .fanstatic_resources import bj89ers, nh, nh_dev

def includeme(config):
    # fanstaticよりも先
    config.add_tween(".gaq_tween_factory",
        under='pyramid_fanstatic.tween_factory')    


def gaq_tween_factory(handler, registry):
    def tween(request):
        ua = getattr(request, '_ua', None)
        if ua is None or ua.is_nonmobile():
            # ドメインによってneedを変える
            # TODO: Domainモデルなど作ってそこにまとめる
            if request.host == 'happinets.dev.ticketstar.jp':
                nh_dev.need()
            elif request.host.startswith('89ers'):
                bj89ers.need()
            elif request.host.startswith('secure'):
                bj89ers.need()
            elif request.host.startswith('happinets'):
                nh.need()
        return handler(request)
    return tween
