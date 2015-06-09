# -*- coding:utf-8 -*-
import unittest
from datetime import datetime
from webob.multidict import MultiDict
from pyramid import testing
from altair.app.ticketing.testing import _setup_db, _teardown_db


class FormMemoAttributeFormTests(unittest.TestCase):
    def _getTarget(self):
        from altair.app.ticketing.orders.forms import OrderMemoEditFormFactory
        return OrderMemoEditFormFactory

    def test_render(self):
        target = self._getTarget()
        N = 3
        form = target(N)()
        for field in form:
            self.assertIn("memo_on_order", field.name)
            self.assertIn(u"補助文言", field.label.text)

    def test_get_errors(self):
        target = self._getTarget()
        N = 3
        form = target(N)(MultiDict({"memo_on_order3": u"あいうえおかきくけこさあいうえおかきくけこさ"}))
        self.assertFalse(form.validate())
        self.assertIn(u"補助文言3(最大20文字):", form.get_error_messages())

    def test_get_result(self):
        target = self._getTarget()
        N = 3
        form = target(N)(MultiDict({"memo_on_order3": u"あいうえおかきくけこ"}))
        self.assertTrue(form.validate())
        result = form.get_result()
        self.assertEquals(len(result), 3)
        self.assertEquals(result[0], ("memo_on_order1", ""))
        self.assertEquals(result[1], ("memo_on_order2", ""))
        self.assertEquals(result[2], ("memo_on_order3", u"あいうえおかきくけこ"))


class OrderRefundFormTests(unittest.TestCase):

    def setUp(self):
        self.session = _setup_db([
            'altair.app.ticketing.core.models',
            'altair.app.ticketing.orders.models',
        ])
        self._add_payment_methods()

    def tearDown(self):
        _teardown_db()

    def _getTarget(self):
        from altair.app.ticketing.orders.forms import OrderRefundForm
        return OrderRefundForm

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _add_payment_methods(self):
        from altair.app.ticketing.core.models import PaymentMethod
        self.session.add(PaymentMethod(
            payment_plugin_id=1,
            name=u'クレジットカード決済',
            fee=100,
        ))
        self.session.add(PaymentMethod(
            payment_plugin_id=2,
            name=u'楽天ID決済',
            fee=200,
        ))
        self.session.add(PaymentMethod(
            payment_plugin_id=3,
            name=u'コンビニ決済',
            fee=300,
        ))
        self.session.add(PaymentMethod(
            payment_plugin_id=4,
            name=u'窓口支払',
            fee=400,
        ))
        self.session.flush()
        return

    def _order(self, payment_plugin_id, delivery_plugin_id, issued_at=datetime(2014, 1, 1), order_no=None):
        from altair.app.ticketing.orders.models import (
            Order,
            OrderedProduct,
            OrderedProductItem,
            PaymentDeliveryMethodPair,
            PaymentMethod,
            DeliveryMethod,
        )
        order = Order(
            order_no=order_no or 'DMY',
            issued_at=issued_at,
            total_amount=180,
            system_fee=0,
            transaction_fee=100,
            delivery_fee=50,
            payment_delivery_pair=PaymentDeliveryMethodPair(
                payment_method=PaymentMethod(
                    payment_plugin_id=payment_plugin_id,
                    fee=100,
                ),
                delivery_method=DeliveryMethod(
                    delivery_plugin_id=delivery_plugin_id,
                    fee_per_order=50,
                    fee_per_principal_ticket=0,
                    fee_per_subticket=0
                ),
                system_fee=0,
                transaction_fee=100,
                delivery_fee_per_order=50,
                delivery_fee_per_principal_ticket=0,
                delivery_fee_per_subticket=0,
                discount=0,
            ),
            items=[OrderedProduct(
                price=30,
                elements=[OrderedProductItem(
                    price=30,
                    issued_at=issued_at
                )]
            )]
        )
        self.session.add(order)
        self.session.flush()
        return order

    def test_validate_payment_method_id_no_orders(self):
        orders = []
        target = self._makeOne(orders=orders)

        field = testing.DummyModel(data=1)
        try:
            target.validate_payment_method_id(field)
            self.assert_(True)
        except:
            self.assert_(False)

    def test_validate_payment_method_id_payment_card_and_refund_card(self):
        orders = [self._order(
            payment_plugin_id=1,
            delivery_plugin_id=1
        )]
        target = self._makeOne(orders=orders)

        field = testing.DummyModel(data=1)
        try:
            target.validate_payment_method_id(field)
            self.assert_(True)
        except:
            self.assert_(False)

    def test_validate_payment_method_id_payment_card_and_refund_bank(self):
        orders = [self._order(
            payment_plugin_id=1,
            delivery_plugin_id=1
        )]
        target = self._makeOne(orders=orders)

        field = testing.DummyModel(data=4)
        try:
            target.validate_payment_method_id(field)
            self.assert_(True)
        except:
            self.assert_(False)

    def test_validate_payment_method_id_payment_checkout_and_refund_checkout(self):
        orders = [self._order(
            payment_plugin_id=2,
            delivery_plugin_id=1
        )]
        target = self._makeOne(orders=orders)

        field = testing.DummyModel(data=2)
        try:
            target.validate_payment_method_id(field)
            self.assert_(True)
        except:
            self.assert_(False)

    def test_validate_payment_method_id_payment_checkout_and_refund_bank(self):
        orders = [self._order(
            payment_plugin_id=2,
            delivery_plugin_id=1
        )]
        target = self._makeOne(orders=orders)

        field = testing.DummyModel(data=4)
        try:
            target.validate_payment_method_id(field)
            self.assert_(True)
        except:
            self.assert_(False)

    def test_validate_payment_method_id_payment_sej_and_refund_sej(self):
        orders = [self._order(
            payment_plugin_id=3,
            delivery_plugin_id=2,
        )]
        target = self._makeOne(orders=orders)

        field = testing.DummyModel(data=3)
        try:
            target.validate_payment_method_id(field)
            self.assert_(True)
        except:
            self.assert_(False)

    def test_validate_payment_method_id_payment_sej_and_refund_bank(self):
        orders = [self._order(
            payment_plugin_id=3,
            delivery_plugin_id=1,
        )]
        target = self._makeOne(orders=orders)

        field = testing.DummyModel(data=4)
        try:
            target.validate_payment_method_id(field)
            self.assert_(True)
        except:
            self.assert_(False)

    def test_validate_payment_method_id_payment_bank_and_refund_bank(self):
        orders = [self._order(
            payment_plugin_id=4,
            delivery_plugin_id=1,
        )]
        target = self._makeOne(orders=orders)

        field = testing.DummyModel(data=4)
        try:
            target.validate_payment_method_id(field)
            self.assert_(True)
        except:
            self.assert_(False)

    def test_validate_payment_method_id_delivery_sej_issued_and_refund_sej(self):
        from wtforms import ValidationError
        orders = [self._order(
            payment_plugin_id=1,
            delivery_plugin_id=2,
        )]
        target = self._makeOne(orders=orders)

        field = testing.DummyModel(data=3)
        try:
            target.validate_payment_method_id(field)
            self.assert_(True)
        except:
            self.assert_(False)

    def test_validate_payment_method_id_delivery_sej_issued_and_refund_other(self):
        from wtforms import ValidationError
        orders = [self._order(
            payment_plugin_id=1,
            delivery_plugin_id=2,
        )]
        target = self._makeOne(orders=orders)

        field = testing.DummyModel(data=1)
        try:
            target.validate_payment_method_id(field)
            self.assert_(False)
        except Exception as e:
            self.assertTrue(isinstance(e, ValidationError))
            self.assertEqual(e.message, u'指定された払戻方法は、この決済引取方法では選択できません: 既にコンビニ発券済なのでコンビニ払戻を選択してください(DMY)')

    def test_validate_payment_method_id_delivery_sej_not_issued_and_refund_other(self):
        from wtforms import ValidationError
        orders = [self._order(
            payment_plugin_id=1,
            delivery_plugin_id=2,
            issued_at=None,
        )]
        target = self._makeOne(orders=orders)

        field = testing.DummyModel(data=1)
        try:
            target.validate_payment_method_id(field)
            self.assert_(True)
        except:
            self.assert_(False)

    def test_validate_payment_method_id_delivery_not_sej_and_refund_sej(self):
        from wtforms import ValidationError
        orders = [self._order(
            payment_plugin_id=2,
            delivery_plugin_id=1,
        )]
        target = self._makeOne(orders=orders)

        field = testing.DummyModel(data=3)
        try:
            target.validate_payment_method_id(field)
            self.assert_(False)
        except Exception as e:
            self.assertTrue(isinstance(e, ValidationError))
            self.assertEqual(e.message, u'指定された払戻方法は、この決済引取方法では選択できません: コンビニ引取ではありません(DMY)')

    def test_validate_payment_method_id_multi_order(self):
        from wtforms import ValidationError
        orders = [
            self._order(
                payment_plugin_id=1,
                delivery_plugin_id=2,
                issued_at=None,
                order_no='DMY1'
            ), self._order(
                payment_plugin_id=1,
                delivery_plugin_id=4,
                issued_at=None,
                order_no='DMY2'
            )
        ]
        target = self._makeOne(orders=orders)

        field = testing.DummyModel(data=1)
        try:
            target.validate_payment_method_id(field)
            self.assert_(True)
        except:
            self.assert_(False)

    def test_validate_payment_method_id_multi_order_sej(self):
        from wtforms import ValidationError
        orders = [
            self._order(
                payment_plugin_id=1,
                delivery_plugin_id=2,
                order_no='DMY1'
            ), self._order(
                payment_plugin_id=3,
                delivery_plugin_id=2,
                order_no='DMY2'
            )
        ]
        target = self._makeOne(orders=orders)

        field = testing.DummyModel(data=3)
        try:
            target.validate_payment_method_id(field)
            self.assert_(True)
        except:
            self.assert_(False)
