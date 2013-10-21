# -*- coding:utf-8 -*-
from zope.interface import Interface
from zope.interface import Attribute

class IModelDescription(Interface):
    def __call__():
        pass

class IDescriptionItem(Interface):
    name = Attribute("name")
    display_name = Attribute("display name")
    value = Attribute("name")
