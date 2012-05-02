# -*- coding:utf-8 -*-

import xml.etree.ElementTree as et
import uuid
import functools
from .interfaces import ISigner
from . import models as m


def generate_requestid():
    """
    安心決済の一意なリクエストIDを生成する
    """

    # uuidの前半16桁
    return uuid.uuid4().hex[:16]

def get_cart_confirm(request):
    confirmId = request.params('confirmId').decode('base64')

    tree = et.XML(confirmId)

    cart_xml_visitor = CartXmlVisitor()
    cartInformation = cart_xml_visitor.visit(tree)
    return cartInformation

class CartXmlVisitor(object):
    def __init__(self):
        pass

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
        cart = m.Cart()
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
                self.visit_item(item_el, cart)

    def visit_item(self, el, cart):
        item = m.CheckoutItem()
        cart.items.append(item)
        for e in el:
            if e.tag == 'itemId':
                item.itemId = e.text.strip()
            elif e.tag == 'itemName':
                item.itemName = e.text.strip()
            elif e.tag == 'itemNumbers':
                item.itemNumbers = int(e.text.strip())
            elif e.tag == 'itemFee':
                item.itemFee = int(e.text.strip())



def sign_to_xml(request, xml):
    signer = request.registry.utilities.lookup(ISigner, [], "")
    return signer(xml)

def checkout_to_xml(checkout):
    root = et.Element(u'orderItemsInfo')

    et.SubElement(root, u'serviceId').text = checkout.serviceId
    itemsInfo = et.SubElement(root, u'itemsInfo')

    for item in checkout.itemsInfo:
        item_el = et.SubElement(itemsInfo, 'item')
        subelement = functools.partial(et.SubElement, item_el)
        subelement('itemId').text = item.itemId
        subelement('itemName').text = item.itemName
        subelement('itemNumbers').text = str(item.itemNumbers)
        subelement('itemFee').text = str(item.itemFee)

    et.SubElement(root, u'orderCartId').text = checkout.orderCartId
    et.SubElement(root, u'orderCompleteUrl').text = checkout.orderCompleteUrl

    if checkout.orderFailedUrl is not None:
        et.SubElement(root, u'orderFailedUrl').text = checkout.orderFailedUrl

    et.SubElement(root, u'authMethod').text = checkout.authMethod

    if checkout.isTMode is not None:
        et.SubElement(root, u'isTMode').text = checkout.isTMode

    return et.tostring(root)

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

class HMAC_SHA1(object):
    hash_algorithm = "SHA1"
    def __init__(self, secret):
        self.secret = secret

    def __call__(self, checkout_xml):
        hashed = hashlib.sha1(checkout_xml).digest()
        return hmac.new(self.secret).update(hashed).hexdigest()

class HMAC_MD5(object):
    hash_algorithm = "MD5"

    def __init__(self, secret):
        self.secret = secret

    def __call__(self, checkout_xml):
        hashed = hashlib.md5(checkout_xml).digest()
        return hmac.new(self.secret).update(hashed).hexdigest()


AUTH_METHOD_HMAC_SHA1 = 1
AUTH_METHOD_HMAC_MD5 = 2

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
