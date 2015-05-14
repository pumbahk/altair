# -*- coding:utf-8 -*-
from zope.interface import Interface, Attribute


class ILotResource(Interface):
    lot = Attribute('''''')

    cart_setting = Attribute('''''')


class IElecting(Interface):

    def elect_lot_entries():
        """抽選申し込み確定
        """
