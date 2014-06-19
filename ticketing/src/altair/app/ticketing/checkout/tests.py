# -*- coding:utf-8 -*-

import unittest
import mock
from datetime import datetime

from pyramid import testing

import altair.app.ticketing.models
import altair.app.ticketing.core.models
from altair.app.ticketing.testing import _setup_db as _setup_db_, _teardown_db
from altair.app.ticketing.checkout import api, models, interfaces


def _setup_db(echo=False):
    return _setup_db_(
        modules=[
            'altair.app.ticketing.models',
            'altair.app.ticketing.cart.models',
            'altair.app.ticketing.users.models',
            'altair.app.ticketing.checkout.models',
            ],
        echo=echo
    )

class DummyResponseFactory(object):
    def create_checkout_object(self, orderCartId):
        return testing.DummyModel(orderCartId=orderCartId)

    def create_checkout_item_object(self):
        return testing.DummyModel()


class GetCheckoutServiceTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.session = _setup_db()

        from altair.app.ticketing.core.models import Organization, Host, ChannelEnum
        organization = Organization(id=1, name=u'organization_name', short_name=u'org')
        self.session.add(organization)

        host = models.RakutenCheckoutSetting(
            id=1,
            organization_id=1,
            service_id='this-is-serviceId',
            secret='secret',
            auth_method='HMAC-SHA1',
            channel=ChannelEnum.PC.v
        )
        self.session.add(host)

        self.session.flush()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *args, **kwargs):
        return api.get_checkout_service(*args, **kwargs)

    def test_it(self):
        from altair.app.ticketing.core.models import Organization, ChannelEnum
        request = testing.DummyRequest()
        organization = Organization.get(1)
        channel = ChannelEnum.PC

        settings = {
            u'altair_checkout.success_url': 'http://example.com/success/',
            u'altair_checkout.fail_url': 'http://example.com/fail/',
            u'altair_checkout.api_url': 'http://example.com/api/',
            u'altair_checkout.is_test': '1',
        }
        self.config.registry.settings.update(settings)
        request.config = self.config

        result = self._callFUT(request, organization, channel)
        self.assertTrue(isinstance(result, api.AnshinCheckoutAPI))
        self.assertEqual(result.pb.success_url, 'http://example.com/success/')
        self.assertEqual(result.pb.fail_url, 'http://example.com/fail/')
        self.assertEqual(result.comm.api_url, 'http://example.com/api/')
        self.assertEqual(result.pb.is_test, '1')
        self.assertEqual(result.pb.service_id, 'this-is-serviceId')
        self.assertEqual(result.pb.auth_method, 'HMAC-SHA1')
        self.assertEqual(result.pb.secret, 'secret')

class AnshinCheckoutPayloadBuilderTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _getTarget(self):
        from altair.app.ticketing.checkout.payload import AnshinCheckoutPayloadBuilder
        return AnshinCheckoutPayloadBuilder

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_sign_to_xml(self):
        target = self._makeOne('this-is-serviceId', 'success_url', 'fail_url', 'HMAC-SHA1', 'secret', '1') 
        xml = '<xml></xml>'
        self.assertEqual(target.sign_to_xml(xml), '35ca1b4753dfd6d58b0ee455dfe1ecc90620f3fa')

    def test_create_checkout_item_xml_basic(self):
        from lxml import etree
        xml = etree.fromstring('<root></root>')

        target = self._makeOne('this-is-serviceId', 'success_url', 'fail_url', 'HMAC-SHA1', 'secret', '1') 
        target._create_checkout_item_xml(
            xml, 
            itemId='this-is-itemId',
            itemName=u'なまえ',
            itemNumbers='100',
            itemFee='2112'
            )
        self.assertEqual(etree.tostring(xml),
            u'<root>'
            u'<item>'
            u'<itemId>this-is-itemId</itemId>'
            u'<itemNumbers>100</itemNumbers>'
            u'<itemFee>2112</itemFee>'
            u'<itemName>&#12394;&#12414;&#12360;</itemName>'
            u'</item>'
            u'</root>'
        )

    def test_create_checkout_item_xml_change_order(self):
        from lxml import etree
        xml = etree.fromstring('<root></root>')

        target = self._makeOne('this-is-serviceId', 'success_url', 'fail_url', 'HMAC-SHA1', 'secret', '1') 
        target._create_checkout_item_xml(
            xml,
            itemId='this-is-itemId',
            itemNumbers='100',
            itemFee='2112',
            orderShippingFee='0'
            )
        self.assertEqual(etree.tostring(xml),
            u'<root>'
            u'<item>'
            u'<itemId>this-is-itemId</itemId>'
            u'<itemNumbers>100</itemNumbers>'
            u'<itemFee>2112</itemFee>'
            u'</item>'
            u'</root>'
        )

    def test_create_checkout_request_xml_no_products(self):
        from lxml import etree
        target = self._makeOne('this-is-serviceId', 'success_url', 'fail_url', 'HMAC-SHA1', 'secret', '1') 
        checkout_object = testing.DummyModel(
            orderCartId='XX0000000000',
            orderTotalFee=1000,
            items=[]
            )
        result = target.create_checkout_request_xml(checkout_object)
        self.assertEqual(
            etree.tostring(result),
            '<orderItemsInfo>'
            '<serviceId>this-is-serviceId</serviceId>'
            '<orderCompleteUrl>success_url</orderCompleteUrl>'
            '<orderFailedUrl>fail_url</orderFailedUrl>'
            '<authMethod>1</authMethod>'
            '<isTMode>1</isTMode>'
            '<orderCartId>XX0000000000</orderCartId>'
            '<orderTotalFee>1000</orderTotalFee>'
            '<itemsInfo/>'
            '</orderItemsInfo>')

    def test_create_checkout_request_xml_with_items(self):
        from lxml import etree
        target = self._makeOne('this-is-serviceId', 'success_url', 'fail_url', 'HMAC-SHA1', 'secret', '1') 
        checkout_object = testing.DummyResource(
            orderCartId='XX0000000000',
            orderTotalFee=1000,
            items=[
                testing.DummyResource(
                    itemId='item-%02d' % i,
                    itemName='item %d' % i,
                    itemNumbers=i,
                    itemFee=20 + i * 10
                ) for i in range(2)
            ]
        )
        result = target.create_checkout_request_xml(checkout_object)

        self.assertEqual(
            etree.tostring(result),
            '<orderItemsInfo>'
            '<serviceId>this-is-serviceId</serviceId>'
            '<orderCompleteUrl>success_url</orderCompleteUrl>'
            '<orderFailedUrl>fail_url</orderFailedUrl>'
            '<authMethod>1</authMethod>'
            '<isTMode>1</isTMode>'
            '<orderCartId>XX0000000000</orderCartId>'
            '<orderTotalFee>1000</orderTotalFee>'
            '<itemsInfo>'
            '<item>'
            '<itemId>item-00</itemId>'
            '<itemNumbers>0</itemNumbers>'
            '<itemFee>20</itemFee>'
            '<itemName>item 0</itemName>'
            '</item>'
            '<item>'
            '<itemId>item-01</itemId>'
            '<itemNumbers>1</itemNumbers>'
            '<itemFee>30</itemFee>'
            '<itemName>item 1</itemName>'
            '</item>'
            '</itemsInfo>'
            '</orderItemsInfo>')

    def test_create_checkout_request_xml_without_tmode(self):
        from lxml import etree
        target = self._makeOne('this-is-serviceId', 'success_url', 'fail_url', 'HMAC-SHA1', 'secret', '0') 
        cart = testing.DummyResource(
            orderCartId='XX0000000000',
            orderTotalFee=1000,
            items=[
                testing.DummyResource(
                    itemId='item-%02d' % i,
                    itemName='item %d' % i,
                    itemFee=(20 + i*10),
                    itemNumbers=i,
                    ) for i in range(2)
                ]
            )
        result = target.create_checkout_request_xml(cart)

        self.assertEqual(
            etree.tostring(result),
            '<orderItemsInfo>'
            '<serviceId>this-is-serviceId</serviceId>'
            '<orderCompleteUrl>success_url</orderCompleteUrl>'
            '<orderFailedUrl>fail_url</orderFailedUrl>'
            '<authMethod>1</authMethod>'
            '<isTMode>0</isTMode>'
            '<orderCartId>XX0000000000</orderCartId>'
            '<orderTotalFee>1000</orderTotalFee>'
            '<itemsInfo>'
            '<item>'
            '<itemId>item-00</itemId>'
            '<itemNumbers>0</itemNumbers>'
            '<itemFee>20</itemFee>'
            '<itemName>item 0</itemName>'
            '</item>'
            '<item>'
            '<itemId>item-01</itemId>'
            '<itemNumbers>1</itemNumbers>'
            '<itemFee>30</itemFee>'
            '<itemName>item 1</itemName>'
            '</item>'
            '</itemsInfo>'
            '</orderItemsInfo>')

    def test_create_order_complete_response_xml(self):
        from lxml import etree
        target = self._makeOne('this-is-serviceId', 'success_url', 'fail_url', 'HMAC-SHA1', 'secret', '1') 
        complete_time = datetime.strptime('2012-12-12 12:12:12', '%Y-%m-%d %H:%M:%S')
        result = target.create_order_complete_response_xml(0, complete_time)

        self.assertIsNotNone(result)
        self.assertEqual(etree.tostring(result),
            '<orderCompleteResponse>'
            '<result>0</result>'
            '<completeTime>2012-12-12 12:12:12</completeTime>'
            '</orderCompleteResponse>')

    def test__parse_order_complete_xml(self):
        from lxml import etree
        xml = etree.fromstring(
            '<orderCompleteRequest>'
            '<orderId>this-is-order-id</orderId>'
            '<orderControlId>this-is-order-control-id</orderControlId>'
            '<orderCartId>this-is-order-cart-id</orderCartId>'
            '<openId>https://example.com/openid/user/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx</openId>'
            '<isTMode>0</isTMode>'
            '<orderTotalFee>3000</orderTotalFee>'
            '<orderDate>2011-04-15 01:23:45</orderDate>'
            '<items>'
            '<item>'
            '<itemId>product1</itemId>'
            '<itemName>テスト用商品 1</itemName>'
            '<itemFee>1000</itemFee>'
            '<itemNumbers>1</itemNumbers>'
            '</item>'
            '<item>'
            '<itemId>product2</itemId>'
            '<itemName>テスト用商品 2</itemName>'
            '<itemFee>2000</itemFee>'
            '<itemNumbers>2</itemNumbers>'
            '</item>'
            '</items>'
            '</orderCompleteRequest>'
        )
        target = self._makeOne('this-is-serviceId', 'success_url', 'fail_url', 'HMAC-SHA1', 'secret', '1') 
        dummy_response_factory = DummyResponseFactory()
        checkout = target.parse_order_complete_xml(dummy_response_factory, xml)

        self.assertIsNotNone(checkout)
        self.assertEqual(checkout.orderId, 'this-is-order-id')
        self.assertEqual(checkout.orderControlId, 'this-is-order-control-id')
        self.assertEqual(checkout.orderCartId, 'this-is-order-cart-id')
        self.assertEqual(checkout.orderTotalFee, '3000')
        self.assertEqual(checkout.orderDate, datetime(2011, 4, 15, 1, 23, 45))
        self.assertEqual(checkout.isTMode, '0')
        self.assertEqual(checkout.usedPoint, None)
        self.assertEqual(len(checkout.items), 2)

    def test__parse_item_xml(self):
        from lxml import etree
        xml = etree.fromstring(
            '<items>'
            '<item>'
            '<itemId>product1</itemId>'
            '<itemName>テスト用商品 1</itemName>'
            '<itemFee>1000</itemFee>'
            '<itemNumbers>1</itemNumbers>'
            '</item>'
            '<item>'
            '<itemId>product2</itemId>'
            '<itemName>テスト用商品 2</itemName>'
            '<itemFee>2000</itemFee>'
            '<itemNumbers>2</itemNumbers>'
            '</item>'
            '</items>'
        )
        target = self._makeOne('this-is-serviceId', 'success_url', 'fail_url', 'HMAC-SHA1', 'secret', '1') 
        dummy_response_factory = DummyResponseFactory()
        items = [
            target._parse_item_xml(dummy_response_factory, item_el)
            for item_el in xml
            ]
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].itemId, 'product1')
        self.assertEqual(items[0].itemName, u'テスト用商品 1')
        self.assertEqual(items[0].itemNumbers, 1)
        self.assertEqual(items[0].itemFee, 1000)
        self.assertEqual(items[1].itemId, 'product2')
        self.assertEqual(items[1].itemName, u'テスト用商品 2')
        self.assertEqual(items[1].itemNumbers, 2)
        self.assertEqual(items[1].itemFee, 2000)

    def test__create_order_control_request_xml_no_orders(self):
        from lxml import etree
        target = self._makeOne('this-is-serviceId', 'success_url', 'fail_url', 'HMAC-SHA1', 'secret', '1') 
        orders = []
        request_id = target._generate_requestid()
        result = target.create_order_control_request_xml(orders, request_id)

        self.assertIsNotNone(result)
        self.assertEqual(
            etree.tostring(result),
            '<root>'
            '<serviceId>this-is-serviceId</serviceId>'
            '<accessKey>secret</accessKey>'
            '<requestId>%(request_id)s</requestId>'
            '<orders/>'
            '</root>' % dict(request_id=request_id)
        )

    def test__create_order_control_request_xml_with_orders(self):
        from lxml import etree
        target = self._makeOne('this-is-serviceId', 'success_url', 'fail_url', 'HMAC-SHA1', 'secret', '1') 
        request_id = target._generate_requestid()
        checkout_object_list = [
            testing.DummyResource(orderControlId='10'),
            testing.DummyResource(orderControlId='20'),
            ]
        result = target.create_order_control_request_xml(checkout_object_list, request_id)

        self.assertIsNotNone(result)
        self.assertEqual(
            etree.tostring(result),
            '<root>'
            '<serviceId>this-is-serviceId</serviceId>'
            '<accessKey>secret</accessKey>'
            '<requestId>%(request_id)s</requestId>'
            '<orders>'
            '<order>'
            '<orderControlId>10</orderControlId>'
            '</order>'
            '<order>'
            '<orderControlId>20</orderControlId>'
            '</order>'
            '</orders>'
            '</root>' % dict(request_id=request_id)
        )

    def test__create_order_control_request_xml_with_items(self):
        from lxml import etree
        target = self._makeOne('this-is-serviceId', 'success_url', 'fail_url', 'HMAC-SHA1', 'secret', '1') 
        request_id = target._generate_requestid()
        checkout_object = testing.DummyModel(
            orderCartId='testing-order-no',
            orderControlId='dc-1234567890-110415-0000022222',
            items=[
                testing.DummyModel(
                    itemId='22',
                    itemFee=140,
                    itemNumbers=1
                    )
                ]
            )
        result = target.create_order_control_request_xml([checkout_object], request_id, with_items=True)

        self.assertIsNotNone(result)
        self.assertEqual(
            etree.tostring(result),
            '<root>'
            '<serviceId>this-is-serviceId</serviceId>'
            '<accessKey>secret</accessKey>'
            '<requestId>%(request_id)s</requestId>'
            '<orders>'
            '<order>'
            '<orderControlId>dc-1234567890-110415-0000022222</orderControlId>'
            '<items>'
            '<item>'
            '<itemId>22</itemId>'
            '<itemNumbers>1</itemNumbers>'
            '<itemFee>140</itemFee>'
            '</item>'
            '</items>'
            '<orderShippingFee>0</orderShippingFee>'  # <- 移動？
            '</order>'
            '</orders>'
            '</root>' % dict(request_id=request_id)
        )

    def test__parse_order_control_response_xml(self):
        from lxml import etree
        xml = etree.fromstring(
            '<root>'
            '<statusCode>1</statusCode>'
            '<acceptNumber>2</acceptNumber>'
            '<successNumber>3</successNumber>'
            '<failedNumber>4</failedNumber>'
            '<orders>'
            '<order>'
            '<orderControlId>dc-1234567890-110415-0000022222</orderControlId>'
            '<orderErrorCode>090</orderErrorCode>'
            '</order>'
            '</orders>'
            '<apiErrorCode>100</apiErrorCode>'
            '</root>'
        )
        target = self._makeOne('this-is-serviceId', 'success_url', 'fail_url', 'HMAC-SHA1', 'secret', '1') 
        result = target.parse_order_control_response_xml(xml)

        self.assertEqual(result['statusCode'], '1')
        self.assertEqual(result['acceptNumber'], '2')
        self.assertEqual(result['successNumber'], '3')
        self.assertEqual(result['failedNumber'], '4')
        self.assertEqual(result['apiErrorCode'], '100')
        self.assertEqual(len(result['orders']), 1)
        self.assertEqual(result['orders'][0]['orderControlId'], 'dc-1234567890-110415-0000022222')
        self.assertEqual(result['orders'][0]['orderErrorCode'], '090')

class AnshinCheckoutAPITest(unittest.TestCase):
    maxDiff = 16384

    def setUp(self):
        self.config = testing.setUp()
        from .models import _session as priv_session
        priv_session.remove()
        self._session = _setup_db()
        self.session = priv_session
        self.request = testing.DummyRequest()

    def tearDown(self):
        testing.tearDown()
        self._session.remove()
        self.session.remove()
        _teardown_db()

    def create_order_test_data(self):
        from altair.app.ticketing.core.models import Product
        from altair.app.ticketing.orders.models import Order, OrderedProduct
        product = Product(
            id=22,
            price=140,
            public=1,
            display_order=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self._session.add(product)
        ordered_product = OrderedProduct(
            id=11,
            order_id=1,
            product_id=22,
            price=140,
            quantity=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self._session.add(ordered_product)
        order = Order(
            id=1,
            order_no='testing-order-no',
            branch_no=1,
            total_amount=200,
            system_fee=10,
            transaction_fee=20,
            delivery_fee=30,
            issuing_start_at=datetime(1970, 1, 1),
            issuing_end_at=datetime(1970, 1, 1),
            payment_start_at=datetime(1970, 1, 1),
            payment_due_at=datetime(1970, 1, 1),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self._session.add(order)

        from altair.app.ticketing.cart.models import Cart
        cart = Cart(
            id=111,
            order_id=1,
            _order_no=order.order_no,
        )
        self._session.add(cart)
        self._session.flush()

        from altair.app.ticketing.checkout.models import Checkout
        checkout = Checkout(id=1111, orderCartId=111, orderControlId=u'dc-1234567890-110415-0000022222')
        self.session.add(checkout)
        self.session.flush()

    def _getTarget(self):
        from .api import AnshinCheckoutAPI
        return AnshinCheckoutAPI

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _buildTarget(self, service_id='this-is-serviceId', success_url='/completed', fail_url='/failed', auth_method='HMAC-SHA1', secret='access_key', api_url='https://example.com/api_url', is_test='1', channel=None):
        from .payload import AnshinCheckoutPayloadBuilder, AnshinCheckoutHTMLFormBuilder
        from .communicator import AnshinCheckoutCommunicator
        from datetime import datetime
        from altair.app.ticketing.core.models import ChannelEnum
        if channel is None:
            channel = ChannelEnum.PC
        pb = AnshinCheckoutPayloadBuilder(
            service_id=service_id, 
            success_url=success_url,
            fail_url=fail_url,
            auth_method=auth_method,
            secret=secret,
            is_test=is_test
            )
        return self._makeOne(
            request=self.request,
            session=self.session,
            now=datetime(2014, 1, 1, 0, 0, 0),
            payload_builder=pb,
            html_form_builder=AnshinCheckoutHTMLFormBuilder(
                payload_builder=pb,
                channel=channel,
                nonmobile_checkin_url='/nonmobile',
                mobile_checkin_url='/checkin'
                ),
            communicator=AnshinCheckoutCommunicator(api_url)
            )



    def test_build_checkout_request_form_no_products(self):
        from lxml import etree
        from base64 import b64decode
        from altair.app.ticketing.core.models import SalesSegment, PaymentDeliveryMethodPair, PaymentMethod, DeliveryMethod, FeeTypeEnum
        from altair.app.ticketing.cart.models import Cart
        target = self._buildTarget()
        cart = Cart(
            id=10,
            _order_no='XX0000000000',
            sales_segment=SalesSegment(),
            payment_delivery_pair=PaymentDeliveryMethodPair(
                system_fee=80,
                delivery_fee=60,
                transaction_fee=0,
                discount=10,
                payment_method=PaymentMethod(
                    fee=0,
                    fee_type=FeeTypeEnum.Once.v[0]
                    ),
                delivery_method=DeliveryMethod(
                    fee=0,
                    fee_type=FeeTypeEnum.Once.v[0]
                    )
                ),
            items=[]
            )
        self._session.add(cart)
        self._session.flush()
        _, result = target.build_checkout_request_form(cart)
        result_n = etree.fromstring(result)
        checkout_n = result_n.find('input[@name="checkout"]')
        self.assertTrue(checkout_n is not None)
        payload = b64decode(checkout_n.get('value')).decode('utf-8')
        self.assertEqual(payload,
            u'<orderItemsInfo>'
            u'<serviceId>this-is-serviceId</serviceId>'
            u'<orderCompleteUrl>/completed</orderCompleteUrl>'
            u'<orderFailedUrl>/failed</orderFailedUrl>'
            u'<authMethod>1</authMethod>'
            u'<isTMode>1</isTMode>'
            u'<orderCartId>XX0000000000</orderCartId>'
            u'<orderTotalFee>140</orderTotalFee>'
            u'<itemsInfo>'
            u'<item>'
            u'<itemId>delivery_fee</itemId>'
            u'<itemNumbers>1</itemNumbers>'
            u'<itemFee>60</itemFee>'
            u'<itemName>引取手数料</itemName>'
            u'</item>'
            u'<item>'
            u'<itemId>system_fee</itemId>'
            u'<itemNumbers>1</itemNumbers>'
            u'<itemFee>80</itemFee>'
            u'<itemName>システム利用料</itemName>'
            u'</item>'
            u'</itemsInfo>'
            u'</orderItemsInfo>')

    def test_create_checkout_request_xml_with_items(self):
        from lxml import etree
        from altair.app.ticketing.core.models import SalesSegment, PaymentDeliveryMethodPair, PaymentMethod, DeliveryMethod, Product, FeeTypeEnum
        from altair.app.ticketing.cart.models import Cart, CartedProduct
        from decimal import Decimal
        from base64 import b64decode
        target = self._buildTarget()
        cart = Cart(
            id=10,
            _order_no='XX0000000000',
            sales_segment=SalesSegment(),
            payment_delivery_pair=PaymentDeliveryMethodPair(
                system_fee=80,
                delivery_fee=60,
                transaction_fee=0,
                discount=10,
                payment_method=PaymentMethod(
                    fee=0,
                    fee_type=FeeTypeEnum.Once.v[0]
                    ),
                delivery_method=DeliveryMethod(
                    fee=0,
                    fee_type=FeeTypeEnum.Once.v[0]
                    )
                ),
            items=[
                CartedProduct(
                    product=Product(
                        id=i,
                        name='item %d' % i,
                        price=Decimal(i*10)
                    ),
                    quantity=(i + 1)
                    ) for i in range(2)
                ]
        )
        self._session.add(cart)
        self._session.flush()
        _, result = target.build_checkout_request_form(cart)
        result_n = etree.fromstring(result)
        checkout_n = result_n.find('input[@name="checkout"]')
        self.assertTrue(checkout_n is not None)
        payload = b64decode(checkout_n.get('value')).decode('utf-8')

        self.assertEqual(payload,
            u'<orderItemsInfo>'
            u'<serviceId>this-is-serviceId</serviceId>'
            u'<orderCompleteUrl>/completed</orderCompleteUrl>'
            u'<orderFailedUrl>/failed</orderFailedUrl>'
            u'<authMethod>1</authMethod>'
            u'<isTMode>1</isTMode>'
            u'<orderCartId>XX0000000000</orderCartId>'
            u'<orderTotalFee>160</orderTotalFee>'
            u'<itemsInfo>'
            u'<item>'
            u'<itemId>0</itemId>'
            u'<itemNumbers>1</itemNumbers>'
            u'<itemFee>0</itemFee>'
            u'<itemName>item 0</itemName>'
            u'</item>'
            u'<item>'
            u'<itemId>1</itemId>'
            u'<itemNumbers>2</itemNumbers>'
            u'<itemFee>10</itemFee>'
            u'<itemName>item 1</itemName>'
            u'</item>'
            u'<item>'
            u'<itemId>delivery_fee</itemId>'
            u'<itemNumbers>1</itemNumbers>'
            u'<itemFee>60</itemFee>'
            u'<itemName>引取手数料</itemName>'
            u'</item>'
            u'<item>'
            u'<itemId>system_fee</itemId>'
            u'<itemNumbers>1</itemNumbers>'
            u'<itemFee>80</itemFee>'
            u'<itemName>システム利用料</itemName>'
            u'</item>'
            u'</itemsInfo>'
            u'</orderItemsInfo>')

    def test_create_checkout_request_xml_with_items_and_special_fee(self):
        from lxml import etree
        from altair.app.ticketing.core.models import SalesSegment, PaymentDeliveryMethodPair, PaymentMethod, DeliveryMethod, Product, FeeTypeEnum
        from altair.app.ticketing.cart.models import Cart, CartedProduct
        from decimal import Decimal
        from base64 import b64decode
        target = self._buildTarget()
        cart = Cart(
            id=10,
            _order_no='XX0000000000',
            sales_segment=SalesSegment(),
            payment_delivery_pair=PaymentDeliveryMethodPair(
                system_fee=80,
                delivery_fee=60,
                transaction_fee=0,
                special_fee=70,
                special_fee_name=u'特別☆手数料',
                discount=10,
                payment_method=PaymentMethod(
                    fee=0,
                    fee_type=FeeTypeEnum.Once.v[0]
                    ),
                delivery_method=DeliveryMethod(
                    fee=0,
                    fee_type=FeeTypeEnum.Once.v[0]
                    )
                ),
            items=[
                CartedProduct(
                    product=Product(
                        id=i,
                        name='item %d' % i,
                        price=Decimal(i*10)
                    ),
                    quantity=(i + 1)
                    ) for i in range(2)
                ]
        )
        self._session.add(cart)
        self._session.flush()
        _, result = target.build_checkout_request_form(cart)
        result_n = etree.fromstring(result)
        checkout_n = result_n.find('input[@name="checkout"]')
        self.assertTrue(checkout_n is not None)
        payload = b64decode(checkout_n.get('value')).decode('utf-8')

        self.assertEqual(payload,
            u'<orderItemsInfo>'
            u'<serviceId>this-is-serviceId</serviceId>'
            u'<orderCompleteUrl>/completed</orderCompleteUrl>'
            u'<orderFailedUrl>/failed</orderFailedUrl>'
            u'<authMethod>1</authMethod>'
            u'<isTMode>1</isTMode>'
            u'<orderCartId>XX0000000000</orderCartId>'
            u'<orderTotalFee>230</orderTotalFee>'
            u'<itemsInfo>'
            u'<item>'
            u'<itemId>0</itemId>'
            u'<itemNumbers>1</itemNumbers>'
            u'<itemFee>0</itemFee>'
            u'<itemName>item 0</itemName>'
            u'</item>'
            u'<item>'
            u'<itemId>1</itemId>'
            u'<itemNumbers>2</itemNumbers>'
            u'<itemFee>10</itemFee>'
            u'<itemName>item 1</itemName>'
            u'</item>'
            u'<item>'
            u'<itemId>delivery_fee</itemId>'
            u'<itemNumbers>1</itemNumbers>'
            u'<itemFee>60</itemFee>'
            u'<itemName>引取手数料</itemName>'
            u'</item>'
            u'<item>'
            u'<itemId>system_fee</itemId>'
            u'<itemNumbers>1</itemNumbers>'
            u'<itemFee>80</itemFee>'
            u'<itemName>システム利用料</itemName>'
            u'</item>'
            u'<item>'
            u'<itemId>special_fee</itemId>'
            u'<itemNumbers>1</itemNumbers>'
            u'<itemFee>70</itemFee>'
            u'<itemName>特別☆手数料</itemName>'
            u'</item>'
            u'</itemsInfo>'
            u'</orderItemsInfo>')

    def test_create_checkout_request_xml_without_tmode(self):
        from altair.app.ticketing.core.models import SalesSegment, PaymentDeliveryMethodPair, PaymentMethod, DeliveryMethod, Product, FeeTypeEnum
        from altair.app.ticketing.cart.models import Cart, CartedProduct
        from decimal import Decimal
        from lxml import etree
        from base64 import b64decode
        args = [
            'this-is-serviceId',
            'success_url',
            'fail_url',
            'HMAC-MD5',
            'access_key',
            'https://example.com/api_url',
            '0'
        ]
        target = self._buildTarget(*args)
        cart = Cart(
            id=10,
            _order_no='XX0000000000',
            sales_segment=SalesSegment(),
            payment_delivery_pair=PaymentDeliveryMethodPair(
                system_fee=80,
                delivery_fee=60,
                transaction_fee=0,
                discount=10,
                payment_method=PaymentMethod(
                    fee=0,
                    fee_type=FeeTypeEnum.Once.v[0]
                    ),
                delivery_method=DeliveryMethod(
                    fee=0,
                    fee_type=FeeTypeEnum.Once.v[0]
                    )
                ),
            items=[
                CartedProduct(
                    product=Product(
                        id=i,
                        name='item %d' % i,
                        price=Decimal(i*10)
                        ),
                    quantity=(i + 1)
                    ) for i in range(2)
                ]
        )
        self._session.add(cart)
        self._session.flush()
        _, result = target.build_checkout_request_form(cart)
        result_n = etree.fromstring(result)
        checkout_n = result_n.find('input[@name="checkout"]')
        self.assertTrue(checkout_n is not None)
        payload = b64decode(checkout_n.get('value')).decode('utf-8')

        self.assertEqual(payload,
            u'<orderItemsInfo>'
            u'<serviceId>this-is-serviceId</serviceId>'
            u'<orderCompleteUrl>success_url</orderCompleteUrl>'
            u'<orderFailedUrl>fail_url</orderFailedUrl>'
            u'<authMethod>2</authMethod>'
            u'<isTMode>0</isTMode>'
            u'<orderCartId>XX0000000000</orderCartId>'
            u'<orderTotalFee>160</orderTotalFee>'
            u'<itemsInfo>'
            u'<item>'
            u'<itemId>0</itemId>'
            u'<itemNumbers>1</itemNumbers>'
            u'<itemFee>0</itemFee>'
            u'<itemName>item 0</itemName>'
            u'</item>'
            u'<item>'
            u'<itemId>1</itemId>'
            u'<itemNumbers>2</itemNumbers>'
            u'<itemFee>10</itemFee>'
            u'<itemName>item 1</itemName>'
            u'</item>'
            u'<item>'
            u'<itemId>delivery_fee</itemId>'
            u'<itemNumbers>1</itemNumbers>'
            u'<itemFee>60</itemFee>'
            u'<itemName>引取手数料</itemName>'
            u'</item>'
            u'<item>'
            u'<itemId>system_fee</itemId>'
            u'<itemNumbers>1</itemNumbers>'
            u'<itemFee>80</itemFee>'
            u'<itemName>システム利用料</itemName>'
            u'</item>'
            u'</itemsInfo>'
            u'</orderItemsInfo>')

    def test_save_order_complete(self):
        from lxml import etree
        from altair.app.ticketing.cart.models import Cart
        from .models import Checkout
        xml = etree.fromstring(
            '<orderCompleteRequest>'
            '<orderId>this-is-order-id</orderId>'
            '<orderControlId>this-is-order-control-id</orderControlId>'
            '<orderCartId>XX0000000000</orderCartId>'
            '<openId>https://example.com/openid/user/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx</openId>'
            '<isTMode>0</isTMode>'
            '<orderTotalFee>3000</orderTotalFee>'
            '<orderDate>2011-04-15 01:23:45</orderDate>'
            '<items>'
            '<item>'
            '<itemId>product1</itemId>'
            '<itemName>テスト用商品 1</itemName>'
            '<itemFee>1000</itemFee>'
            '<itemNumbers>1</itemNumbers>'
            '</item>'
            '<item>'
            '<itemId>product2</itemId>'
            '<itemName>テスト用商品 2</itemName>'
            '<itemFee>2000</itemFee>'
            '<itemNumbers>2</itemNumbers>'
            '</item>'
            '</items>'
            '</orderCompleteRequest>'
        )
        self._session.add(Cart(id=10, _order_no='XX0000000000'))
        self._session.flush()
        self.session.add(Checkout(orderCartId='XX0000000000', orderCartId_old=10))
        self.session.flush()
        xml_str = etree.tostring(xml)
        confirmId = xml_str.replace('+', ' ').encode('base64')

        target = self._buildTarget()
        result = target.save_order_complete(dict(confirmId=confirmId))

    def test_request_cancel_order_normal(self):
        from lxml import etree
        from .models import Checkout
        from altair.app.ticketing.cart.models import Cart
        from altair.multicheckout.testing import DummyHTTPLib

        res_data = etree.fromstring(
            '<root>'
            '<statusCode>0</statusCode>'
            '<acceptNumber>1</acceptNumber>'
            '<successNumber>1</successNumber>'
            '<failedNumber>0</failedNumber>'
            '<orders>'
            '<order>'
            '<orderControlId>dc-1234567890-110415-0000022222</orderControlId>'
            '</order>'
            '</orders>'
            '</root>'
        )
        target = self._buildTarget()
        target.comm._httplib = DummyHTTPLib(etree.tostring(res_data))

        self.session.add(
            Checkout(
                orderCartId='XX0000000000',
                orderControlId='dc-1234567890-110415-0000022222'
                )
            )
        self.session.flush()

        cart = Cart(
            _order_no='XX0000000000'
            )
        self._session.add(cart)
        self._session.flush()

        result = target.request_cancel_order([cart])

        self.assertEqual(target.comm._httplib.path, '/api_url/odrctla/cancelorder/1.0/')
        self.assertTrue(result)

    def test_request_cancel_order_with_error(self):
        from lxml import etree
        from altair.multicheckout.testing import DummyHTTPLib
        from altair.app.ticketing.cart.models import Cart
        from .models import Checkout
        from .exceptions import AnshinCheckoutAPIError

        res_data = etree.fromstring(
            '<root>'
            '<statusCode>1</statusCode>'
            '<acceptNumber>1</acceptNumber>'
            '<successNumber>0</successNumber>'
            '<failedNumber>1</failedNumber>'
            '<orders>'
            '<order>'
            '<orderControlId>dc-1234567890-110415-0000022222</orderControlId>'
            '<orderErrorCode>090</orderErrorCode>'
            '</order>'
            '</orders>'
            '<apiErrorCode>100</apiErrorCode>'
            '</root>'
        )
        target = self._buildTarget()
        target.comm._httplib = DummyHTTPLib(etree.tostring(res_data))

        self.session.add(
            Checkout(
                orderCartId='XX0000000000',
                orderControlId='dc-1234567890-110415-0000022222'
                )
            )
        self.session.flush()

        cart = Cart(
            _order_no='XX0000000000'
            )
        self._session.add(cart)
        self._session.flush()

        with self.assertRaises(AnshinCheckoutAPIError) as e:
            target.request_cancel_order([cart])

        self.assertEqual(target.comm._httplib.path, '/api_url/odrctla/cancelorder/1.0/')
        self.assertEqual(e.exception.error_code, '100')

    def test_request_fixation_order_normal(self):
        from lxml import etree
        from .models import Checkout
        from altair.multicheckout.testing import DummyHTTPLib
        from altair.app.ticketing.cart.models import Cart

        res_data = etree.fromstring(
            '<root>'
            '<statusCode>0</statusCode>'
            '<acceptNumber>1</acceptNumber>'
            '<successNumber>1</successNumber>'
            '<failedNumber>0</failedNumber>'
            '<orders>'
            '<order>'
            '<orderControlId>dc-1234567890-110415-0000022222</orderControlId>'
            '</order>'
            '</orders>'
            '</root>'
        )
        target = self._buildTarget()
        target.comm._httplib = DummyHTTPLib(etree.tostring(res_data))

        self.session.add(
            Checkout(
                orderCartId='XX0000000000',
                orderControlId='dc-1234567890-110415-0000022222'
                )
            )
        self.session.flush()

        cart = Cart(
            _order_no='XX0000000000'
            )
        self._session.add(cart)
        self._session.flush()

        result = target.request_fixation_order([cart])

        self.assertEqual(target.comm._httplib.path, '/api_url/odrctla/fixationorder/1.0/')
        self.assertTrue(result)

    def test_request_fixation_order_with_error(self):
        from lxml import etree
        from altair.multicheckout.testing import DummyHTTPLib
        from altair.app.ticketing.cart.models import Cart
        from .models import Checkout
        from .exceptions import AnshinCheckoutAPIError

        res_data = etree.fromstring(
            '<root>'
            '<statusCode>1</statusCode>'
            '<acceptNumber>1</acceptNumber>'
            '<successNumber>0</successNumber>'
            '<failedNumber>1</failedNumber>'
            '<orders>'
            '<order>'
            '<orderControlId>dc-1234567890-110415-0000022222</orderControlId>'
            '<orderErrorCode>090</orderErrorCode>'
            '</order>'
            '</orders>'
            '<apiErrorCode>100</apiErrorCode>'
            '</root>'
        )
        target = self._buildTarget()
        target.comm._httplib = DummyHTTPLib(etree.tostring(res_data))

        self.session.add(
            Checkout(
                orderCartId='XX0000000000',
                orderCartId_old=10,
                orderControlId='dc-1234567890-110415-0000022222'
                )
            )
        self.session.flush()

        cart = Cart(
            id=10,
            _order_no='XX0000000000'
            )
        self._session.add(cart)
        self._session.flush()

        with self.assertRaises(AnshinCheckoutAPIError) as e:
            target.request_fixation_order([cart])

        self.assertEqual(target.comm._httplib.path, '/api_url/odrctla/fixationorder/1.0/')
        self.assertEqual(e.exception.error_code, '100')

    def test_request_change_order_normal(self):
        from lxml import etree
        from altair.multicheckout.testing import DummyHTTPLib
        from altair.app.ticketing.orders.models import Order, OrderedProduct, OrderedProductItem
        from altair.app.ticketing.core.models import SalesSegment, PaymentDeliveryMethodPair, PaymentMethod, DeliveryMethod, FeeTypeEnum, Product
        from .models import Checkout, CheckoutItem

        self.create_order_test_data()

        res_data = etree.fromstring(
            '<root>'
            '<statusCode>0</statusCode>'
            '<acceptNumber>1</acceptNumber>'
            '<successNumber>1</successNumber>'
            '<failedNumber>0</failedNumber>'
            '<orders>'
            '<order>'
            '<orderControlId>dc-1234567890-110415-0000022222</orderControlId>'
            '</order>'
            '</orders>'
            '</root>'
        )
        target = self._buildTarget()
        target.comm._httplib = DummyHTTPLib(etree.tostring(res_data))

        self.session.add(
            Checkout(
                orderCartId='XX0000000000',
                orderControlId='dc-1234567890-110415-0000022222',
                items=[
                    CheckoutItem(
                        itemId='1',
                        itemName='dummy1',
                        itemNumbers=1,
                        itemFee=1000
                        ),
                    CheckoutItem(
                        itemId='2',
                        itemName='dummy2',
                        itemNumbers=2,
                        itemFee=2000
                        ),
                    CheckoutItem(
                        itemId='system_fee',
                        itemName='system_fee',
                        itemNumbers=1,
                        itemFee=100
                        ),
                    CheckoutItem(
                        itemId='delivery_fee',
                        itemName='delivery_fee',
                        itemNumbers=1,
                        itemFee=100
                        ),
                    ],
                )
            )
        self.session.flush()

        order = Order(
            order_no='XX0000000000',
            sales_segment=SalesSegment(),
            total_amount=0,
            system_fee=200,
            transaction_fee=0,
            delivery_fee=0,
            special_fee_name='special',
            special_fee=100,
            payment_delivery_pair=PaymentDeliveryMethodPair(
                system_fee=0,
                delivery_fee=0,
                transaction_fee=0,
                discount=10,
                payment_method=PaymentMethod(
                    fee=0,
                    fee_type=FeeTypeEnum.Once.v[0]
                    ),
                delivery_method=DeliveryMethod(
                    fee=0,
                    fee_type=FeeTypeEnum.Once.v[0]
                    )
                ),
            items=[
                OrderedProduct(
                    product=Product(id=1, name='dummy1', price=500),
                    price=500,
                    quantity=2
                    ),
                ]
            )
        self._session.add(order)
        self._session.flush()

        result = target.request_change_order([(order, None)])

        self.assertEqual(target.comm._httplib.path, '/api_url/odrctla/changepayment/1.0/')
        self.assertEqual(result['statusCode'], '0')
        self.assertEqual(result['acceptNumber'], '1')
        self.assertEqual(result['successNumber'], '1')
        self.assertEqual(result['failedNumber'], '0')
        self.assertEqual(len(result['orders']), 1)
        self.assertEqual(result['orders'][0]['orderControlId'], 'dc-1234567890-110415-0000022222')

    @mock.patch('altair.app.ticketing.checkout.api.get_cart_id_by_order_no')
    def test_request_change_order_refunding(self, get_cart_id_by_order_no):
        from lxml import etree
        from urlparse import parse_qs
        from base64 import b64decode
        from altair.multicheckout.testing import DummyHTTPLib
        from altair.app.ticketing.orders.models import Order, OrderedProduct
        from altair.app.ticketing.core.models import SalesSegment, PaymentDeliveryMethodPair, PaymentMethod, DeliveryMethod, FeeTypeEnum, Product
        from .models import Checkout
        from .api import build_checkout_object_from_order_like

        self.create_order_test_data()

        res_data = etree.fromstring(
            '<root>'
            '<statusCode>0</statusCode>'
            '<acceptNumber>1</acceptNumber>'
            '<successNumber>1</successNumber>'
            '<failedNumber>0</failedNumber>'
            '<orders>'
            '<order>'
            '<orderControlId>dc-1234567890-110415-0000022222</orderControlId>'
            '</order>'
            '</orders>'
            '</root>'
        )
        target = self._buildTarget()
        target.comm._httplib = DummyHTTPLib(etree.tostring(res_data))

        order = Order(
            order_no='XX0000000000',
            sales_segment=SalesSegment(),
            total_amount=200,
            system_fee=50,
            transaction_fee=0,
            delivery_fee=50,
            special_fee=20,
            special_fee_name=u'special',
            payment_delivery_pair=PaymentDeliveryMethodPair(
                system_fee=0,
                delivery_fee=0,
                transaction_fee=0,
                discount=10,
                payment_method=PaymentMethod(
                    fee=0,
                    fee_type=FeeTypeEnum.Once.v[0]
                    ),
                delivery_method=DeliveryMethod(
                    fee=0,
                    fee_type=FeeTypeEnum.Once.v[0]
                    )
                ),
            items=[
                OrderedProduct(
                    quantity=1,
                    product=Product(id=1, price=100),
                    price=100,
                    refund_price=50
                    )
                ],
            refund_total_amount=50,
            refund_system_fee=30,
            refund_delivery_fee=30,
            refund_special_fee=10
            )
        self._session.add(order)
        self._session.flush()

        get_cart_id_by_order_no.return_value = 1
        checkout_object = build_checkout_object_from_order_like(self.request, order)
        self.session.add(checkout_object)

        result = target.request_change_order([(order, order)])

        self.assertEqual(target.comm._httplib.path, '/api_url/odrctla/changepayment/1.0/')
        self.assertEqual(result['statusCode'], '0')
        self.assertEqual(result['acceptNumber'], '1')
        self.assertEqual(result['successNumber'], '1')
        self.assertEqual(result['failedNumber'], '0')
        self.assertEqual(len(result['orders']), 1)
        self.assertEqual(result['orders'][0]['orderControlId'], 'dc-1234567890-110415-0000022222')
        qs = parse_qs(target.comm._httplib.body)
        self.assertTrue('rparam' in qs)
        xml = etree.fromstring(b64decode(qs['rparam'][0]))
        order_n_list = xml.findall(u'orders/order')
        self.assertEqual(len(order_n_list), 1)
        item_n_list = order_n_list[0].findall(u'items/item')
        self.assertEqual(len(item_n_list), 4)
        self.assertEqual(item_n_list[0].find(u'itemId').text, u'1')
        self.assertEqual(item_n_list[0].find(u'itemNumbers').text, u'1')
        self.assertEqual(item_n_list[0].find(u'itemFee').text, u'50')
        self.assertEqual(item_n_list[1].find(u'itemId').text, u'delivery_fee')
        self.assertEqual(item_n_list[1].find(u'itemNumbers').text, u'1')
        self.assertEqual(item_n_list[1].find(u'itemFee').text, u'20')
        self.assertEqual(item_n_list[2].find(u'itemId').text, u'system_fee')
        self.assertEqual(item_n_list[2].find(u'itemNumbers').text, u'1')
        self.assertEqual(item_n_list[2].find(u'itemFee').text, u'20')
        self.assertEqual(item_n_list[3].find(u'itemId').text, u'special_fee')
        self.assertEqual(item_n_list[3].find(u'itemNumbers').text, u'1')
        self.assertEqual(item_n_list[3].find(u'itemFee').text, u'10')

    def test_request_change_order_with_error(self):
        from lxml import etree
        from decimal import Decimal
        from altair.multicheckout.testing import DummyHTTPLib
        from altair.app.ticketing.core.models import SalesSegment, PaymentDeliveryMethodPair, PaymentMethod, DeliveryMethod, FeeTypeEnum
        from altair.app.ticketing.orders.models import Order
        from .models import Checkout
        from .exceptions import AnshinCheckoutAPIError

        self.create_order_test_data()

        res_data = etree.fromstring(
            '<root>'
            '<statusCode>1</statusCode>'
            '<acceptNumber>1</acceptNumber>'
            '<successNumber>0</successNumber>'
            '<failedNumber>1</failedNumber>'
            '<orders>'
            '<order>'
            '<orderControlId>dc-1234567890-110415-0000022222</orderControlId>'
            '<orderErrorCode>090</orderErrorCode>'
            '</order>'
            '</orders>'
            '<apiErrorCode>100</apiErrorCode>'
            '</root>'
        )
        target = self._buildTarget()
        target.comm._httplib = DummyHTTPLib(etree.tostring(res_data))

        self.session.add(
            Checkout(
                orderCartId='XX0000000000',
                orderControlId='dc-1234567890-110415-0000022222'
                )
            )
        self.session.flush()

        order = Order(
            order_no='XX0000000000',
            sales_segment=SalesSegment(),
            total_amount=0,
            system_fee=0,
            transaction_fee=0,
            delivery_fee=0,
            payment_delivery_pair=PaymentDeliveryMethodPair(
                system_fee=0,
                delivery_fee=0,
                transaction_fee=0,
                discount=10,
                payment_method=PaymentMethod(
                    fee=0,
                    fee_type=FeeTypeEnum.Once.v[0]
                    ),
                delivery_method=DeliveryMethod(
                    fee=0,
                    fee_type=FeeTypeEnum.Once.v[0]
                    )
                )
            )
        self._session.add(order)
        self._session.flush()

        with self.assertRaises(AnshinCheckoutAPIError) as e:
            result = target.request_change_order([(order, None)])

        self.assertEqual(target.comm._httplib.path, '/api_url/odrctla/changepayment/1.0/')
        self.assertEqual(e.exception.error_code, '100')


if __name__ == "__main__":
    unittest.main()
