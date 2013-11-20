# -*- coding:utf-8 -*-

import hashlib
import hmac
import httplib
import urllib
import uuid
import functools
import logging
import urlparse
import xml.etree.ElementTree as et
from datetime import datetime

from pyramid.threadlocal import get_current_request

from altair.app.ticketing.core import api as core_api
from altair.app.ticketing.cart.models import Cart
from altair.app.ticketing.core.models import Order
from . import interfaces
from . import models as m

logger = logging.getLogger(__name__)

AUTH_METHOD_TYPE = {
    'HMAC-SHA1':'1',
    'HMAC-MD5':'2',
    }

RESULT_FLG_SUCCESS = 0
RESULT_FLG_FAILED = 1

ERROR_CODES = {
    "100": u"メンテナンス中",
    "200": u"システムエラー",
    "300": u"入力値のフォーマットエラー",
    "400": u"サービス ID、アクセスキーのエラー",
    "500": u"リクエスト ID 重複エラー または 実在しないリクエスト ID に対するリクエストエラー",
    "600": u"XML 解析エラー",
    "700": u"全て受付エラー(成功件数が0件)",
    "800": u"最大処理件数エラー(リクエストの処理依頼件数超過)",
    }

ORDER_ERROR_CODES = {
    "10", u"設定された注文管理番号が存在しない",
    "11", u"設定された注文管理番号が不正",
    "20", u"􏰀済ステータスが不正",
    "30", u"締め日チェックエラー",
    "40", u"商品 ID が不一致",
    "41", u"商品数が不足",
    "42", u"商品個数が不正(商品個数が 501 以上)",
    "50", u"リクエストの総合計金額が不正(100 円未満)",
    "51", u"リクエストの総合計金額が不正(合計金額が 0 円)",
    "52", u"リクエストの総合計金額が不正(合計金額が 9 桁以上)",
    "60", u"別処理を既に受付(当該データが受付済みで処理待ち)",
    "90", u"システムエラー",
    }

def generate_requestid():
    """
    楽天あんしん支払いサービスの一意なリクエストIDを生成する
    """
    return uuid.uuid4().hex[:16]  # uuidの前半16桁

def get_checkout_service(request, organization=None, channel=None):
    settings = request.registry.settings
    params = dict(
        success_url=settings.get('altair_checkout.success_url'),
        fail_url=settings.get('altair_checkout.fail_url'),
        api_url=settings.get('altair_checkout.api_url'),
        is_test=settings.get('altair_checkout.is_test', False),
        service_id=None,
        auth_method=None,
        secret=None
    )

    if organization and channel:
        shop_settings = m.RakutenCheckoutSetting.query.filter_by(
            organization_id=organization.id,
            channel=channel.v
        ).first()
        if not shop_settings:
            raise Exception('RakutenCheckoutSetting not found (organization_id=%s, channel=%s)' % (organization.id, channel.v))

        params.update(dict(
            service_id=shop_settings.service_id,
            auth_method=shop_settings.auth_method,
            secret=shop_settings.secret
        ))

    return Checkout(**params)

def sign_to_xml(request, organization, channel, xml):
    shop_settings = m.RakutenCheckoutSetting.query.filter_by(
        organization_id=organization.id,
        channel=channel.v
    ).first()
    if not shop_settings:
        raise Exception('RakutenCheckoutSetting not found (organization_id=%s, channel=%s)' % (organization.id, channel.v))

    if shop_settings.auth_method == 'HMAC-SHA1':
        signer = HMAC_SHA1(str(shop_settings.secret))
    elif shop_settings.auth_method == 'HMAC-MD5':
        signer = HMAC_MD5(str(shop_settings.secret))
    else:
        raise Exception('setting(auth_method) not found')
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
    _httplib = httplib

    def __init__(self, service_id, success_url, fail_url, auth_method, secret, api_url, is_test):
        self.service_id = service_id
        self.success_url = success_url
        self.fail_url = fail_url
        self.auth_method = auth_method
        self.secret = secret
        self.api_url = api_url
        self.is_test = is_test

    def create_checkout_request_xml(self, cart):
        request = get_current_request()
        root = et.Element('orderItemsInfo')

        et.SubElement(root, 'serviceId').text = self.service_id
        et.SubElement(root, 'orderCompleteUrl').text = 'https://%(host)s%(path)s' % dict(host=request.host, path=self.success_url)
        et.SubElement(root, 'orderFailedUrl').text = 'https://%(host)s%(path)s' % dict(host=request.host, path=self.fail_url)
        et.SubElement(root, 'authMethod').text = AUTH_METHOD_TYPE.get(self.auth_method)
        if self.is_test is not None:
            et.SubElement(root, 'isTMode').text = self.is_test

        # カート
        et.SubElement(root, 'orderCartId').text = str(cart.id)
        et.SubElement(root, 'orderTotalFee').text = str(int(cart.total_amount))

        # 商品
        itemsInfo = et.SubElement(root, 'itemsInfo')
        for carted_product in cart.items:
            self._create_checkout_item_xml(itemsInfo, **dict(
                itemId=carted_product.product.id,
                itemName=carted_product.product.name,
                itemNumbers=carted_product.quantity,
                itemFee=carted_product.product.price
            ))

        # 商品:システム利用料
        self._create_checkout_item_xml(itemsInfo, **dict(
            itemId='system_fee',
            itemName=u'システム利用料',
            itemNumbers='1',
            itemFee=str(int(cart.system_fee))
        ))

        # 商品:引取手数料
        self._create_checkout_item_xml(itemsInfo, **dict(
            itemId='delivery_fee',
            itemName=u'引取手数料',
            itemNumbers='1',
            itemFee=str(int(cart.delivery_fee))
        ))

        logger.debug(et.tostring(root))
        return et.tostring(root)

    def _create_checkout_item_xml(self, parent, **kwargs):
        el = et.SubElement(parent, 'item')
        subelement = functools.partial(et.SubElement, el)
        subelement('itemId').text = str(kwargs.get('itemId'))
        subelement('itemNumbers').text = str(kwargs.get('itemNumbers'))
        subelement('itemFee').text = str(int(kwargs.get('itemFee')))
        if 'itemName' in kwargs:
            subelement('itemName').text = kwargs.get('itemName')

    def create_order_complete_response_xml(self, result, complete_time):
        root = et.Element('orderCompleteResponse')
        et.SubElement(root, 'result').text = str(result)
        et.SubElement(root, 'completeTime').text = str(complete_time)

        return et.tostring(root)

    def save_order_complete(self, request):
        confirmId = request.params['confirmId']
        xml = confirmId.replace(' ', '+').decode('base64')
        checkout = self._parse_order_complete_xml(et.XML(xml))
        checkout.save()
        return checkout

    def _parse_order_complete_xml(self, root):
        if root.tag != 'orderCompleteRequest':
            return None

        checkout = m.Checkout()
        for e in root:
            if e.tag == 'orderId':
                checkout.orderId = unicode(e.text.strip())
            elif e.tag == 'orderControlId':
                checkout.orderControlId = unicode(e.text.strip())
            elif e.tag == 'orderCartId':
                checkout.orderCartId = e.text.strip()
            elif e.tag == 'orderTotalFee':
                checkout.orderTotalFee = e.text.strip()
            elif e.tag == 'orderDate':
                checkout.orderDate = datetime.strptime(e.text.strip(), '%Y-%m-%d %H:%M:%S')
            elif e.tag == 'isTMode':
                checkout.isTMode = e.text.strip()
            elif e.tag == 'usedPoint':
                checkout.usedPoint = e.text.strip()
            elif e.tag == 'items':
                self._parse_item_xml(e, checkout)
            elif e.tag == 'openId':
                checkout.openId = unicode(e.text.strip())
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
                    item.itemName = unicode(e.text.strip())
                elif e.tag == 'itemNumbers':
                    item.itemNumbers = int(e.text.strip())
                elif e.tag == 'itemFee':
                    item.itemFee = int(e.text.strip())

    def _request_order_control(self, url, message=None):
        content_type = "application/xhtml+xml;charset=UTF-8"
        body = message if message is not None else ''
        url_parts = urlparse.urlparse(url)

        if url_parts.scheme == "http":
            http = self._httplib.HTTPConnection(host=url_parts.hostname, port=url_parts.port)
        elif url_parts.scheme == "https":
            http = self._httplib.HTTPSConnection(host=url_parts.hostname, port=url_parts.port)
        else:
            raise ValueError, "unknown scheme %s" % (url_parts.scheme)

        logger.debug("request %s body = %s" % (url, body))
        headers = {"Content-Type": content_type}
        http.request("POST", url_parts.path, body=body, headers=headers)
        res = http.getresponse()
        try:
            logger.debug('%(url)s %(status)s %(reason)s' % dict(
                url=url,
                status=res.status,
                reason=res.reason,
            ))
            if res.status != 200:
                raise Exception, res.reason
            return et.parse(res).getroot()
        finally:
            res.close()

    def _create_order_control_request_xml(self, order_control_ids, request_id=None, with_items=False):
        request_id = request_id or generate_requestid()
        root = et.Element('root')
        et.SubElement(root, 'serviceId').text = self.service_id
        et.SubElement(root, 'accessKey').text = self.secret
        et.SubElement(root, 'requestId').text = request_id
        sub_element = et.SubElement(root, 'orders')

        for order_control_id in order_control_ids:
            el = et.SubElement(sub_element, 'order')
            id_el = functools.partial(et.SubElement, el)
            id_el('orderControlId').text = order_control_id

            if with_items:
                # 商品
                items = et.SubElement(el, 'items')
                order = Order.query.join(Cart, Order.order_no==Cart._order_no).join(Cart.checkout).filter(m.Checkout.orderControlId==order_control_id).first()
                if not order:
                    raise Exception('order (order_control_id=%s) not found' % order_control_id)
                for ordered_product in order.items:
                    self._create_checkout_item_xml(items, **dict(
                        itemId=ordered_product.product.id,
                        itemNumbers=ordered_product.quantity,
                        itemFee=ordered_product.price,
                    ))
                # 商品:システム利用料
                self._create_checkout_item_xml(items, **dict(
                    itemId='system_fee',
                    itemNumbers='1',
                    itemFee=str(int(order.system_fee)),
                ))
                # 商品:配送手数料
                self._create_checkout_item_xml(items, **dict(
                    itemId='delivery_fee',
                    itemNumbers='1',
                    itemFee=str(int(order.delivery_fee)),
                ))
                id_el('orderShippingFee').text = '0'

        logger.debug(et.tostring(root))
        return et.tostring(root)

    def _parse_order_control_response_xml(self, root):
        if root.tag != 'root':
            return None

        response = {}
        for e in root:
            if e.tag == 'orders':
                response['orders'] = []
                for sub_el in e:
                    if sub_el.tag != 'order':
                        continue
                    order = {}
                    for order_el in sub_el:
                        if order_el.tag in ['orderControlId', 'orderErrorCode']:
                            order[order_el.tag] = order_el.text.strip()
                    response['orders'].append(order)
            elif e.tag in ['statusCode', 'acceptNumber', 'successNumber', 'failedNumber', 'apiErrorCode']:
                response[e.tag] = e.text.strip()
        return response

    def request_fixation_order(self, order_control_ids):
        url = self.api_url + '/odrctla/fixationorder/1.0/'
        message = self._create_order_control_request_xml(order_control_ids)
        logger.info('checkout fixation request body = %s' % message)

        res = self._request_order_control(url, 'rparam=%s' % urllib.quote(message.encode('base64')))
        logger.info('got response %s' % et.tostring(res))
        result = self._parse_order_control_response_xml(res)

        if 'statusCode' in result and result['statusCode'] != '0':
            error_code = result['apiErrorCode'] if 'apiErrorCode' in result else ''
            logger.warn(u'楽天あんしん支払いサービスの決済確定に失敗しました (%s:%s)' % (error_code, ERROR_CODES.get(error_code)))
        return result

    def request_cancel_order(self, order_control_ids):
        url = self.api_url + '/odrctla/cancelorder/1.0/'
        message = self._create_order_control_request_xml(order_control_ids)
        logger.info('checkout cancel request body = %s' % message)

        res = self._request_order_control(url, 'rparam=%s' % urllib.quote(message.encode('base64')))
        logger.info('got response %s' % et.tostring(res))
        result = self._parse_order_control_response_xml(res)

        if 'statusCode' in result and result['statusCode'] != '0':
            error_code = result['apiErrorCode'] if 'apiErrorCode' in result else ''
            logger.warn(u'楽天あんしん支払いサービスのキャンセルに失敗しました (%s:%s)' % (error_code, ERROR_CODES.get(error_code)))
        return result

    def request_change_order(self, order_control_ids):
        url = self.api_url + '/odrctla/changepayment/1.0/'
        message = self._create_order_control_request_xml(order_control_ids, with_items=True)
        logger.info('checkout change request body = %s' % message)

        res = self._request_order_control(url, 'rparam=%s' % urllib.quote(message.encode('base64')))
        logger.info('got response %s' % et.tostring(res))
        result = self._parse_order_control_response_xml(res)

        if 'statusCode' in result and result['statusCode'] != '0':
            error_code = result['apiErrorCode'] if 'apiErrorCode' in result else ''
            logger.warn(u'あんしん決済の金額変更に失敗しました (%s:%s)' % (error_code, ERROR_CODES.get(error_code)))
        return result
