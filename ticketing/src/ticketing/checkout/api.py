# -*- coding:utf-8 -*-

import hashlib
import hmac
import uuid
import functools
import xml.etree.ElementTree as et

from . import interfaces
from . import models as m


def generate_requestid():
    """
    安心決済の一意なリクエストIDを生成する
    """
    return uuid.uuid4().hex[:16]  # uuidの前半16桁

def get_checkout_service(request):
    return request.registry.utilities.lookup([], interfaces.ICheckout)


def sign_to_xml(request, xml):
    signer = request.registry.utilities.lookup([], interfaces.ISigner, "HMAC")
    return signer(xml)


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


class Checkout(object):

    def __init__(self, service_id, success_url, fail_url, auth_method, is_test):
        self.service_id = service_id
        self.success_url = success_url
        self.fail_url = fail_url
        self.auth_method = auth_method
        self.is_test = is_test

    def create_checkout_request_xml(self, cart):
        root = et.Element('orderItemsInfo')

        et.SubElement(root, 'serviceId').text = self.service_id
        et.SubElement(root, 'orderCompleteUrl').text = self.success_url
        et.SubElement(root, 'orderFailedUrl').text = self.fail_url
        et.SubElement(root, 'authMethod').text = AUTH_METHOD_TYPE.get(self.auth_method)
        if self.is_test is not None:
            et.SubElement(root, 'isTMode').text = self.is_test

        # カート
        et.SubElement(root, 'orderCartId').text = str(cart.id)
        et.SubElement(root, 'orderTotalFee').text = str(int(cart.total_amount))

        # 商品
        itemsInfo = et.SubElement(root, 'itemsInfo')
        for carted_product in cart.products:
            self._create_checkout_item_xml(itemsInfo, **dict(
                itemId=carted_product.product.id,
                itemName=carted_product.product.name,
                itemNumbers=carted_product.quantity,
                itemFee=carted_product.amount
            ))

        # 商品:システム手数料
        self._create_checkout_item_xml(itemsInfo, **dict(
            itemId='system_fee',
            itemName=u'システム利用料',
            itemNumbers='1',
            itemFee=str(int(cart.system_fee))
        ))

        # 商品:決済手数料
        self._create_checkout_item_xml(itemsInfo, **dict(
            itemId='transaction_fee',
            itemName=u'決済手数料',
            itemNumbers='1',
            itemFee=str(int(cart.transaction_fee))
        ))

        # 商品:配送手数料
        self._create_checkout_item_xml(itemsInfo, **dict(
            itemId='delivery_fee',
            itemName=u'配送手数料',
            itemNumbers='1',
            itemFee=str(int(cart.delivery_fee))
        ))

        return et.tostring(root)

    def create_order_complete_response_xml(self, result, complete_time):
        root = et.Element('orderCompleteResponse')
        et.SubElement(root, 'result').text = str(result)
        et.SubElement(root, 'completeTime').text = str(complete_time)

        return et.tostring(root)

    def _create_checkout_item_xml(self, parent, **kwargs):
        el = et.SubElement(parent, 'item')
        subelement = functools.partial(et.SubElement, el)
        subelement('itemId').text = str(kwargs.get('itemId'))
        subelement('itemNumbers').text = str(kwargs.get('itemNumbers'))
        subelement('itemFee').text = str(int(kwargs.get('itemFee')))
        subelement('itemName').text = kwargs.get('itemName')

    def save_order_complete(self, request):
        confirmId = request.params['confirmId']
        xml = confirmId.replace(' ', '+').decode('base64')
        checkout = self._parse_order_complete_xml(et.XML(xml))

        # セッションタイムアウトで確保在庫が解放されてないかチェックする
        # ToDo
        # if validate:
        #     return RESULT_FLG_FAILED

        checkout.save()
        return RESULT_FLG_SUCCESS

    def _parse_order_complete_xml(self, root):
        if root.tag != 'orderCompleteRequest':
            return None

        checkout = m.Checkout()
        for e in root:
            if e.tag == 'orderId':
                checkout.orderId = e.text.strip()
            elif e.tag == 'orderControlId':
                checkout.orderControlId = e.text.strip()
            elif e.tag == 'orderCartId':
                checkout.orderCartId = e.text.strip()
            elif e.tag == 'orderTotalFee':
                checkout.orderTotalFee = e.text.strip()
            elif e.tag == 'orderDate':
                checkout.orderDate = e.text.strip()
            elif e.tag == 'isTMode':
                checkout.isTMode = e.text.strip()
            elif e.tag == 'usedPoint':
                checkout.usedPoint = e.text.strip()
            elif e.tag == 'items':
                self._parse_item_xml(e, checkout)
        return checkout

    def _parse_item_xml(self, element, checkout):
        for item_el in element:
            if item_el.tag != 'item':
                continue

            item = m.CheckoutItem()
            checkout.items.append(item)
            for e in item_el:
                if e.tag == 'itemId':
                    item.itemId = e.text.strip()
                elif e.tag == 'itemName':
                    item.itemName = e.text.strip()
                elif e.tag == 'itemNumbers':
                    item.itemNumbers = int(e.text.strip())
                elif e.tag == 'itemFee':
                    item.itemFee = int(e.text.strip())


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
