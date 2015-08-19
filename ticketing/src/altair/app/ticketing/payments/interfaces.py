# -*- coding:utf-8 -*-

"""
"""

from zope.interface import Interface, Attribute
from altair.app.ticketing.core.interfaces import (
    IOrderLike,
    IOrderedProductLike,
    IOrderedProductItemLike,
    IShippingAddress
    )

class ICartInterface(Interface):
    def get_cart(request, retrieve_invalidated=False):
        """ get IPaymentCart impl from request """

    def get_cart_by_order_no(request, order_no, retrieve_invalidated=False):
        """ get IPaymentCart impl from request """

    def get_success_url(request):
        """ get success url """

    def make_order_from_cart(request, cart):
        pass

    def cont_complete_view(context, request, order_no, magazine_ids):
        pass


class IPaymentCart(IOrderLike):
    performance           = Attribute(u"")
    name                  = Attribute(u"")
    order                 = Attribute(u"")
    order_no              = Attribute(u"")

    def finish():
        """ finish cart lifecycle"""

class IOrderRefundRecord(Interface):
    refund = Attribute(u"")
    refund_total_amount = Attribute(u"")
    refund_system_fee = Attribute(u"")
    refund_transaction_fee = Attribute(u"")
    refund_delivery_fee = Attribute(u"")
    refund_special_fee = Attribute(u"")
    refund_per_order_fee = Attribute(u"")
    refund_per_ticket_fee = Attribute(u"")

    def get_refund_ticket_price(product_item_id):
        pass

    def get_item_refund_record(item):
        pass

class IItemRefundRecord(Interface):
    refund_price = Attribute(u"")

    def get_element_refund_record(element):
        return element

class IElementRefundRecord(Interface):
    refund_price = Attribute(u"")

class IPaymentOrder(IOrderLike):
    performance = Attribute(u"tentative")

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
    def validate_order(request, order_like, update=False):
        """ バリデーション """

    def prepare(request, cart):
        """ 前処理 """

    def finish(request, cart):
        """ 確定処理 """

    def finish2(request, order):
        """ 確定処理 (先にOrderを作る場合) """

    def finished(request, order):
        """ 確定済みか判定する"""

    def cancel(request, order):
        """ キャンセル """

    def refresh(request, order):
        """ 内容変更 """

    def refund(request, order, refund_record):
        """ 払戻 """

    def get_order_info(request, order):
        pass

class IPaymentPlugin(Interface, IPaymentPreparer):
    """ 決済プラグイン"""
    def validate_order(request, order_like, update=False):
        """ バリデーション """

    def prepare(request, cart):
        """ 前処理 """

    def finish(request, cart):
        """ 確定処理 """

    def finish2(request, order):
        """ 確定処理 (先にOrderを作る場合) """

    def sales(request, cart):
        """ 売上確定処理 """

    def finished(request, order):
        """ *売上*確定済みか判定する (メソッド名がミスリードなのは歴史的経緯) """

    def cancel(request, order):
        """ キャンセル """

    def refresh(request, order):
        """ 注文金額変更 """

    def refund(request, order, refund_record):
        """ 払戻 """

    def get_order_info(request, order):
        pass

class IPaymentDeliveryPlugin(Interface):
    """ 決済配送を一度に行うプラグイン"""
    def validate_order(request, order_like, update=False):
        """ バリデーション """

    def prepare(request, cart):
        """ 前処理 """

    def finish(request, cart):
        """ 確定処理 """

    def finish2(request, order):
        """ 確定処理 (先にOrderを作る場合) """

    def refresh(request, order):
        """ 内容変更 """

    def refund(request, order, refund_record):
        """ 払戻 """

    def get_order_info(request, order):
        pass

class IOrderPayment(Interface):
    """ 完了画面の決済ビューレットのコンテキスト"""
    order = Attribute(u"注文内容")

class IOrderDelivery(Interface):
    """ 完了画面の配送ビューレットのコンテキスト"""
    order = Attribute(u"注文内容")

class IPayment(Interface):
    def call_prepare(self):
        pass

    def call_delegator(self):
        pass

    def call_validate(self):
        pass

    def call_payment(self):
        pass

    def call_delivery(self, order):
        pass

class IPaymentViewRendererLookup(Interface):
    def __call__(request, path_or_renderer_name, for_, plugin_type, plugin_id, package, registry, **kwargs):
        pass

class ISejDeliveryPlugin(Interface):
    def template_record_for_ticket_format(request, ticket_format):
        pass
