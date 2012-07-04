# -*- coding:utf-8 -*-

""" TBA
"""

import unittest
from pyramid import testing

def _setup_db():
    from sqlalchemy import create_engine
    import sqlahelper
    engine = create_engine('sqlite:///')
    sqlahelper.add_engine(engine)
    session = sqlahelper.get_session()
    import ticketing.models
    import ticketing.core.models
    import ticketing.cart.models
    import ticketing.orders.models
    sqlahelper.get_base().metadata.create_all(bind=session.bind)
    return session

def _teardown_db():
    import sqlahelper
    session = sqlahelper.get_session()
    session.remove()
    sqlahelper.get_base().metadata.drop_all(bind=session.bind)



class set_user_profile_for_orderTests(unittest.TestCase):

    def setUp(self):
        self.session = _setup_db()

    def tearDown(self):
        _teardown_db()

    def _callFUT(self, *args, **kwargs):
        from .api import set_user_profile_for_order
        return set_user_profile_for_order(*args, **kwargs)


    def _add_order(self, product_id):
        from ticketing.core.models import  Product, ProductItem
        from ticketing.orders.models import Order, OrderedProduct
        order = Order(total_amount=0, system_fee=0, transaction_fee=0, delivery_fee=0)
        ordered_product = OrderedProduct(product_id=product_id, order=order, price=0)
        self.session.add(order)
        return order

    def assertAttributes(self, attributes, expected):
        self.assertEqual(len(attributes), len(expected), msg='length %d != %d' % (len(attributes), len(expected)))
        for i, kv in enumerate(expected):
            self.assertEqual(attributes[i].name, kv[0], msg="[OrderedProductAttribute[%d].name] (%s) %s != %s" % (i, kv[0], attributes[i].name, kv[0]))
            self.assertEqual(attributes[i].value, kv[1], msg="[OrderedProductAttribute[%d].value] (%s) %s != %s" % (i, kv[0], attributes[i].value, kv[1]))

    def test_it(self):
        bj89er_user_profile = {
            'cont': '1',
            'member_type': '10',
            u'number': "1",
            u'first_name': u"太郎",
            u'last_name': u"楽天",
            u'first_name_kana': u"たろう",
            u'last_name_kana': u"らくてん",
            u'year': "1980",
            u'month': "01",
            u'day': "02",
            u'sex': "1",
            u'zipcode1': "123",
            u'zipcode2': "4567",
            u'prefecture': u"東京都",
            u'city': u"港区",
            u'address1': u"品川",
            u'address2': u"",
            u'tel1_1': u"123",
            u'tel1_2': u"123",
            u'tel1_3': u"123",
            u'tel2_1': u"123",
            u'tel2_2': u"123",
            u'tel2_3': u"123",
            u'email': u"ticketstar@example.com",
        }
        request = testing.DummyRequest(session=dict(bj89er_user_profile=bj89er_user_profile))
        order = self._add_order(product_id=10)
        self._callFUT(request, order, bj89er_user_profile)

        self.assertAttributes(order.ordered_products[0].attributes,
            sorted([
                (u'cont', '1'),
                (u'member_type', '10'),
                (u'number', "1"),
                (u'first_name', u"太郎"),
                (u'last_name', u"楽天"),
                (u'first_name_kana', u"たろう"),
                (u'last_name_kana', u"らくてん"),
                (u'year', u"1980"),
                (u'month', u"01"),
                (u'day', u"02"),
                (u'sex', u"1"),
                (u'zipcode1', u"123"),
                (u'zipcode2', u"4567"),
                (u'prefecture', u"東京都"),
                (u'city', u"港区"),
                (u'address1', u"品川"),
                (u'address2', u""),
                (u'tel1_1', u"123"),
                (u'tel1_2', u"123"),
                (u'tel1_3', u"123"),
                (u'tel2_1', u"123"),
                (u'tel2_2', u"123"),
                (u'tel2_3', u"123"),
                (u'email', u"ticketstar@example.com"),
            ]))

class Bj89erCartResourceTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.session = _setup_db()

    def tearDown(self):
        _teardown_db()
        testing.tearDown()

    def _getTarget(self):
        from .resources import Bj89erCartResource
        return Bj89erCartResource

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_get_or_create_user(self):
        request = testing.DummyRequest()
        request._cart = testing.DummyModel(id="this-is-cart-id")
        request.registry.settings['89er.event_id'] = '10'
        request.registry.settings['89er.performance_id'] = '100'
        target = self._makeOne(request)
        result = target.get_or_create_user()

        self.assertEqual(result.user_credential[0].membership.name, '89er')
        self.assertEqual(result.user_credential[0].auth_identifier, 'this-is-cart-id')
