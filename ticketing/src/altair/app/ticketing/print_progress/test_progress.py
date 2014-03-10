# -*- coding:utf-8 -*-
import unittest

"""
進捗状況確認のテスト

Order -* OrderedProduct -* OrderedProductItem -* OrderedProductItemToken

tokenの数を数える。

くっつき方
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Order : OrderedProduct : OrderedProductItem : OrderedProductItemToken = 1:1:1:1
- Order(canceled) : OrderedProduct : OrderedProductItem : OrderedProductItemToken = 1:1:1:1
- Order : OrderedProduct : OrderedProductItem : OrderedProductItemToken = 1:2:4:4
- Order : OrderedProduct : OrderedProductItem : OrderedProductItemToken = 1:2:4:8

発券の種類
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- 配送
- QR
- その他

状況
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- 未発券(printed_at=None)
- 発券済み(printed_at!=None)
- 再発券許可時(printed_at < refreshed_at)
- 再発券許可後印刷済み(printed_at > refreshed_at)

券面の種類
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- 通常
- 副券あり
- box席あり
※box席は購入時にSeatGroupを見るだけなので発券枚数をカウントする際は考慮しなくて良い
※副券は関連するTicketがTicketBundleに結びついているだけなので発券枚数をカウントする際は考慮しなくて良い。

todo: 枝番の対応
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

一応
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
- organization別
- performance別
- event別
※"""
from altair.app.ticketing.core.models import (
    Order,
    OrderedProduct,
    OrderedProductItem,
    OrderedProductItemToken,
    PaymentDeliveryMethodPair,
    PaymentMethod,
    DeliveryMethod
)
from altair.app.ticketing.payments import plugins
from datetime import datetime

def setUpModule():
    from altair.app.ticketing.testing import _setup_db
    _setup_db(["altair.app.ticketing.core.models"])

def  _teardown_db():
    from altair.app.ticketing.testing import _teardown_db
    _teardown_db()

class FixtureFactory(object):
    organization_id = 1
    def __init__(self, organization_id=organization_id):
        self.organization_id = organization_id

    def order(self, pdmp=None, performance_id=None):
        return Order(organization_id=self.organization_id, 
                     payment_delivery_pair=pdmp, 
                     performance_id=performance_id, 

                     total_amount=600, 
                     system_fee=100, 
                     transaction_fee=200, 
                     delivery_fee=300, 
                     special_fee=400, 
                )
    def ordered_product(self, order):
        return OrderedProduct(order=order, price=1000)

    def ordered_product_item(self, ordered_product):
        return OrderedProductItem(ordered_product=ordered_product, price=1000)

    def ordered_product_item_token(self, ordered_product_item, printed_at=None):
        return OrderedProductItemToken(item=ordered_product_item, serial="", printed_at=printed_at)

    def payment_delivery_method_pair(self, payment_plugin_id, delivery_plugin_id):
        payment_method = PaymentMethod(payment_plugin_id=payment_plugin_id, 
                                       fee=300, 
                                       fee_type=1, 
                                   )
        delivery_method = DeliveryMethod(delivery_plugin_id=delivery_plugin_id, 
                                         fee=300, 
                                         fee_type=1, 
                                     )
        return PaymentDeliveryMethodPair(
            system_fee=100, 
            transaction_fee=200, 
            delivery_fee=300, 
            discount=0, 
            payment_method=payment_method, 
            delivery_method=delivery_method
        )


class PerformancePrintProgressTests(unittest.TestCase):
    """qr, sej, shipping 1枚ずつ。"""
    def tearDown(self):
        import transaction
        transaction.abort()

    def _getTarget(self):
        from altair.app.ticketing.print_progress.progress import PerformancePrintProgress
        return PerformancePrintProgress

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    order_id = 1
    performance_id = 1111

    def _create_fixture_1111(self):
        """Order : OrderedProduct : OrderedProductItem : OrderedProductItemToken = 1:1:1:1"""
        from altair.app.ticketing.models import DBSession as session
        fixture = FixtureFactory(self.order_id)
        qr_pdmp = fixture.payment_delivery_method_pair(
            plugins.MULTICHECKOUT_PAYMENT_PLUGIN_ID, 
            plugins.QR_DELIVERY_PLUGIN_ID
        )
        sej_pdmp = fixture.payment_delivery_method_pair(
            plugins.MULTICHECKOUT_PAYMENT_PLUGIN_ID, 
            plugins.SEJ_DELIVERY_PLUGIN_ID
        )
        shipping_pdmp = fixture.payment_delivery_method_pair(
            plugins.MULTICHECKOUT_PAYMENT_PLUGIN_ID, 
            plugins.SHIPPING_DELIVERY_PLUGIN_ID
        )

        session.add(fixture.ordered_product_item_token(
            fixture.ordered_product_item(
                fixture.ordered_product(
                    fixture.order(pdmp=qr_pdmp, performance_id=self.performance_id)))))
        session.add(fixture.ordered_product_item_token(
            fixture.ordered_product_item(
                fixture.ordered_product(
                    fixture.order(pdmp=sej_pdmp, performance_id=self.performance_id)))))
        session.add(fixture.ordered_product_item_token(
            fixture.ordered_product_item(
                fixture.ordered_product(
                    fixture.order(pdmp=shipping_pdmp, performance_id=self.performance_id)))))

    def _create_fixture_1244(self):
        """Order : OrderedProduct : OrderedProductItem : OrderedProductItemToken = 1:2:4:4"""
        from altair.app.ticketing.models import DBSession as session
        fixture = FixtureFactory(self.order_id)
        qr_pdmp = fixture.payment_delivery_method_pair(
            plugins.MULTICHECKOUT_PAYMENT_PLUGIN_ID, 
            plugins.QR_DELIVERY_PLUGIN_ID
        )
        sej_pdmp = fixture.payment_delivery_method_pair(
            plugins.MULTICHECKOUT_PAYMENT_PLUGIN_ID, 
            plugins.SEJ_DELIVERY_PLUGIN_ID
        )
        shipping_pdmp = fixture.payment_delivery_method_pair(
            plugins.MULTICHECKOUT_PAYMENT_PLUGIN_ID, 
            plugins.SHIPPING_DELIVERY_PLUGIN_ID
        )

        qr_order = fixture.order(pdmp=qr_pdmp, performance_id=self.performance_id)
        qr_ordered_product0 = fixture.ordered_product(qr_order)
        qr_ordered_product1 = fixture.ordered_product(qr_order)

        qr_ordered_product_item00 = fixture.ordered_product_item(qr_ordered_product0)
        qr_ordered_product_item01 = fixture.ordered_product_item(qr_ordered_product0)
        qr_ordered_product_item10 = fixture.ordered_product_item(qr_ordered_product1)
        qr_ordered_product_item11 = fixture.ordered_product_item(qr_ordered_product1)

        session.add(fixture.ordered_product_item_token(qr_ordered_product_item00))
        session.add(fixture.ordered_product_item_token(qr_ordered_product_item01))
        session.add(fixture.ordered_product_item_token(qr_ordered_product_item10))
        session.add(fixture.ordered_product_item_token(qr_ordered_product_item11))

        sej_order = fixture.order(pdmp=sej_pdmp, performance_id=self.performance_id)
        sej_ordered_product0 = fixture.ordered_product(sej_order)
        sej_ordered_product1 = fixture.ordered_product(sej_order)

        sej_ordered_product_item00 = fixture.ordered_product_item(sej_ordered_product0)
        sej_ordered_product_item01 = fixture.ordered_product_item(sej_ordered_product0)
        sej_ordered_product_item10 = fixture.ordered_product_item(sej_ordered_product1)
        sej_ordered_product_item11 = fixture.ordered_product_item(sej_ordered_product1)

        session.add(fixture.ordered_product_item_token(sej_ordered_product_item00))
        session.add(fixture.ordered_product_item_token(sej_ordered_product_item01))
        session.add(fixture.ordered_product_item_token(sej_ordered_product_item10))
        session.add(fixture.ordered_product_item_token(sej_ordered_product_item11))

        shipping_order = fixture.order(pdmp=shipping_pdmp, performance_id=self.performance_id)
        shipping_ordered_product0 = fixture.ordered_product(shipping_order)
        shipping_ordered_product1 = fixture.ordered_product(shipping_order)

        shipping_ordered_product_item00 = fixture.ordered_product_item(shipping_ordered_product0)
        shipping_ordered_product_item01 = fixture.ordered_product_item(shipping_ordered_product0)
        shipping_ordered_product_item10 = fixture.ordered_product_item(shipping_ordered_product1)
        shipping_ordered_product_item11 = fixture.ordered_product_item(shipping_ordered_product1)

        session.add(fixture.ordered_product_item_token(shipping_ordered_product_item00))
        session.add(fixture.ordered_product_item_token(shipping_ordered_product_item01))
        session.add(fixture.ordered_product_item_token(shipping_ordered_product_item10))
        session.add(fixture.ordered_product_item_token(shipping_ordered_product_item11))

    def _create_fixture_1248(self):
        """Order : OrderedProduct : OrderedProductItem : OrderedProductItemToken = 1:2:4:8"""
        from altair.app.ticketing.models import DBSession as session
        fixture = FixtureFactory(self.order_id)
        qr_pdmp = fixture.payment_delivery_method_pair(
            plugins.MULTICHECKOUT_PAYMENT_PLUGIN_ID, 
            plugins.QR_DELIVERY_PLUGIN_ID
        )
        sej_pdmp = fixture.payment_delivery_method_pair(
            plugins.MULTICHECKOUT_PAYMENT_PLUGIN_ID, 
            plugins.SEJ_DELIVERY_PLUGIN_ID
        )
        shipping_pdmp = fixture.payment_delivery_method_pair(
            plugins.MULTICHECKOUT_PAYMENT_PLUGIN_ID, 
            plugins.SHIPPING_DELIVERY_PLUGIN_ID
        )

        qr_order = fixture.order(pdmp=qr_pdmp, performance_id=self.performance_id)
        qr_ordered_product0 = fixture.ordered_product(qr_order)
        qr_ordered_product1 = fixture.ordered_product(qr_order)

        qr_ordered_product_item00 = fixture.ordered_product_item(qr_ordered_product0)
        qr_ordered_product_item01 = fixture.ordered_product_item(qr_ordered_product0)
        qr_ordered_product_item10 = fixture.ordered_product_item(qr_ordered_product1)
        qr_ordered_product_item11 = fixture.ordered_product_item(qr_ordered_product1)

        session.add(fixture.ordered_product_item_token(qr_ordered_product_item00))
        session.add(fixture.ordered_product_item_token(qr_ordered_product_item01))
        session.add(fixture.ordered_product_item_token(qr_ordered_product_item10))
        session.add(fixture.ordered_product_item_token(qr_ordered_product_item11))
        session.add(fixture.ordered_product_item_token(qr_ordered_product_item00, printed_at=datetime(2000, 1, 1)))
        session.add(fixture.ordered_product_item_token(qr_ordered_product_item01, printed_at=datetime(2000, 1, 1)))
        session.add(fixture.ordered_product_item_token(qr_ordered_product_item10, printed_at=datetime(2000, 1, 1)))
        session.add(fixture.ordered_product_item_token(qr_ordered_product_item11, printed_at=datetime(2000, 1, 1)))

        sej_order = fixture.order(pdmp=sej_pdmp, performance_id=self.performance_id)
        sej_ordered_product0 = fixture.ordered_product(sej_order)
        sej_ordered_product1 = fixture.ordered_product(sej_order)

        sej_ordered_product_item00 = fixture.ordered_product_item(sej_ordered_product0)
        sej_ordered_product_item01 = fixture.ordered_product_item(sej_ordered_product0)
        sej_ordered_product_item10 = fixture.ordered_product_item(sej_ordered_product1)
        sej_ordered_product_item11 = fixture.ordered_product_item(sej_ordered_product1)

        session.add(fixture.ordered_product_item_token(sej_ordered_product_item00))
        session.add(fixture.ordered_product_item_token(sej_ordered_product_item01))
        session.add(fixture.ordered_product_item_token(sej_ordered_product_item10))
        session.add(fixture.ordered_product_item_token(sej_ordered_product_item11))
        session.add(fixture.ordered_product_item_token(sej_ordered_product_item00, printed_at=datetime(2000, 1, 1)))
        session.add(fixture.ordered_product_item_token(sej_ordered_product_item01, printed_at=datetime(2000, 1, 1)))
        session.add(fixture.ordered_product_item_token(sej_ordered_product_item10, printed_at=datetime(2000, 1, 1)))
        session.add(fixture.ordered_product_item_token(sej_ordered_product_item11, printed_at=datetime(2000, 1, 1)))

        shipping_order = fixture.order(pdmp=shipping_pdmp, performance_id=self.performance_id)
        shipping_ordered_product0 = fixture.ordered_product(shipping_order)
        shipping_ordered_product1 = fixture.ordered_product(shipping_order)

        shipping_ordered_product_item00 = fixture.ordered_product_item(shipping_ordered_product0)
        shipping_ordered_product_item01 = fixture.ordered_product_item(shipping_ordered_product0)
        shipping_ordered_product_item10 = fixture.ordered_product_item(shipping_ordered_product1)
        shipping_ordered_product_item11 = fixture.ordered_product_item(shipping_ordered_product1)

        session.add(fixture.ordered_product_item_token(shipping_ordered_product_item00))
        session.add(fixture.ordered_product_item_token(shipping_ordered_product_item01))
        session.add(fixture.ordered_product_item_token(shipping_ordered_product_item10))
        session.add(fixture.ordered_product_item_token(shipping_ordered_product_item11))
        session.add(fixture.ordered_product_item_token(shipping_ordered_product_item00, printed_at=datetime(2000, 1, 1)))
        session.add(fixture.ordered_product_item_token(shipping_ordered_product_item01, printed_at=datetime(2000, 1, 1)))
        session.add(fixture.ordered_product_item_token(shipping_ordered_product_item10, printed_at=datetime(2000, 1, 1)))
        session.add(fixture.ordered_product_item_token(shipping_ordered_product_item11, printed_at=datetime(2000, 1, 1)))


    def _create_shipping_ordered_product_item_token(self):
        fixture = FixtureFactory(self.order_id)
        shipping_pdmp = fixture.payment_delivery_method_pair(
            plugins.MULTICHECKOUT_PAYMENT_PLUGIN_ID, 
            plugins.SHIPPING_DELIVERY_PLUGIN_ID
        )
        return fixture.ordered_product_item_token(
            fixture.ordered_product_item(
                fixture.ordered_product(
                    fixture.order(pdmp=shipping_pdmp, performance_id=self.performance_id))))


    def test_unprinted_shipping(self):
        """未発券(printed_at=None)"""
        from altair.app.ticketing.models import DBSession as session
        token = self._create_shipping_ordered_product_item_token()
        token.printed_at = None
        session.add(token)

        assert self.performance_id == 1111
        target = self._makeOne(1111)
        self.assertEqual(target.total, 1)
        self.assertEqual(target.shipping.total, 1)
        self.assertEqual(target.shipping.unprinted, 1)
        self.assertEqual(target.shipping.printed, 0)

    def test_printed_shipping(self):
        """発券済み(printed_at!=None)"""
        from altair.app.ticketing.models import DBSession as session
        token = self._create_shipping_ordered_product_item_token()
        token.printed_at = datetime(2000, 1, 1)
        session.add(token)

        assert self.performance_id == 1111
        target = self._makeOne(1111)
        self.assertEqual(target.total, 1)
        self.assertEqual(target.shipping.total, 1)
        self.assertEqual(target.shipping.unprinted, 0)
        self.assertEqual(target.shipping.printed, 1)

    def test_refreshed_shipping(self):
        """再発券許可時(printed_at < refreshed_at)"""
        from altair.app.ticketing.models import DBSession as session
        token = self._create_shipping_ordered_product_item_token()
        token.printed_at = datetime(2000, 1, 1)
        token.refreshed_at = datetime(2001, 1, 1)
        session.add(token)

        assert self.performance_id == 1111
        target = self._makeOne(1111)
        self.assertEqual(target.total, 1)
        self.assertEqual(target.shipping.total, 1)
        self.assertEqual(target.shipping.unprinted, 1)
        self.assertEqual(target.shipping.printed, 0)

    def test_printed_after_refreshed_shipping(self):
        """再発券許可後印刷済み(printed_at > refreshed_at)"""
        from altair.app.ticketing.models import DBSession as session
        token = self._create_shipping_ordered_product_item_token()
        token.printed_at = datetime(2002, 1, 1)
        token.refreshed_at = datetime(2001, 1, 1)
        session.add(token)

        assert self.performance_id == 1111
        target = self._makeOne(1111)
        self.assertEqual(target.total, 1)
        self.assertEqual(target.shipping.total, 1)
        self.assertEqual(target.shipping.unprinted, 0)
        self.assertEqual(target.shipping.printed, 1)

    def test_it_matched_performance_exists(self):
        self._create_fixture_1111()

        assert self.performance_id == 1111
        target = self._makeOne(1111)

        self.assertEqual(target.total, 3)
        self.assertEqual(target.qr.total, 1)
        self.assertEqual(target.qr.printed, 0)
        self.assertEqual(target.qr.unprinted, 1)
        self.assertEqual(target.shipping.total, 1)
        self.assertEqual(target.shipping.printed, 0)
        self.assertEqual(target.shipping.unprinted, 1)
        self.assertEqual(target.other.total, 1)
        self.assertEqual(target.other.printed, 0)
        self.assertEqual(target.other.unprinted, 1)

    def test_it_matched_performance_notfound(self):
        self._create_fixture_1111()

        assert self.performance_id != 2222
        target = self._makeOne(2222)

        self.assertEqual(target.total, 0)
        self.assertEqual(target.qr.total, 0)
        self.assertEqual(target.qr.printed, 0)
        self.assertEqual(target.qr.unprinted, 0)
        self.assertEqual(target.shipping.total, 0)
        self.assertEqual(target.shipping.printed, 0)
        self.assertEqual(target.shipping.unprinted, 0)
        self.assertEqual(target.other.total, 0)
        self.assertEqual(target.other.printed, 0)
        self.assertEqual(target.other.unprinted, 0)

    def test_it_order_is_canceled(self):
        from altair.app.ticketing.models import DBSession as session
        self._create_fixture_1111()

        ### cancel
        for ob in session.new:
            if isinstance(ob, Order):
                ob.canceled_at = datetime(2000, 1, 1)

        assert self.performance_id == 1111
        target = self._makeOne(1111)

        self.assertEqual(target.total, 0)
        self.assertEqual(target.qr.total, 0)
        self.assertEqual(target.qr.printed, 0)
        self.assertEqual(target.qr.unprinted, 0)
        self.assertEqual(target.shipping.total, 0)
        self.assertEqual(target.shipping.printed, 0)
        self.assertEqual(target.shipping.unprinted, 0)
        self.assertEqual(target.other.total, 0)
        self.assertEqual(target.other.printed, 0)
        self.assertEqual(target.other.unprinted, 0)

    def test_it_1244(self):
        """Order : OrderedProduct : OrderedProductItem : OrderedProductItemToken = 1:2:4:4"""
        self._create_fixture_1244()

        assert self.performance_id == 1111
        target = self._makeOne(1111)

        self.assertEqual(target.total, 12)
        self.assertEqual(target.qr.total, 4)
        self.assertEqual(target.qr.printed, 0)
        self.assertEqual(target.qr.unprinted, 4)
        self.assertEqual(target.shipping.total, 4)
        self.assertEqual(target.shipping.printed, 0)
        self.assertEqual(target.shipping.unprinted, 4)
        self.assertEqual(target.other.total, 4)
        self.assertEqual(target.other.printed, 0)
        self.assertEqual(target.other.unprinted, 4)

    def test_it_1248(self):
        """Order : OrderedProduct : OrderedProductItem : OrderedProductItemToken = 1:2:4:8"""
        self._create_fixture_1248()

        assert self.performance_id == 1111
        target = self._makeOne(1111)

        self.assertEqual(target.total, 24)
        self.assertEqual(target.qr.total, 8)
        self.assertEqual(target.qr.printed, 4)
        self.assertEqual(target.qr.unprinted, 4)
        self.assertEqual(target.shipping.total, 8)
        self.assertEqual(target.shipping.printed, 4)
        self.assertEqual(target.shipping.unprinted, 4)
        self.assertEqual(target.other.total, 8)
        self.assertEqual(target.other.printed, 4)
        self.assertEqual(target.other.unprinted, 4)

class EventPrintProgressTests(unittest.TestCase):
    pass
