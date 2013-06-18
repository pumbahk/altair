# -*- coding:utf-8 -*-
from zope.interface import Interface

class IWHOAPIDecider(Interface):
    def decide():
        """ 
        :return: str 利用するWho APIの名前
        """
