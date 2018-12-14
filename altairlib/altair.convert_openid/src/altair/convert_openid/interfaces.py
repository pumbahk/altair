# -*- coding:utf-8 -*-
from zope.interface import Interface, Attribute


class IOpenIDConverterFactory(Interface):
    """
    OpenID -> EasyID転換API用クライアントクラスです。
    """
    def get_easyid(self, openid):
        pass
