# -*- coding: utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from .interfaces import IQRDataBuilder
from .builder import qr

def get_qrdata_builder(request):
    return request.registry.getUtility(IQRDataBuilder)

def includeme(config):
    builder = qr()
    builder.key = u"THISISIMPORTANTSECRET"
    config.registry.registerUtility(builder, IQRDataBuilder)

