# -*- coding:utf-8 -*-

from zope.interface import Interface
from zope.interface import Attribute

class IInternalAuthResource(Interface):
    def get_after_login_url(*args, **kwargs):
        """ arguments is same for 'pyramid.request.route_path' """

    def login_validate(form):
        pass

    organization = Attribute(u"組織")
    operator = Attribute(u"オペレーター")

    __acl__ = Attribute("__acl__")

class IInternalAuthAPIResource(Interface):
    def on_after_login(operator):
        """continuation callback of login"""
    def on_after_logout(operator):
        """continuation callback of logout"""

    def login_validate(form):
        pass

    __acl__ = Attribute("__acl__")
