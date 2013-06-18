# -*- coding:utf-8 -*-

from zope.interface import Interface


class IElecting(Interface):

    def elect_lot_entries():
        """抽選申し込み確定 
        """
