# -*- coding:utf-8 -*-

import unittest
from pyramid import testing

class CarXmlVisitor(unittest.TestCase):
    def _getTarget(self):
        from .api import CartXmlVisitor
        return CartXmlVisitor

    def _makeOne(self):
        return self._getTarget()()

    def test_visit_invalid(self):
        import xml.etree.ElementTree as et

        xml = et.XML('<root />')
        target = self._makeOne()
        result = target.visit(xml)

        self.assertIsNone(result)

    def test_visit_empty(self):
        import xml.etree.ElementTree as et

        xml = et.XML('<cartConfirmationRequest />')
        target = self._makeOne()
        result = target.visit(xml)

        self.assertIsNotNone(result)

    def test_visit_item(self):
        import xml.etree.ElementTree as et
        xml = et.XML('<item>'
                     '<itemId>this-is-itemId</itemId>'
                     '<itemName>なまえ</itemName>'
                     '<itemNumbers>100</itemNumbers>'
                     '<itemFee>2112</itemFee>'
                     '</item>')

        target = self._makeOne()
        cart = testing.DummyResource(items=[])
        target.visit_item(xml, cart)
        item = cart.items[0]
        self.assertEqual(item.itemId, 'this-is-itemId')
        self.assertEqual(item.itemName, u'なまえ')
        self.assertEqual(item.itemNumbers, 100)
        self.assertEqual(item.itemFee, 2112)


    def test_visit_items(self):
        import xml.etree.ElementTree as et
        xml = et.XML('<items>'
                     '<item />'
                     '<item />'
                     '<item />'
                     '</items>')

        target = self._makeOne()
        cart = testing.DummyResource(items=[])
        target.visit_items(xml, cart)

        self.assertEqual(len(cart.items), 3)


    def test_visit_cart(self):
        import xml.etree.ElementTree as et
        xml = et.XML('<cart>'
                     '<cartConfirmationId>this-is-info-id</cartConfirmationId>'
                     '<orderCartId>this-is-cart-id</orderCartId>'
                     '<orderItemsTotalFee>1123</orderItemsTotalFee>'
                     '<items>'
                     '<item />'
                     '<item />'
                     '<item />'
                     '</items>'
                      '</cart>'
            )
        
        target = self._makeOne()
        cart_confirm = testing.DummyResource(carts=[])
        target.visit_cart(xml, cart_confirm)

        cart = cart_confirm.carts[0]

        self.assertEqual(cart.cartConfirmationId, 'this-is-info-id')
        self.assertEqual(cart.orderCartId, 'this-is-cart-id')
        self.assertEqual(cart.orderItemsTotalFee, 1123)
        self.assertEqual(len(cart.items), 3)


    def test_visit_carts(self):
        import xml.etree.ElementTree as et
        xml = et.XML('<carts>'
                     '<cart />'
                     '</carts>')

        context = testing.DummyResource(carts=[])

        target = self._makeOne()
        target.visit_carts(xml, context)
        
        self.assertEqual(len(context.carts), 1)

    def test_visit_cartConfirmationRequest(self):
        import xml.etree.ElementTree as et
        xml = et.XML('<cartConfirmationRequest>'
                     '<openId>http://example.com/user</openId>'
                     '<carts>'
                     '<cart/>'
                     '<cart/>'
                     '</carts>'
                     '<isTMode>1</isTMode>'
                     '</cartConfirmationRequest>')
        
        target = self._makeOne()
        result = target.visit_cartConfirmationRequest(xml)
        
        self.assertEqual(result.openid, 'http://example.com/user')
        self.assertEqual(len(result.carts), 2)
        self.assertEqual(result.isTMode, '1')


    def test_it(self):
        import xml.etree.ElementTree as et
        xml = et.XML("""<?xml version="1.0" encoding="UTF-8"?>
<cartConfirmationRequest>
<openId>https://myid.rakuten.co.jp/openid/user/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx</openId>
<carts>
<cart>
<cartConfirmationId>10000000000-20111201000000-01</cartConfirmationId>
<orderCartId>ABCXYZ</orderCartId>
<orderItemsTotalFee>5000</orderItemsTotalFee>
<items>
<item>
<itemId>product1</itemId>
<itemName>テスト用商品 1</itemName>
<itemNumbers>1</itemNumbers>
<itemFee>1000</itemFee>
</item>
<item>
<itemId> product2</itemId>
<itemName>テスト用商品 2</itemName>
<itemNumbers>2</itemNumbers>
<itemFee>2000</itemFee>
</item>
</items>
</cart>
</carts>
<isTMode>0</isTMode>
</cartConfirmationRequest>""")


        target = self._makeOne()
        result = target.visit(xml)

        self.assertEqual(result.openid, 'https://myid.rakuten.co.jp/openid/user/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        self.assertEqual(len(result.carts), 1)
        cart = result.carts[0]
        self.assertEqual(cart.cartConfirmationId, '10000000000-20111201000000-01')
        self.assertEqual(cart.orderCartId, 'ABCXYZ')
        self.assertEqual(cart.orderItemsTotalFee, 5000)
        self.assertEqual(len(cart.items), 2)
        item1 = cart.items[0]
        self.assertEqual(item1.itemId, 'product1')
        self.assertEqual(item1.itemName, u'テスト用商品 1')
        self.assertEqual(item1.itemNumbers, 1)
        self.assertEqual(item1.itemFee, 1000)
        item2 = cart.items[1]
        self.assertEqual(item2.itemId, 'product2')
        self.assertEqual(item2.itemName, u'テスト用商品 2')
        self.assertEqual(item2.itemNumbers, 2)
        self.assertEqual(item2.itemFee, 2000)
        self.assertEqual(result.isTMode, '0')

class IncludeMe(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, config):
        from . import includeme
        return includeme(config)

    def test_it_with_sha1(self):
        from .interfaces import ISigner
        self.config.registry.settings.update(
            {
                'altair_checkout.secret': 'this-is-secret',
                'altair_checkout.authmethod': 'HMAC-SHA1',
                }
            )
        self._callFUT(self.config)

        lookup = self.config.registry.utilities.lookup([], ISigner, "")
        self.assertIsNotNone(lookup)
        self.assertEqual(lookup.hash_algorithm, "SHA1")

        lookup = self.config.registry.utilities.lookup([], ISigner, "HMAC-SHA1")
        self.assertEqual(lookup.hash_algorithm, "SHA1")
        lookup = self.config.registry.utilities.lookup([], ISigner, "HMAC-MD5")
        self.assertEqual(lookup.hash_algorithm, "MD5")

    def test_it_with_md5(self):
        from .interfaces import ISigner
        self.config.registry.settings.update(
            {
                'altair_checkout.secret': 'this-is-secret',
                'altair_checkout.authmethod': 'HMAC-MD5',
                }
            )
        self._callFUT(self.config)

        lookup = self.config.registry.utilities.lookup([], ISigner, "")
        self.assertIsNotNone(lookup)
        self.assertEqual(lookup.hash_algorithm, "MD5")



class ChckoutToXmlTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from .api import checkout_to_xml
        return checkout_to_xml(*args, **kwargs)

    def test_it_no_items(self):
        resource = testing.DummyResource(serviceId='this-is-serviceId',
                                         orderCartId='this-is-cart-id',
                                         orderCompleteUrl='http://example.com/completed',
                                         orderFailedUrl='http://example.com/failed',
                                         authMethod='2',
                                         itemsInfo=[],
                                         isTMode='1')
        result = self._callFUT(resource)

        self.assertEqual(result, 
                         '<orderItemsInfo>'
                         '<serviceId>this-is-serviceId</serviceId>'
                         '<itemsInfo />'
                         '<orderCartId>this-is-cart-id</orderCartId>'
                         '<orderCompleteUrl>http://example.com/completed</orderCompleteUrl>'
                         '<orderFailedUrl>http://example.com/failed</orderFailedUrl>'
                         '<authMethod>2</authMethod>'
                         '<isTMode>1</isTMode>'
                         '</orderItemsInfo>')


    def test_it_with_items(self):
        resource = testing.DummyResource(serviceId='this-is-serviceId',
                                         orderCartId='this-is-cart-id',
                                         orderCompleteUrl='http://example.com/completed',
                                         orderFailedUrl='http://example.com/failed',
                                         authMethod='2',
                                         itemsInfo=[testing.DummyResource(itemId="item-%02d" % i,
                                                                          itemName="item %d" % i,
                                                                          itemNumbers=i,
                                                                          itemFee=100 + i * 10)
                                                    for i in range(2)],
                                         isTMode='1')
        result = self._callFUT(resource)

        self.assertEqual(result, 
                         '<orderItemsInfo>'
                         '<serviceId>this-is-serviceId</serviceId>'
                         '<itemsInfo>'
                         # item 1
                         '<item><itemId>item-00</itemId><itemName>item 0</itemName><itemNumbers>0</itemNumbers><itemFee>100</itemFee></item>'
                         # item 2
                         '<item><itemId>item-01</itemId><itemName>item 1</itemName><itemNumbers>1</itemNumbers><itemFee>110</itemFee></item>'
                         '</itemsInfo>'
                         '<orderCartId>this-is-cart-id</orderCartId>'
                         '<orderCompleteUrl>http://example.com/completed</orderCompleteUrl>'
                         '<orderFailedUrl>http://example.com/failed</orderFailedUrl>'
                         '<authMethod>2</authMethod>'
                         '<isTMode>1</isTMode>'
                         '</orderItemsInfo>')

    def test_it_without_tmode(self):
        resource = testing.DummyResource(serviceId='this-is-serviceId',
                                         orderCartId='this-is-cart-id',
                                         orderCompleteUrl='http://example.com/completed',
                                         orderFailedUrl='http://example.com/failed',
                                         authMethod='2',
                                         isTMode=None,
                                         itemsInfo=[],
                                         )

        result = self._callFUT(resource)

        self.assertEqual(result, 
                         '<orderItemsInfo>'
                         '<serviceId>this-is-serviceId</serviceId>'
                         '<itemsInfo />'
                         '<orderCartId>this-is-cart-id</orderCartId>'
                         '<orderCompleteUrl>http://example.com/completed</orderCompleteUrl>'
                         '<orderFailedUrl>http://example.com/failed</orderFailedUrl>'
                         '<authMethod>2</authMethod>'
                         '</orderItemsInfo>')

    def test_it_without_failed_url(self):
        resource = testing.DummyResource(serviceId='this-is-serviceId',
                                         orderCartId='this-is-cart-id',
                                         orderCompleteUrl='http://example.com/completed',
                                         orderFailedUrl=None,
                                         authMethod='2',
                                         isTMode='1',
                                         itemsInfo=[],
                                         )

        result = self._callFUT(resource)

        self.assertEqual(result, 
                         '<orderItemsInfo>'
                         '<serviceId>this-is-serviceId</serviceId>'
                         '<itemsInfo />'
                         '<orderCartId>this-is-cart-id</orderCartId>'
                         '<orderCompleteUrl>http://example.com/completed</orderCompleteUrl>'
                         '<authMethod>2</authMethod>'
                         '<isTMode>1</isTMode>'
                         '</orderItemsInfo>')
        

        


class TestIt(unittest.TestCase):
    def test_it(self):
        pass
