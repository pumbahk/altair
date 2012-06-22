# -*- coding:utf-8 -*-

import hashlib
import hmac
import uuid
import functools
import xml.etree.ElementTree as et

from . import interfaces
from . import models as m


class ItemXmlVisitor(object):
    """ """
    def visit_item(self, el, items_folder):
        item = m.CheckoutItem()
        items_folder.items.append(item)
        for e in el:
            if e.tag == 'itemId':
                item.itemId = e.text.strip()
            elif e.tag == 'itemName':
                item.itemName = e.text.strip()
            elif e.tag == 'itemNumbers':
                item.itemNumbers = int(e.text.strip())
            elif e.tag == 'itemFee':
                item.itemFee = int(e.text.strip())


class CartXmlVisitor(object):
    item_visitor = ItemXmlVisitor()

    def visit(self, root):

        if root.tag == 'cartConfirmationRequest':
            return self.visit_cartConfirmationRequest(root)
        else:
            return None

    def visit_cartConfirmationRequest(self, el):
        cart_confirm = m.CartConfirm()
        for e in el:
            if e.tag == 'openId':
                cart_confirm.openid = e.text.strip()
            elif e.tag == 'carts':
                self.visit_carts(e, cart_confirm)
            elif e.tag == 'isTMode':
                cart_confirm.isTMode = e.text.strip()

        return cart_confirm

    def visit_carts(self, el, cart_confirm):
        for cart_el in el:
            if cart_el.tag == 'cart':
                self.visit_cart(cart_el, cart_confirm)

    def visit_cart(self, el, cart_confirm):
        cart = m.CheckoutCart()
        cart_confirm.carts.append(cart)
        for e in el:
            if e.tag == 'cartConfirmationId':
                cart.cartConfirmationId = e.text.strip()
            elif e.tag == 'orderCartId':
                cart.orderCartId = e.text.strip()
            elif e.tag == 'orderItemsTotalFee':
                cart.orderItemsTotalFee = int(e.text.strip())
            elif e.tag == 'items':
                self.visit_items(e, cart)

    def visit_items(self, el, cart):
        for item_el in el:
            if item_el.tag == 'item':
                self.item_visitor.visit_item(item_el, cart)


class CompletedOrderXmlVisitor(object):
    """ """

    item_visitor = ItemXmlVisitor()

    def visit(self, root):
        if root.tag == 'orderCompleteRequest':
            return self.visit_root(root)
        else:
            return None

    def visit_root(self, root):
        completedOrder = m.Checkout()
        for e in root:
            if e.tag == 'orderId':
                completedOrder.orderId = e.text.strip()
            elif e.tag == 'orderControlId':
                completedOrder.orderControlId = e.text.strip()
            elif e.tag == 'orderCartId':
                completedOrder.orderCartId = e.text.strip()
            elif e.tag == 'orderTotalFee':
                completedOrder.orderTotalFee = e.text.strip()
            elif e.tag == 'orderDate':
                completedOrder.orderDate = e.text.strip()
            elif e.tag == 'usedPoint':
                completedOrder.usedPoint = e.text.strip()
            elif e.tag == 'items':
                self.visit_items(e, completedOrder)

        return completedOrder

    def visit_items(self, el, completedOrder):
        for item_el in el:
            if item_el.tag == 'item':
                self.item_visitor.visit_item(item_el, completedOrder)


class HMAC_SHA1(object):

    def __init__(self, secret):
        self.secret = secret

    def __call__(self, checkout_xml):
        return hmac.new(self.secret, checkout_xml, hashlib.sha1).hexdigest()


class HMAC_MD5(object):

    def __init__(self, secret):
        self.secret = secret

    def __call__(self, checkout_xml):
        return hmac.new(self.secret, checkout_xml, hashlib.md5).hexdigest()


class CheckoutAPI(object):

    def __init__(self, service_id, success_url, fail_url, auth_method, is_test):
        self.service_id = service_id
        self.success_url = success_url
        self.fail_url = fail_url
        self.auth_method = auth_method
        self.is_test = is_test

    def create_checkout_xml(self, cart):
        root = et.Element(u'orderItemsInfo')

        et.SubElement(root, u'serviceId').text = self.service_id
        et.SubElement(root, u'orderCompleteUrl').text = self.success_url
        et.SubElement(root, u'orderFailedUrl').text = self.fail_url
        et.SubElement(root, u'authMethod').text = AUTH_METHOD_TYPE.get(self.auth_method)
        if self.is_test is not None:
            et.SubElement(root, u'isTMode').text = self.is_test

        # カート
        et.SubElement(root, u'orderCartId').text = str(cart.id)
        et.SubElement(root, u'orderTotalFee').text = str(int(cart.total_amount))

        # 商品
        itemsInfo = et.SubElement(root, u'itemsInfo')
        for carted_product in cart.products:
            item_el = et.SubElement(itemsInfo, 'item')
            subelement = functools.partial(et.SubElement, item_el)
            subelement('itemId').text = str(carted_product.product.id)
            subelement('itemName').text = carted_product.product.name
            subelement('itemNumbers').text = str(carted_product.quantity)
            subelement('itemFee').text = str(int(carted_product.amount))

        # 商品:システム手数料
        item_el = et.SubElement(itemsInfo, 'item')
        subelement = functools.partial(et.SubElement, item_el)
        subelement('itemId').text = 'system_fee'
        subelement('itemName').text = u'システム利用料'
        subelement('itemNumbers').text = '1'
        subelement('itemFee').text = str(int(cart.system_fee))

        # 商品:決済手数料
        item_el = et.SubElement(itemsInfo, 'item')
        subelement = functools.partial(et.SubElement, item_el)
        subelement('itemId').text = 'transaction_fee'
        subelement('itemName').text = u'決済手数料'
        subelement('itemNumbers').text = '1'
        subelement('itemFee').text = str(int(cart.transaction_fee_amount))

        # 商品:配送手数料
        item_el = et.SubElement(itemsInfo, 'item')
        subelement = functools.partial(et.SubElement, item_el)
        subelement('itemId').text = 'delivery_fee'
        subelement('itemName').text = u'配送手数料'
        subelement('itemNumbers').text = '1'
        subelement('itemFee').text = str(int(cart.delivery_fee_amount))

        return '<?xml version="1.0" encoding="UTF-8"?>' + et.tostring(root)

    def save_order_complete(self, request):
        confirmId = request.params['confirmId']
        xml = confirmId.replace(' ', '+').decode('base64')
        visitor = CompletedOrderXmlVisitor()
        completed_order = visitor.visit(et.XML(xml))
        completed_order.save()

        return RESULT_FLG_SUCCESS

def get_checkout_service(request):
    return request.registry.utilities.lookup([], interfaces.ICheckoutAPI)

def generate_requestid():
    """
    安心決済の一意なリクエストIDを生成する
    """
    return uuid.uuid4().hex[:16]  # uuidの前半16桁

def sign_to_xml(request, xml):
    signer = request.registry.utilities.lookup([], interfaces.ISigner, "HMAC")
    return signer(xml)

def confirmation_to_xml(confirmation):
    root = et.Element('cartConfirmationResponse')
    carts_el = et.SubElement(root, 'carts')

    for cart in confirmation.carts:
        cart_el = et.SubElement(carts_el, 'cart')
        subelement = functools.partial(et.SubElement, cart_el)
        subelement('cartConfirmationId').text = cart.cartConfirmationId
        subelement('orderCartId').text = cart.orderCartId
        subelement('orderItemsTotalFee').text = str(cart.orderItemsTotalFee)
        items_el = subelement('items')

        for item in cart.items:
            item_el = et.SubElement(items_el, 'item')
            isublement = functools.partial(et.SubElement, item_el)
            isublement('itemId').text = item.itemId
            isublement('itemNumbers').text = str(item.itemNumbers)
            isublement('itemFee').text = str(item.itemFee)
            isublement('itemConfirmationResult').text = item.itemConfirmationResult
            isublement('itemNumbersMessage').text = item.itemNumbersMessage
            isublement('itemFeeMessage').text = item.itemFeeMessage

    return et.tostring(root)


AUTH_METHOD_TYPE = {
    'HMAC-SHA1':'1',
    'HMAC-MD5':'2',
}

IS_NOT_TO_MODE = 0
IS_T_MODE = 1

API_STATUS_SUCCESS = 0
API_STATUS_ERROR = 1


ITEM_SETTLEMENT_RESULT_NOT_REQUIRED = 0
ITEM_SETTLEMENT_RESULT_REQUIRED = 1

RESULT_OK = 0
RESULT_ERROR = 1


PAYMENT_STATUS_YET = 0
PAYMENT_STATUS_PROGRESS = 1
PAYMENT_STATUS_COMPLETED = 2

PROCCES_STATUE_PROGRESS = 0
PROCCES_STATUE_COMPLETED = 1

RESULT_FLG_SUCCESS = 0
RESULT_FLG_FAILED = 1


ERROR_CODES = {
    "100": u"メンテナンス中",
    "200": u"システムエラー",
    "300": u"入力値のフォーマットエラー",
    "400": u"サービス ID、アクセスキーのエラー",
    "500": u"リクエスト ID 重複エラー または 実在しないリクエスト ID に対するリクエストエラー",
    "600": u"XML 解析エラー",
    "700": u"全て受付エラー(成功件数が0件)",
    "800": u"最大処理件数エラー(リクエストの処理依頼件数超過)",
}

ORDER_ERROR_CODES = {
    "10", u"設定された注文管理番号が存在しない",
    "11", u"設定された注文管理番号が不正",
    "20", u"􏰀済ステータスが不正",
    "30", u"締め日チェックエラー",
    "40", u"商品 ID が不一致",
    "41", u"商品数が不足",
    "42", u"商品個数が不正(商品個数が 501 以上)",
    "50", u"リクエストの総合計金額が不正(100 円未満)",
    "51", u"リクエストの総合計金額が不正(合計金額が 0 円)",
    "52", u"リクエストの総合計金額が不正(合計金額が 9 桁以上)",
    "60", u"別処理を既に受付(当該データが受付済みで処理待ち)",
    "90", u"システムエラー",
}

ITEM_CONFIRMATION_RESULTS = {
    "0": u"個数・商品単価共に変更なし",
    "1": u"個数変更あり",
    "2": u"商品単価変更あり",
    "3": u"個数・商品単価共に変更あり",
}
