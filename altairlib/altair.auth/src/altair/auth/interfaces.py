# -*- coding:utf-8 -*-
from zope.interface import Interface, Attribute

class IWhoAPIDecider(Interface):
    def decide():
        """ 
        :return: str 利用するWho APIの名前
        """

class IWhoAPIFactoryRegistry(Interface):
    def register(name, factory):
        pass

    def __iter__(self):
        pass

    def lookup(name):
        pass

    def reverse_lookup(factory):
        pass

class IAugmentedWhoAPI(Interface):
    factory = Attribute('''''')

class IAugmentedWhoAPIFactory(Interface):
    def __call__(request, identifiers):
        pass
