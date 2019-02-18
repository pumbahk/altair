# -*- coding: utf-8 -*-

from zope.interface import Interface


class IFamimaBarcodeUrlGeneratorFactory(Interface):
    """Famima 電子バーコード URL 生成
    :param
        Famima reserve number
    """
    def generate(self, reserve_number):
        pass
