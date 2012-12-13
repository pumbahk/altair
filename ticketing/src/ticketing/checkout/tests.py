# -*- coding:utf-8 -*-

import unittest
from datetime import datetime

from pyramid import testing

import ticketing.models
import ticketing.core.models
from ticketing.testing import _setup_db as _setup_db_, _teardown_db
from ticketing.checkout import api, models, interfaces


def _setup_db(echo=False):
    return _setup_db_(
        modules=[
            'ticketing.models',
            'ticketing.cart.models',
            'ticketing.users.models',
            'ticketing.checkout.models',
            ],
        echo=echo
    )


class IncludeMe(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, config):
        from ticketing.checkout import includeme
        return includeme(config)

    def test_it_with_sha1(self):
        from ticketing.checkout.interfaces import ISigner
        self.config.registry.settings.update({
            'altair_checkout.secret': 'this-is-secret',
            'altair_checkout.auth_method': 'HMAC-SHA1',
        })
        self._callFUT(self.config)

        lookup = self.config.registry.utilities.lookup([], ISigner, 'HMAC')
        self.assertIsNotNone(lookup)
        self.assertTrue(isinstance(lookup, api.HMAC_SHA1))

    def test_it_with_md5(self):
        from ticketing.checkout.interfaces import ISigner
        self.config.registry.settings.update({
            'altair_checkout.secret': 'this-is-secret',
            'altair_checkout.auth_method': 'HMAC-MD5',
        })
        self._callFUT(self.config)

        lookup = self.config.registry.utilities.lookup([], ISigner, 'HMAC')
        self.assertIsNotNone(lookup)
        self.assertTrue(isinstance(lookup, api.HMAC_MD5))


class SignToXml(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *args, **kwargs):
        return api.sign_to_xml(*args, **kwargs)

    def test_it(self):
        class DummySigner(object):
            def __call__(self, xml):
                self.called = xml
                return 'sign!'
        dummySigner = DummySigner()
        self.config.registry.utilities.register([], interfaces.ISigner, 'HMAC', dummySigner)

        request = testing.DummyRequest()
        xml = object()

        result = self._callFUT(request, xml)
        self.assertEqual(result, 'sign!')


class CheckoutTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.session = _setup_db()

        from pyramid.threadlocal import get_current_request, manager
        thread = manager.pop()
        thread['request'] = testing.DummyRequest()
        manager.push(thread)

    def tearDown(self):
        testing.tearDown()
        _teardown_db()

    def _getTarget(self):
        return api.Checkout

    def _makeOne(self, *args, **kwargs):
        args = args or [
            'this-is-serviceId',
            '/completed',
            '/failed',
            'HMAC-SHA1',
            'access_key',
            'https://example.com/api_url',
            '1'
        ]
        return self._getTarget()(*args, **kwargs)

    def test__create_checkout_item_xml(self):
        import xml.etree.ElementTree as et
        xml = et.XML('<root></root>')

        target = self._makeOne()
        params = dict(
            itemId='this-is-itemId',
            itemName=u'なまえ',
            itemNumbers='100',
            itemFee='2112'
        )
        target._create_checkout_item_xml(xml, **params)
        self.assertEqual(et.tostring(xml),
            '<root>'
            '<item>'
            '<itemId>this-is-itemId</itemId>'
            '<itemNumbers>100</itemNumbers>'
            '<itemFee>2112</itemFee>'
            '<itemName>&#12394;&#12414;&#12360;</itemName>'
            '</item>'
            '</root>'
        )

    def test_create_checkout_request_xml_no_products(self):
        target = self._makeOne()
        cart = testing.DummyResource(
            id=10,
            total_amount=1000,
            system_fee=80,
            transaction_fee=70,
            delivery_fee=60,
            products=[]
        )
        result = target.create_checkout_request_xml(cart)

        self.assertEqual(result,
            '<orderItemsInfo>'
            '<serviceId>this-is-serviceId</serviceId>'
            '<orderCompleteUrl>https://example.com:80/completed</orderCompleteUrl>'
            '<orderFailedUrl>https://example.com:80/failed</orderFailedUrl>'
            '<authMethod>1</authMethod>'
            '<isTMode>1</isTMode>'
            '<orderCartId>10</orderCartId>'
            '<orderTotalFee>1000</orderTotalFee>'
            '<itemsInfo>'
            '<item>'
            '<itemId>system_fee</itemId>'
            '<itemNumbers>1</itemNumbers>'
            '<itemFee>80</itemFee>'
            '<itemName>&#12471;&#12473;&#12486;&#12512;&#21033;&#29992;&#26009;</itemName>'
            '</item>'
            '<item>'
            '<itemId>transaction_fee</itemId>'
            '<itemNumbers>1</itemNumbers>'
            '<itemFee>70</itemFee>'
            '<itemName>&#27770;&#28168;&#25163;&#25968;&#26009;</itemName>'
            '</item>'
            '<item>'
            '<itemId>delivery_fee</itemId>'
            '<itemNumbers>1</itemNumbers>'
            '<itemFee>60</itemFee>'
            '<itemName>&#37197;&#36865;&#25163;&#25968;&#26009;</itemName>'
            '</item>'
            '</itemsInfo>'
            '</orderItemsInfo>')

    def test_create_checkout_item_xml_with_items(self):
        target = self._makeOne()
        cart = testing.DummyResource(
            id=10,
            total_amount=1000,
            system_fee=80,
            transaction_fee=70,
            delivery_fee=60,
            products=[
                testing.DummyResource(
                    product=testing.DummyResource(
                        id='item-%02d' % i,
                        name='item %d' % i,
                    ),
                    quantity=i,
                    amount=20 + i * 10
                ) for i in range(2)
            ]
        )
        result = target.create_checkout_request_xml(cart)

        self.assertEqual(result,
            '<orderItemsInfo>'
            '<serviceId>this-is-serviceId</serviceId>'
            '<orderCompleteUrl>https://example.com:80/completed</orderCompleteUrl>'
            '<orderFailedUrl>https://example.com:80/failed</orderFailedUrl>'
            '<authMethod>1</authMethod>'
            '<isTMode>1</isTMode>'
            '<orderCartId>10</orderCartId>'
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
            '<item>'
            '<itemId>system_fee</itemId>'
            '<itemNumbers>1</itemNumbers>'
            '<itemFee>80</itemFee>'
            '<itemName>&#12471;&#12473;&#12486;&#12512;&#21033;&#29992;&#26009;</itemName>'
            '</item>'
            '<item>'
            '<itemId>transaction_fee</itemId>'
            '<itemNumbers>1</itemNumbers>'
            '<itemFee>70</itemFee>'
            '<itemName>&#27770;&#28168;&#25163;&#25968;&#26009;</itemName>'
            '</item>'
            '<item>'
            '<itemId>delivery_fee</itemId>'
            '<itemNumbers>1</itemNumbers>'
            '<itemFee>60</itemFee>'
            '<itemName>&#37197;&#36865;&#25163;&#25968;&#26009;</itemName>'
            '</item>'
            '</itemsInfo>'
            '</orderItemsInfo>')

    def test_create_checkout_item_xml_without_tmode(self):
        args = [
            'this-is-serviceId',
            '/completed',
            '/failed',
            'HMAC-MD5',
            'access_key',
            'https://example.com/api_url',
            '0'
        ]
        target = self._makeOne(*args)
        cart = testing.DummyResource(
            id=10,
            total_amount=1000,
            system_fee=80,
            transaction_fee=70,
            delivery_fee=60,
            products=[
            testing.DummyResource(
                product=testing.DummyResource(
                    id='item-%02d' % i,
                    name='item %d' % i,
                ),
                quantity=i,
                amount=20 + i * 10
            ) for i in range(2)
            ]
        )
        result = target.create_checkout_request_xml(cart)

        self.assertEqual(result,
            '<orderItemsInfo>'
            '<serviceId>this-is-serviceId</serviceId>'
            '<orderCompleteUrl>https://example.com:80/completed</orderCompleteUrl>'
            '<orderFailedUrl>https://example.com:80/failed</orderFailedUrl>'
            '<authMethod>2</authMethod>'
            '<isTMode>0</isTMode>'
            '<orderCartId>10</orderCartId>'
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
            '<item>'
            '<itemId>system_fee</itemId>'
            '<itemNumbers>1</itemNumbers>'
            '<itemFee>80</itemFee>'
            '<itemName>&#12471;&#12473;&#12486;&#12512;&#21033;&#29992;&#26009;</itemName>'
            '</item>'
            '<item>'
            '<itemId>transaction_fee</itemId>'
            '<itemNumbers>1</itemNumbers>'
            '<itemFee>70</itemFee>'
            '<itemName>&#27770;&#28168;&#25163;&#25968;&#26009;</itemName>'
            '</item>'
            '<item>'
            '<itemId>delivery_fee</itemId>'
            '<itemNumbers>1</itemNumbers>'
            '<itemFee>60</itemFee>'
            '<itemName>&#37197;&#36865;&#25163;&#25968;&#26009;</itemName>'
            '</item>'
            '</itemsInfo>'
            '</orderItemsInfo>')

    def test_create_order_complete_response_xml(self):
        target = self._makeOne()
        complete_time = datetime.strptime('2012-12-12 12:12:12', '%Y-%m-%d %H:%M:%S')
        result = target.create_order_complete_response_xml(0, complete_time)

        self.assertIsNotNone(result)
        self.assertEqual(result,
            '<orderCompleteResponse>'
            '<result>0</result>'
            '<completeTime>2012-12-12 12:12:12</completeTime>'
            '</orderCompleteResponse>')

    def test__parse_order_complete_xml(self):
        import xml.etree.ElementTree as et
        xml = et.XML(
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
        target = self._makeOne()
        checkout = target._parse_order_complete_xml(xml)

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
        import xml.etree.ElementTree as et
        xml = et.XML(
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
        target = self._makeOne()
        checkout = testing.DummyResource(items=[])
        target._parse_item_xml(xml, checkout)

        self.assertEqual(len(checkout.items), 2)
        self.assertEqual(checkout.items[0].itemId, 'product1')
        self.assertEqual(checkout.items[0].itemName, u'テスト用商品 1')
        self.assertEqual(checkout.items[0].itemNumbers, 1)
        self.assertEqual(checkout.items[0].itemFee, 1000)
        self.assertEqual(checkout.items[1].itemId, 'product2')
        self.assertEqual(checkout.items[1].itemName, u'テスト用商品 2')
        self.assertEqual(checkout.items[1].itemNumbers, 2)
        self.assertEqual(checkout.items[1].itemFee, 2000)

    def test_save_order_complete(self):
        import xml.etree.ElementTree as et
        xml = et.XML(
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
        xml_str = et.tostring(xml)
        confirmId = xml_str.replace('+', ' ').encode('base64')

        target = self._makeOne()
        request = testing.DummyRequest(dict(confirmId=confirmId))
        result = target.save_order_complete(request)

    def test_create_order_cancel_request_xml_no_orders(self):
        target = self._makeOne()
        orders = []
        request_id = api.generate_requestid()
        result = target.create_order_cancel_request_xml(orders, request_id)

        self.assertIsNotNone(result)
        self.assertEqual(
            result,
            '<root>'
            '<serviceId>this-is-serviceId</serviceId>'
            '<accessKey>access_key</accessKey>'
            '<requestId>%(request_id)s</requestId>'
            '<orders />'
            '</root>' % dict(request_id=request_id)
        )

    def test_create_order_cancel_request_xml_with_orders(self):
        target = self._makeOne()
        orders = [
            testing.DummyResource(
                cart = testing.DummyResource(
                    checkout = testing.DummyResource(orderControlId='10')
                )
            ),
            testing.DummyResource(
                cart = testing.DummyResource(
                    checkout = testing.DummyResource(orderControlId='20')
                )
            )
        ]
        request_id = api.generate_requestid()
        result = target.create_order_cancel_request_xml(orders, request_id)

        self.assertIsNotNone(result)
        self.assertEqual(
            result,
            '<root>'
            '<serviceId>this-is-serviceId</serviceId>'
            '<accessKey>access_key</accessKey>'
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

    def test_order_cancel_url(self):
        target = self._makeOne()
        self.assertEqual(target.order_cancel_url(), 'https://example.com/api_url/odrctla/cancelorder/1.0/')

    def test__parse_response_order_cancel_xml(self):
        import xml.etree.ElementTree as et
        xml = et.XML(
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
        target = self._makeOne()
        result = target._parse_response_order_cancel_xml(xml)

        self.assertEqual(result['statusCode'], '1')
        self.assertEqual(result['acceptNumber'], '2')
        self.assertEqual(result['successNumber'], '3')
        self.assertEqual(result['failedNumber'], '4')
        self.assertEqual(result['apiErrorCode'], '100')
        self.assertEqual(len(result['orders']), 1)
        self.assertEqual(result['orders'][0]['orderControlId'], 'dc-1234567890-110415-0000022222')
        self.assertEqual(result['orders'][0]['orderErrorCode'], '090')

    def test_request_order_cancel(self):
        import xml.etree.ElementTree as et
        from ticketing.multicheckout.testing import DummyHTTPLib

        res_data = et.XML(
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
        target = self._makeOne()
        target._httplib = DummyHTTPLib(et.tostring(res_data))

        orders = [
            testing.DummyResource(
                cart = testing.DummyResource(
                    checkout = testing.DummyResource(orderControlId='10')
                )
            ),
            testing.DummyResource(
                cart = testing.DummyResource(
                    checkout = testing.DummyResource(orderControlId='20')
                )
            )
        ]
        result = target.request_order_cancel(orders)

        self.assertEqual(target._httplib.path, '/api_url/odrctla/cancelorder/1.0/')
        self.assertEqual(result['statusCode'], '1')
        self.assertEqual(result['acceptNumber'], '2')
        self.assertEqual(result['successNumber'], '3')
        self.assertEqual(result['failedNumber'], '4')
        self.assertEqual(result['apiErrorCode'], '100')
        self.assertEqual(len(result['orders']), 1)
        self.assertEqual(result['orders'][0]['orderControlId'], 'dc-1234567890-110415-0000022222')
        self.assertEqual(result['orders'][0]['orderErrorCode'], '090')


if __name__ == "__main__":
    unittest.main()
