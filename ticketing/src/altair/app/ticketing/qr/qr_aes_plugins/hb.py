# -*- coding:utf-8 -*-

import logging

from zope.interface import implementer

from altair.app.ticketing.qr.interfaces import IQRAESPlugin

from .ht import HTQRAESPlugin

logger = logging.getLogger(__name__)

# HBは国際版のハウステンボス（HT）なので、QRのロジックはHTの内容と同じだが、
# QRのテンプレートについて、HBの場合はスマホも表示するテンプレートのみ使う
# そのため、HBQRAESPluginはHTQRAESPluginを継承して`output_to_template`のみ実装します。

def includeme(config):
    config.add_qr_aes_plugin(HBQRAESPlugin(), u"HB")

@implementer(IQRAESPlugin)
class HBQRAESPlugin(HTQRAESPlugin):
    def __init__(self, key=None):
        super(HBQRAESPlugin, self).__init__(key)

    def output_to_template(self, ticket):

        return dict(
            order=ticket.order,
            ticket=ticket,
            performance=ticket.performance,
            event=ticket.event,
            product=ticket.product
        )
