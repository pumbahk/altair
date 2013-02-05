# -*- coding: utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from .interfaces import IQRDataBuilder
from .builder import qr
from .builder import InvalidSignedString

"""
歴史的な理由により、QRコードの署名付き文字列の作成には、同一のOrderedProductItemTokenに紐づくTicketPrintHistoryのid順で先頭のidを利用する。
"""

def get_qrdata_builder(request):
    return request.registry.getUtility(IQRDataBuilder)

def includeme(config):
    builder = qr()
    builder.key = u"THISISIMPORTANTSECRET"
    config.registry.registerUtility(builder, IQRDataBuilder)

