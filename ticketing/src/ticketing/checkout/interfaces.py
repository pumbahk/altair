# -*- coding:utf-8 -*-

from zope.interface import Interface, Attribute


class ISigner(Interface):
    hash_algorithm = Attribute(u"hash algorithm name, SHA1 or MD5")
    def __call__(checkout):
        """ 正規化XMLの署名作成する
        """


class ICheckoutAPI(Interface):
    pass