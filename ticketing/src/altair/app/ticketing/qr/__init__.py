# -*- coding: utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from .interfaces import IQRDataBuilder, IQRDataAESBuilder
from .builder import qr
from .builder import InvalidSignedString
from .builder import qr_aes

"""
歴史的な理由により、QRコードの署名付き文字列の作成には、同一のOrderedProductItemTokenに紐づくTicketPrintHistoryのid順で先頭のidを利用する。
"""

def get_qrdata_builder(request):
    return request.registry.getUtility(IQRDataBuilder)

def get_qrdata_aes_builder(request):
    return request.registry.getUtility(IQRDataAESBuilder)

def includeme(config):
    builder = qr()
    builder.key = u"THISISIMPORTANTSECRET"
    config.registry.registerUtility(builder, IQRDataBuilder)

    builder_aes = qr_aes()
    config.registry.registerUtility(builder_aes, IQRDataAESBuilder)
    config.add_directive("add_qr_aes_plugin", ".directives.add_qr_aes_plugin")
    config.add_directive("add_qr_aes_delivery_form_maker", ".directives.add_qr_aes_delivery_form_maker")
    config.include('.qr_aes_plugins')
