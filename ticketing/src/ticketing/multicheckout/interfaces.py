# -*- coding:utf-8 -*-

""" マルチ決済サービスインターフェイス定義
カード決済のみ
"""

from zope.interface import Interface, Attribute

class IReqCard(Interface):
    """
    """

class IResCard(Interface):
    """
    """
class IResCardInquiry(Interface):
    """
    """


class IMultiCheckout(Interface):

    """ サービスゲートウェイ

    カードサービス

    - カード有効性チェック
    - オーソリ
    - オーソリ取消
    - 売上
    - 売上取消
    - 取引照会

    コンビニサービス

    - 収納依頼
    - 収納取消
    - 取引照会

    Pay-easyサービス

    - 収納依頼
    - 取引照会

    電子マネー

    - 決済依頼
    - 入金取消
    - 取引照会

    """


    def card_check():
        """
        """
    def card_auth():
        """
        """
    def card_authcan():
        """
        """
    def card_sales():
        """
        """
    def card_salescan():
        """
        """

