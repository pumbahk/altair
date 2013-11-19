# -*- coding:utf-8 -*-

import unittest
from datetime import datetime

from pyramid import testing

import altair.app.ticketing.models
import altair.app.ticketing.core.models
from altair.app.ticketing.testing import _setup_db as _setup_db_, _teardown_db
from altair.app.ticketing.checkout import api, models, interfaces
from altair.app.ticketing.core import models as c_models


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


class GetCheckoutService(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.session = _setup_db()

        from altair.app.ticketing.core.models import Organization, Host
        organization = c_models.Organization(id=1, name=u'organization_name', short_name=u'org')
        self.session.add(organization)

        host = models.RakutenCheckoutSetting(
            id=1,
            organization_id=1,
            service_id='service_id',
            secret='secret',
            auth_method='HMAC-SHA1',
            channel=c_models.ChannelEnum.PC.v
        )
        self.session.add(host)

        self.session.flush()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *args, **kwargs):
        return api.get_checkout_service(*args, **kwargs)

    def test_it(self):
        request = testing.DummyRequest()
        organization = c_models.Organization.get(1)
        channel = c_models.ChannelEnum.PC

        settings = {
            u'altair_checkout.success_url': 'http://example.com/success/',
            u'altair_checkout.fail_url': 'http://example.com/fail/',
            u'altair_checkout.api_url': 'http://example.com/api/',
            u'altair_checkout.is_test': '1',
        }
        self.config.registry.settings.update(settings)
        request.config = self.config

        result = self._callFUT(request, organization, channel)
        self.assertTrue(isinstance(result, api.Checkout))
        self.assertEqual(result.success_url, 'http://example.com/success/')
        self.assertEqual(result.fail_url, 'http://example.com/fail/')
        self.assertEqual(result.api_url, 'http://example.com/api/')
        self.assertEqual(result.is_test, '1')
        self.assertEqual(result.service_id, 'service_id')
        self.assertEqual(result.auth_method, 'HMAC-SHA1')
        self.assertEqual(result.secret, 'secret')


class SignToXml(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.session = _setup_db()

        from altair.app.ticketing.core.models import Organization, Host
        organization = c_models.Organization(id=1, name=u'organization_name', short_name=u'org')
        self.session.add(organization)

        host = models.RakutenCheckoutSetting(
            id=1,
            organization_id=1,
            service_id='service_id',
            secret='secret',
            auth_method='HMAC-SHA1',
            channel=c_models.ChannelEnum.PC.v
        )
        self.session.add(host)

        self.session.flush()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *args, **kwargs):
        return api.sign_to_xml(*args, **kwargs)

    def test_it(self):
        request = testing.DummyRequest()
        organization = c_models.Organization.get(1)
        channel = c_models.ChannelEnum.PC
        xml = '<xml></xml>'

        result = self._callFUT(request, organization, channel, xml)
        self.assertEqual(result, '35ca1b4753dfd6d58b0ee455dfe1ecc90620f3fa')


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

    def create_order_test_data(self):
        from altair.app.ticketing.core.models import Order, OrderedProduct, Product
        product = Product(
            id=22,
            price=140,
            public=1,
            display_order=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.session.add(product)
        ordered_product = OrderedProduct(
            id=11,
            order_id=1,
            product_id=22,
            price=140,
            quantity=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.session.add(ordered_product)
        order = Order(
            id=1,
            order_no='testing-order-no',
            branch_no=1,
            total_amount=200,
            system_fee=10,
            transaction_fee=20,
            delivery_fee=30,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.session.add(order)

        from altair.app.ticketing.cart.models import Cart
        cart = Cart(
            id=111,
            order_id=1,
            _order_no=order.order_no,
        )
        self.session.add(cart)

        from altair.app.ticketing.checkout.models import Checkout
        checkout = Checkout(id=1111, orderCartId=111, orderControlId=u'dc-1234567890-110415-0000022222')
        self.session.add(checkout)
        self.session.flush()

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

    def test__create_checkout_item_xml_change_order(self):
        import xml.etree.ElementTree as et
        xml = et.XML('<root></root>')

        target = self._makeOne()
        params = dict(
            itemId='this-is-itemId',
            itemNumbers='100',
            itemFee='2112',
            orderShippingFee='0'
        )
        target._create_checkout_item_xml(xml, **params)
        self.assertEqual(et.tostring(xml),
            '<root>'
            '<item>'
            '<itemId>this-is-itemId</itemId>'
            '<itemNumbers>100</itemNumbers>'
            '<itemFee>2112</itemFee>'
            #'<orderShippingFee>0</orderShippingFee>'
            '</item>'
            '</root>'
        )

    def test_create_checkout_request_xml_no_products(self):
        target = self._makeOne()
        cart = testing.DummyResource(
            id=10,
            total_amount=1000,
            system_fee=80,
            delivery_fee=60,
            items=[]
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
            '<itemId>delivery_fee</itemId>'
            '<itemNumbers>1</itemNumbers>'
            '<itemFee>60</itemFee>'
            '<itemName>&#24341;&#21462;&#25163;&#25968;&#26009;</itemName>'
            '</item>'
            '</itemsInfo>'
            '</orderItemsInfo>')

    def test_create_checkout_request_xml_with_items(self):
        target = self._makeOne()
        cart = testing.DummyResource(
            id=10,
            total_amount=1000,
            system_fee=80,
            delivery_fee=60,
            items=[
                testing.DummyResource(
                    product=testing.DummyResource(
                        id='item-%02d' % i,
                        name='item %d' % i,
                        price=i*10
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
            '<itemFee>0</itemFee>'
            '<itemName>item 0</itemName>'
            '</item>'
            '<item>'
            '<itemId>item-01</itemId>'
            '<itemNumbers>1</itemNumbers>'
            '<itemFee>10</itemFee>'
            '<itemName>item 1</itemName>'
            '</item>'
            '<item>'
            '<itemId>system_fee</itemId>'
            '<itemNumbers>1</itemNumbers>'
            '<itemFee>80</itemFee>'
            '<itemName>&#12471;&#12473;&#12486;&#12512;&#21033;&#29992;&#26009;</itemName>'
            '</item>'
            '<item>'
            '<itemId>delivery_fee</itemId>'
            '<itemNumbers>1</itemNumbers>'
            '<itemFee>60</itemFee>'
            '<itemName>&#24341;&#21462;&#25163;&#25968;&#26009;</itemName>'
            '</item>'
            '</itemsInfo>'
            '</orderItemsInfo>')

    def test_create_checkout_request_xml_without_tmode(self):
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
            delivery_fee=60,
            items=[
                testing.DummyResource(
                    product=testing.DummyResource(
                        id='item-%02d' % i,
                        name='item %d' % i,
                        price=i*10
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
            '<itemFee>0</itemFee>'
            '<itemName>item 0</itemName>'
            '</item>'
            '<item>'
            '<itemId>item-01</itemId>'
            '<itemNumbers>1</itemNumbers>'
            '<itemFee>10</itemFee>'
            '<itemName>item 1</itemName>'
            '</item>'
            '<item>'
            '<itemId>system_fee</itemId>'
            '<itemNumbers>1</itemNumbers>'
            '<itemFee>80</itemFee>'
            '<itemName>&#12471;&#12473;&#12486;&#12512;&#21033;&#29992;&#26009;</itemName>'
            '</item>'
            '<item>'
            '<itemId>delivery_fee</itemId>'
            '<itemNumbers>1</itemNumbers>'
            '<itemFee>60</itemFee>'
            '<itemName>&#24341;&#21462;&#25163;&#25968;&#26009;</itemName>'
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

    def test__create_order_control_request_xml_no_orders(self):
        target = self._makeOne()
        orders = []
        request_id = api.generate_requestid()
        result = target._create_order_control_request_xml(orders, request_id)

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

    def test__create_order_control_request_xml_with_orders(self):
        target = self._makeOne()
        request_id = api.generate_requestid()
        result = target._create_order_control_request_xml(['10', '20'], request_id)

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

    def test__create_order_control_request_xml_with_items(self):
        self.create_order_test_data()
        target = self._makeOne()
        request_id = api.generate_requestid()
        result = target._create_order_control_request_xml(['dc-1234567890-110415-0000022222'], request_id, with_items=True)

        self.assertIsNotNone(result)
        self.assertEqual(
            result,
            '<root>'
            '<serviceId>this-is-serviceId</serviceId>'
            '<accessKey>access_key</accessKey>'
            '<requestId>%(request_id)s</requestId>'
            '<orders>'
            '<order>'
            '<orderControlId>dc-1234567890-110415-0000022222</orderControlId>'
            '<items>'
            '<item>'
            '<itemId>22</itemId>'
            '<itemNumbers>1</itemNumbers>'
            '<itemFee>140</itemFee>'
            #'<orderShippingFee>0</orderShippingFee>'
            '</item>'
            '<item>'
            '<itemId>system_fee</itemId>'
            '<itemNumbers>1</itemNumbers>'
            '<itemFee>10</itemFee>'
            #'<orderShippingFee>0</orderShippingFee>'
            #'</item>'
            #'<item>'
            #'<itemId>transaction_fee</itemId>'
            #'<itemNumbers>1</itemNumbers>'
            #'<itemFee>20</itemFee>'
            #'<orderShippingFee>0</orderShippingFee>'
            '</item>'
            '<item>'
            '<itemId>delivery_fee</itemId>'
            '<itemNumbers>1</itemNumbers>'
            '<itemFee>30</itemFee>'
            #'<orderShippingFee>0</orderShippingFee>'
            '</item>'
            '</items>'
            '<orderShippingFee>0</orderShippingFee>'  # <- 移動？
            '</order>'
            '</orders>'
            '</root>' % dict(request_id=request_id)
        )

    def test__parse_order_control_response_xml(self):
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
        result = target._parse_order_control_response_xml(xml)

        self.assertEqual(result['statusCode'], '1')
        self.assertEqual(result['acceptNumber'], '2')
        self.assertEqual(result['successNumber'], '3')
        self.assertEqual(result['failedNumber'], '4')
        self.assertEqual(result['apiErrorCode'], '100')
        self.assertEqual(len(result['orders']), 1)
        self.assertEqual(result['orders'][0]['orderControlId'], 'dc-1234567890-110415-0000022222')
        self.assertEqual(result['orders'][0]['orderErrorCode'], '090')

    def test_request_cancel_order_normal(self):
        import xml.etree.ElementTree as et
        from altair.multicheckout.testing import DummyHTTPLib

        res_data = et.XML(
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
        target = self._makeOne()
        target._httplib = DummyHTTPLib(et.tostring(res_data))

        order_control_id = ['dc-1234567890-110415-0000022222']
        result = target.request_cancel_order(order_control_id)

        self.assertEqual(target._httplib.path, '/api_url/odrctla/cancelorder/1.0/')
        self.assertTrue(result)

    def test_request_cancel_order_with_error(self):
        import xml.etree.ElementTree as et
        from altair.multicheckout.testing import DummyHTTPLib

        res_data = et.XML(
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
        target = self._makeOne()
        target._httplib = DummyHTTPLib(et.tostring(res_data))

        order_control_id = ['dc-1234567890-110415-0000022222']
        result = target.request_cancel_order(order_control_id)

        self.assertEqual(target._httplib.path, '/api_url/odrctla/cancelorder/1.0/')
        self.assertEqual(result['statusCode'], '1')
        self.assertEqual(result['acceptNumber'], '1')
        self.assertEqual(result['successNumber'], '0')
        self.assertEqual(result['failedNumber'], '1')
        self.assertEqual(result['apiErrorCode'], '100')
        self.assertEqual(len(result['orders']), 1)
        self.assertEqual(result['orders'][0]['orderControlId'], 'dc-1234567890-110415-0000022222')
        self.assertEqual(result['orders'][0]['orderErrorCode'], '090')

    def test_request_fixation_order_normal(self):
        import xml.etree.ElementTree as et
        from altair.multicheckout.testing import DummyHTTPLib

        res_data = et.XML(
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
        target = self._makeOne()
        target._httplib = DummyHTTPLib(et.tostring(res_data))

        order_control_id = ['dc-1234567890-110415-0000022222']
        result = target.request_fixation_order(order_control_id)

        self.assertEqual(target._httplib.path, '/api_url/odrctla/fixationorder/1.0/')
        self.assertTrue(result)

    def test_request_fixation_order_with_error(self):
        import xml.etree.ElementTree as et
        from altair.multicheckout.testing import DummyHTTPLib

        res_data = et.XML(
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
        target = self._makeOne()
        target._httplib = DummyHTTPLib(et.tostring(res_data))

        order_control_id = ['dc-1234567890-110415-0000022222']
        result = target.request_fixation_order(order_control_id)

        self.assertEqual(target._httplib.path, '/api_url/odrctla/fixationorder/1.0/')
        self.assertEqual(result['statusCode'], '1')
        self.assertEqual(result['acceptNumber'], '1')
        self.assertEqual(result['successNumber'], '0')
        self.assertEqual(result['failedNumber'], '1')
        self.assertEqual(result['apiErrorCode'], '100')
        self.assertEqual(len(result['orders']), 1)
        self.assertEqual(result['orders'][0]['orderControlId'], 'dc-1234567890-110415-0000022222')
        self.assertEqual(result['orders'][0]['orderErrorCode'], '090')

    def test_request_change_order_normal(self):
        import xml.etree.ElementTree as et
        from altair.multicheckout.testing import DummyHTTPLib

        self.create_order_test_data()

        res_data = et.XML(
            '<root>'
            '<statusCode>1</statusCode>'
            '<acceptNumber>1</acceptNumber>'
            '<successNumber>0</successNumber>'
            '<failedNumber>1</failedNumber>'
            '<orders>'
            '<order>'
            '<orderControlId>dc-1234567890-110415-0000022222</orderControlId>'
            '</order>'
            '</orders>'
            '</root>'
        )
        target = self._makeOne()
        target._httplib = DummyHTTPLib(et.tostring(res_data))

        order_control_id = ['dc-1234567890-110415-0000022222']
        result = target.request_change_order(order_control_id)

        self.assertEqual(target._httplib.path, '/api_url/odrctla/changepayment/1.0/')
        self.assertEqual(result['statusCode'], '1')
        self.assertEqual(result['acceptNumber'], '1')
        self.assertEqual(result['successNumber'], '0')
        self.assertEqual(result['failedNumber'], '1')
        self.assertEqual(len(result['orders']), 1)
        self.assertEqual(result['orders'][0]['orderControlId'], 'dc-1234567890-110415-0000022222')

    def test_request_change_order_with_error(self):
        import xml.etree.ElementTree as et
        from altair.multicheckout.testing import DummyHTTPLib

        self.create_order_test_data()

        res_data = et.XML(
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
        target = self._makeOne()
        target._httplib = DummyHTTPLib(et.tostring(res_data))

        order_control_id = ['dc-1234567890-110415-0000022222']
        result = target.request_change_order(order_control_id)

        self.assertEqual(target._httplib.path, '/api_url/odrctla/changepayment/1.0/')
        self.assertEqual(result['statusCode'], '1')
        self.assertEqual(result['acceptNumber'], '1')
        self.assertEqual(result['successNumber'], '0')
        self.assertEqual(result['failedNumber'], '1')
        self.assertEqual(result['apiErrorCode'], '100')
        self.assertEqual(len(result['orders']), 1)
        self.assertEqual(result['orders'][0]['orderControlId'], 'dc-1234567890-110415-0000022222')
        self.assertEqual(result['orders'][0]['orderErrorCode'], '090')


if __name__ == "__main__":
    unittest.main()
