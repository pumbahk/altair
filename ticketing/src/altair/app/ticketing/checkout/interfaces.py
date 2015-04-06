# -*- coding:utf-8 -*-

from zope.interface import Interface, Attribute


class ISigner(Interface):
    hash_algorithm = Attribute(u"hash algorithm name, SHA1 or MD5")

    def __call__(checkout):
        """ 正規化XMLの署名作成する
        """


class ICheckout(Interface):
    pass


class IAnshinCheckoutCommunicator(Interface):
    def send_order_fixation_request(xml):
        pass

    def send_order_change_request(xml):
        pass

    def send_order_cancel_request(xml):
        pass


class IAnshinCheckoutPayloadResponseFactory(Interface):
    def create_checkout_object(order_cart_id):
        pass

    def create_checkout_item_object():
        pass
