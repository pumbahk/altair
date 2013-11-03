# -*- coding:utf-8 -*-

"""
"""

from zope.interface import Interface, Attribute

class IGetCart(Interface):
    def __call__(request):
        """ get IPaymentCart impl from request """


class IPaymentCart(Interface):
    performance   = Attribute(u"")
    sales_segment = Attribute(u"")
    payment_delivery_pair = Attribute(u"")
    order_no      = Attribute(u"")
    total_amount  = Attribute(u"")
    system_fee    = Attribute(u"")
    delivery_fee  = Attribute(u"")
    transaction_fee  = Attribute(u"")
    shipping_address = Attribute(u"")
    channel       = Attribute(u"")
    name          = Attribute(u"")
    has_different_amount = Attribute(u"")
    different_amount     = Attribute(u"")
    operator      = Attribute(u"")
    order         = Attribute(u"")
    products      = Attribute(u"")

    def finish(self):
        """ finish cart lifecycle"""


class IPaymentCartedProduct(Interface):
    price    = Attribute(u"")
    quantity = Attribute(u"")
    product  = Attribute(u"")
    items    = Attribute(u"")
    cart     = Attribute(u"")


class IPaymentCartedProductItem(Interface):
    price          = Attribute(u"")
    quantity       = Attribute(u"")
    seats          = Attribute(u"")
    product_item   = Attribute(u"")
    carted_product = Attribute(u"")


class IPaymentShippingAddress(Interface):
    user_id         = Attribute(u"")
    tel_1           = Attribute(u"")
    tel_2           = Attribute(u"")
    first_name      = Attribute(u"")
    last_name       = Attribute(u"")
    first_name_kana = Attribute(u"")
    last_name_kana  = Attribute(u"")
    zip             = Attribute(u"")
    email_1         = Attribute(u"")
    email           = Attribute(u"")


class IPaymentPreparer(Interface):
    def prepare(request, cart):
        """ 決済処理の前処理を行う
        """

class IPaymentPreparerFactory(Interface):
    def __call__(request, payment_delivery_pair):
        """ 決済・引取方法に対応する前処理を取得する
        """

class IDeliveryPlugin(Interface):
    """ 配送処理プラグイン """
    def prepare(request, cart):
        """ 前処理 """

    def finish(request, cart):
        """ 確定処理 """

    def finished(request, order):
        """ 確定済みか判定する"""

    def cancel(request, order):
        pass

class IPaymentPlugin(Interface, IPaymentPreparer):
    """ 決済プラグイン"""
    def prepare(request, cart):
        """ 前処理 """

    def finish(request, cart):
        """ 確定処理 """

    def finished(request, order):
        """ 確定済みか判定する"""

    def cancel(request, order):
        pass

class IPaymentDeliveryPlugin(Interface):
    """ 決済配送を一度に行うプラグイン"""
    def prepare(request, cart):
        """ 前処理 """

    def finish(request, cart):
        """ 確定処理 """

class IOrderPayment(Interface):
    """ 完了画面の決済ビューレットのコンテキスト"""
    order = Attribute(u"注文内容")

class IOrderDelivery(Interface):
    """ 完了画面の配送ビューレットのコンテキスト"""
    order = Attribute(u"注文内容")


class IDeliveryErrorEvent(Interface):
    exception = Attribute(u"error")
    request = Attribute(u"request")
    order = Attribute(u"order caused error")

class IPaymentViewRendererLookup(Interface):
    def __call__(path_or_renderer_name, info, for_, plugin_type, plugin_id, **kwargs):
        pass
