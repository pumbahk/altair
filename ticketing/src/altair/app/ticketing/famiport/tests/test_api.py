# -*- coding:utf-8 -*-
import unittest
import mock
from .base import FamiPortTestBase

class GetFamiPortOrderTest(unittest.TestCase, FamiPortTestBase):
    def _get_target(self):
        from ..api import get_famiport_order as target
        return target

    def setUp(self):
        FamiPortTestBase.setUp(self)

    def tearDown(self):
        FamiPortTestBase.tearDown(self)

    def test_get_famiport_order(self):
        exp_famiport_order = mock.Mock()
        target = self._get_target()
        session = mock.Mock()
        session.query().filter_by().first.return_value = exp_famiport_order
        order_no = 'XX000012345'
        famiport_order = target(order_no, session)
        self.assertEqual(famiport_order, exp_famiport_order)


# class CreateFamiPortOrderTest(unittest.TestCase, FamiPortTestBase):
#     def _target(self):
#         from ..api import create_famiport_order as target
#         return target
# 
#     def setUp(self):
#         FamiPortTestBase.setUp(self)
# 
#     def tearDown(self):
#         FamiPortTestBase.tearDown(self)
# 
#     def _callFUT(self, *args, **kwds):
#         target = self._target()
#         return target(*args, **kwds)
# 
#     def test_in_payment(self):
#         for order in self.orders:
#             famiport_order = self._callFUT(self.request, order.cart, in_payment=True)
#             self.assertEqual(famiport_order.order_no, order.order_no)
#             self.assert_(famiport_order.barcode_no)
#             self.assertEqual(famiport_order.total_amount, order.total_amount)
#             self.assertEqual(famiport_order.system_fee, order.transaction_fee + order.system_fee + order.special_fee)
#             self.assertEqual(famiport_order.ticketing_fee, order.delivery_fee)
#             self.assertEqual(
#                 famiport_order.ticket_payment,
#                 order.total_amount - (order.system_fee + order.transaction_fee + order.delivery_fee + order.special_fee),
#                 )
#             self.assertEqual(famiport_order.name, order.shipping_address.last_name + order.shipping_address.first_name)
#             self.assertEqual(famiport_order.phone_number, (order.shipping_address.tel_1 or order.shipping_address.tel_2).replace('-', ''))
#             self.assertEqual(famiport_order.koen_date, order.sales_segment.performance.start_on)
#             self.assertEqual(famiport_order.kogyo_name, order.sales_segment.event.title)
#             self.assertEqual(famiport_order.ticket_count, len([item for product in order.items for item in product.items]))
#             self.assertEqual(famiport_order.ticket_total_count, len([item for product in order.items for item in product.items]))
# 
#     def test_not_in_payment(self):
#         for order in self.orders:
#             famiport_order = self._callFUT(self.request, order.cart, in_payment=False)
#             self.assertEqual(famiport_order.order_no, order.order_no)
#             self.assert_(famiport_order.barcode_no)
#             self.assertEqual(famiport_order.total_amount, 0)
#             self.assertEqual(famiport_order.system_fee, 0)
#             self.assertEqual(famiport_order.ticketing_fee, 0)
#             self.assertEqual(famiport_order.ticket_payment, 0)
#             self.assertEqual(famiport_order.name, order.shipping_address.last_name + order.shipping_address.first_name)
#             self.assertEqual(famiport_order.phone_number, (order.shipping_address.tel_1 or order.shipping_address.tel_2).replace('-', ''))
#             self.assertEqual(famiport_order.koen_date, order.sales_segment.performance.start_on)
#             self.assertEqual(famiport_order.kogyo_name, order.sales_segment.event.title)
#             self.assertEqual(famiport_order.ticket_count, len([item for product in order.items for item in product.items]))
#             self.assertEqual(famiport_order.ticket_total_count, len([item for product in order.items for item in product.items]))
