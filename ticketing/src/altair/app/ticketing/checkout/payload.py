# encoding: utf-8

import logging
import hashlib
import uuid
import hmac
import urlparse
import functools
from datetime import datetime
from lxml import etree
from base64 import b64encode

logger = logging.getLogger(__name__)

AUTH_METHOD_TYPE = {
    'HMAC-SHA1':'1',
    'HMAC-MD5':'2',
    }

RESULT_FLG_SUCCESS = 0
RESULT_FLG_FAILED = 1

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

def get_signer(auth_method, secret):
    if auth_method == 'HMAC-SHA1':
        signer = HMAC_SHA1(secret)
    elif auth_method == 'HMAC-MD5':
        signer = HMAC_MD5(secret)
    else:
        raise Exception('setting(auth_method) not found')
    return signer

class AnshinCheckoutPayloadBuilder(object):
    def __init__(self, service_id, success_url, fail_url, auth_method, secret, is_test):
        self.service_id = service_id
        self.success_url = success_url
        self.fail_url = fail_url
        self.auth_method = auth_method
        self.secret = str(secret)
        self.is_test = is_test

    def _generate_requestid(self):
        """
        楽天あんしん支払いサービスの一意なリクエストIDを生成する
        """
        return uuid.uuid4().hex[:16]  # uuidの前半16桁

    def sign_to_xml(self, xml_str):
        signer = get_signer(self.auth_method, self.secret)
        return signer(xml_str)

    def create_checkout_request_xml(self, checkout_object):
        root = etree.Element('orderItemsInfo')

        etree.SubElement(root, 'serviceId').text = self.service_id
        etree.SubElement(root, 'orderCompleteUrl').text = self.success_url
        etree.SubElement(root, 'orderFailedUrl').text = self.fail_url
        etree.SubElement(root, 'authMethod').text = AUTH_METHOD_TYPE.get(self.auth_method)
        if self.is_test is not None:
            etree.SubElement(root, 'isTMode').text = self.is_test

        # カート
        etree.SubElement(root, 'orderCartId').text = unicode(checkout_object.orderCartId)
        etree.SubElement(root, 'orderTotalFee').text = unicode(checkout_object.orderTotalFee)

        # 商品
        itemsInfo = etree.SubElement(root, 'itemsInfo')
        for item in checkout_object.items:
            self._create_checkout_item_xml(
                itemsInfo,
                itemId=item.itemId,
                itemName=item.itemName,
                itemNumbers=item.itemNumbers,
                itemFee=item.itemFee
                )
        return root

    def _create_checkout_item_xml(self, parent, **kwargs):
        el = etree.SubElement(parent, 'item')
        subelement = functools.partial(etree.SubElement, el)
        subelement('itemId').text = str(kwargs.get('itemId'))
        subelement('itemNumbers').text = str(kwargs.get('itemNumbers'))
        subelement('itemFee').text = str(int(kwargs.get('itemFee')))
        if 'itemName' in kwargs:
            subelement('itemName').text = kwargs.get('itemName')

    def create_order_complete_response_xml(self, result, complete_time):
        root = etree.Element('orderCompleteResponse')
        etree.SubElement(root, 'result').text = str(result)
        etree.SubElement(root, 'completeTime').text = str(complete_time)
        return root

    def parse_order_complete_xml(self, response_factory, root):
        if root.tag != 'orderCompleteRequest':
            return None

        orderId = None
        orderControlId = None
        orderCartId = None
        orderTotalFee = None
        orderDate = None
        isTMode = None
        usedPoint = None
        openId = None
        items = []

        for e in root:
            if e.tag == 'orderId':
                orderId = unicode(e.text.strip())
            elif e.tag == 'orderControlId':
                orderControlId = unicode(e.text.strip())
            elif e.tag == 'orderCartId':
                orderCartId = e.text.strip()
            elif e.tag == 'orderTotalFee':
                orderTotalFee = e.text.strip()
            elif e.tag == 'orderDate':
                orderDate = datetime.strptime(e.text.strip(), '%Y-%m-%d %H:%M:%S')
            elif e.tag == 'isTMode':
                isTMode = e.text.strip()
            elif e.tag == 'usedPoint':
                usedPoint = e.text.strip()
            elif e.tag == 'items':
                items = [
                    self._parse_item_xml(response_factory, item_el)
                    for item_el in e
                    ]
            elif e.tag == 'openId':
                openId = unicode(e.text.strip())
        checkout = response_factory.create_checkout_object(orderCartId)
        checkout.orderCartId = orderCartId
        checkout.orderId = orderId
        checkout.orderControlId = orderControlId
        checkout.orderTotalFee = orderTotalFee
        checkout.orderDate = orderDate
        checkout.isTMode = isTMode
        checkout.usedPoint = usedPoint
        checkout.openId = openId
        checkout.items = items
        return checkout

    def _parse_item_xml(self, response_factory, item_el):
        if item_el.tag != 'item':
            raise Exception(u'unexpected element: %s' % item_el.tag)

        item = response_factory.create_checkout_item_object()
        for e in item_el:
            if e.tag == 'itemId':
                item.itemId = e.text.strip()
            elif e.tag == 'itemName':
                item.itemName = unicode(e.text.strip())
            elif e.tag == 'itemNumbers':
                item.itemNumbers = int(e.text.strip())
            elif e.tag == 'itemFee':
                item.itemFee = int(e.text.strip())
        return item

    def create_order_control_request_xml(self, checkout_object_list, request_id=None, with_items=False):
        request_id = request_id or self._generate_requestid()
        root = etree.Element('root')
        etree.SubElement(root, 'serviceId').text = self.service_id
        etree.SubElement(root, 'accessKey').text = self.secret
        etree.SubElement(root, 'requestId').text = request_id
        sub_element = etree.SubElement(root, 'orders')

        for checkout in checkout_object_list:
            el = etree.SubElement(sub_element, 'order')
            id_el = functools.partial(etree.SubElement, el)
            id_el('orderControlId').text = checkout.orderControlId

            if with_items:
                # 商品
                items = etree.SubElement(el, 'items')
                for item in checkout.items:
                    self._create_checkout_item_xml(
                        items,
                        itemId=item.itemId,
                        itemNumbers=item.itemNumbers,
                        itemFee=item.itemFee
                        )
                id_el('orderShippingFee').text = '0'
        return root

    def parse_order_control_response_xml(self, root):
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

class AnshinCheckoutHTMLFormBuilder(object):
    def __init__(self, payload_builder, channel, nonmobile_checkin_url, mobile_checkin_url):
        self.pb = payload_builder
        self.channel = channel
        self.mobile_checkin_url = mobile_checkin_url
        self.nonmobile_checkin_url = nonmobile_checkin_url

    def build_checkout_request_form(self, checkout_object):
        from altair.app.ticketing.core.models import ChannelEnum
        xml_str = etree.tostring(self.pb.create_checkout_request_xml(checkout_object), encoding='utf-8')
        # 署名作成する
        sig = self.pb.sign_to_xml(xml_str)

        if int(self.channel) == int(ChannelEnum.Mobile):
            action = self.mobile_checkin_url
            submit = u'<input type="submit" value="楽天 お支払い" />'
        else:
            action = self.nonmobile_checkin_url
            submit = ''

        return u'<form id="checkout-form" action="%(action)s" method="post" accept-charset="utf-8">' \
            '<input type="hidden" name="checkout" value="%(checkout)s" />' \
            '<input type="hidden" name="sig" value="%(sig)s" />' \
            '%(submit)s' \
            '</form>' % \
                dict(
                    action=action,
                    checkout=b64encode(xml_str),
                    sig=sig,
                    submit=submit
                    )

