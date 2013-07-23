# -*- coding:utf-8 -*-

import unittest
from pyramid import testing
from altair.app.ticketing.testing import _setup_db, _teardown_db

dependency_modules = [
    'altair.app.ticketing.core.models',
    'altair.app.ticketing.users.models',
    'altair.app.ticketing.cart.models',
    'altair.app.ticketing.lots.models',
]

# class add_wished_product_namesTests(unittest.TestCase):
#     @classmethod
#     def setUpClass(cls):
#         cls.session = _setup_db(modules=dependency_modules, echo=False)

#     @classmethod
#     def tearDownClass(cls):
#         _teardown_db()

#     def setUp(self):
#         self.session.remove()

#     def tearDown(self):
#         import transaction
#         transaction.abort()

#     def _callFUT(self, *args, **kwargs):
#         from .. import helpers
#         return helpers.add_wished_product_names(*args, **kwargs)

#     def _create_products(self, values):
#         from .. import testing
#         return testing._create_products(self.session, values)

#     def test_empty(self):
#         result = self._callFUT([])
#         self.assertEqual(result, [])

#     def _create_performances(self, num=3):
#         from altair.app.ticketing.core.models import DBSession, Performance
#         performances = []
#         for i in range(3):
#             performance =  Performance()
#             DBSession.add(performance)
#             performances.append(performance)
#         return performances

#     def test_many(self):
#         performances = self._create_performances()
        
#         products = self._create_products([
#             {'name': u'商品 A', 'price': 100},
#             {'name': u'商品 B', 'price': 100},
#             {'name': u'商品 C', 'price': 100},
#         ])
        
#         product1 = products[0]
#         product2 = products[1]
#         product3 = products[2]

#         performance1 = performances[0]
#         performance2 = performances[1]
#         performance_id1 = str(performance1.id)
#         performance_id2 = str(performance2.id)

#         wishes = [{"performance_id": performance_id1, 
#                    "wished_products": [{"wish_order": 1, "product_id": '1', "quantity": 10}, 
#                                        {"wish_order": 1, "product_id": '2', "quantity": 5}]}, 
#                   {"performance_id": performance_id2, 
#                    "wished_products": [{"wish_order": 2, "product_id": '3', "quantity": 5}]}]
#         result = self._callFUT(wishes)
#         self.assertEqual(result, 
#             [[{
#                 'product': product1,
#                 'performance': performance1,
#                 'quantity': 10,
#                 'wish_order': 1,
#                 }, 
#             {
#                 'product': product2,
#                 'performance': performance1,
#                 'quantity': 5,
#                 'wish_order': 1,
#                 }], 
#             [{
#                 'product': product3,
#                 'performance': performance2,
#                 'quantity': 5,
#                 'wish_order': 2,
#                 }]])

#     def test_one(self):
#         performances = self._create_performances()
#         products = self._create_products([
#             {'name': u'商品 A', 'price': 100},
#             {'name': u'商品 B', 'price': 100},
#             {'name': u'商品 C', 'price': 100},
#         ])
        
#         performance1 = performances[0]

#         wishes = [{"performance_id": str(performance1.id), "wished_products": [{"wish_order": 1, "product_id": '1', "quantity": 10}]}]
#         result = self._callFUT(wishes)
#         self.assertEqual(result, [[{'wish_order': 1, 'quantity': 10, 'product': products[0], 'performance': performance1}]])

class validate_tokenTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from .. import helpers
        return helpers.validate_token(*args, **kwargs)

    def test_without_session(self):
        request = testing.DummyRequest()
        result = self._callFUT(request)

        self.assertFalse(result)

    def test_without_session_token(self):
        request = testing.DummyRequest(
            session={'lots.entry': {}}
        )
        result = self._callFUT(request)

        self.assertFalse(result)

    def test_without_remote_token(self):
        request = testing.DummyRequest(
            session={'lots.entry': {'token': 'test-token'}}
        )
        result = self._callFUT(request)

        self.assertFalse(result)

    def test_different_tokens(self):
        request = testing.DummyRequest(
            session={'lots.entry': {'token': 'test-token'}},
            params={'token': 'other-token'}
        )
        result = self._callFUT(request)

        self.assertFalse(result)

    def test_it(self):
        request = testing.DummyRequest(
            session={'lots.entry': {'token': 'test-token'}},
            params={'token': 'test-token'}
        )
        result = self._callFUT(request)

        self.assertTrue(result)
        
class convert_wishesTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from .. import helpers
        return helpers.convert_wishes(*args, **kwargs)


    def test_it(self):
        params = {
            "performanceDate-1": "123",
            "performanceDate-2": "124",
            "product-id-1-1": "1000",
            "product-quantity-1-1": "10",
            "product-id-1-2": "1001",
            "product-quantity-1-2": "5",
            "product-id-2-1": "1003",
            "product-quantity-2-1": "5",
        }

        result = self._callFUT(params, 10)
        self.assertEqual(result,
            [{"performance_id": '123', "wished_products": [{'wish_order': 1, 'product_id': '1000', 'quantity': 10}, 
                                                           {'wish_order': 1, 'product_id': '1001', 'quantity': 5}]},
             {"performance_id": '124', "wished_products": [{'wish_order': 2, 'product_id': '1003', 'quantity': 5}]}])

class check_duplicated_productsTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from .. import helpers
        return helpers.check_duplicated_products(*args, **kwargs)

    def test_empty(self):
        result = self._callFUT([])
        self.assertTrue(result)

    def test_one_empty_wishes(self):
        result = self._callFUT([
            {"wished_products": []}
        ])
        self.assertTrue(result)

    def test_one_wishes(self):
        result = self._callFUT([
            {"wished_products": [{"product_id": "p1"}]}
        ])
        self.assertTrue(result)

    def test_two_wishes_without_duplication(self):
        result = self._callFUT([
            {"wished_products": [{"product_id": "p1"}]},
            {"wished_products": [{"product_id": "p2"}]}
        ])
        self.assertTrue(result)

    def test_two_wishes_with_duplication(self):
        result = self._callFUT([
            {"wished_products": [{"product_id": "p1"}]},
            {"wished_products": [{"product_id": "p1"}]}
        ])
        self.assertFalse(result)
