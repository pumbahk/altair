# -*- coding:utf-8 -*-

import unittest
from pyramid import testing
from altair.app.ticketing.testing import DummyRequest, SetUpTearDownManager
"""
traverser 無視して良いのでは
git revert aa554213 でチェック
viewletのテストで良いだろう。
これで対応できるのは各pluginの表示の所のみ
"""
from altair.app.ticketing.testing import _setup_db, _teardown_db
def setUpModule():
    _setup_db(['altair.app.ticketing.core.models',
               'altair.app.ticketing.lots.models'])

def tearDownModule():
    _teardown_db()


class PluginViewletTestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = testing.setUp(settings={"altair.mailer": "pyramid_mailer.testing", "altair.sej.template_file": ""})
        cls.config.include('pyramid_mako')
        cls.config.include('altair.pyramid_dynamic_renderer')
        cls.config.add_mako_renderer('.html')
        cls.config.add_mako_renderer('.txt')
        cls.config.include('altair.app.ticketing.mails.install_mail_utility')
        cls.config.include('altair.app.ticketing.payments')
        cls.config.include('altair.app.ticketing.payments.plugins')

    @classmethod
    def tearDownClass(cls):
        testing.tearDown()

    def setUp(self):
        from mock import patch
        self._patch_get_cart_setting_from_order_like = patch('altair.app.ticketing.cart.api.get_cart_setting_from_order_like')
        p = self._patch_get_cart_setting_from_order_like.start()
        p.return_value.type = 'standard'

    def tearDown(self):
        self._patch_get_cart_setting_from_order_like.stop()

    def register_fake_storedata(self, data):
        from zope.interface import provider
        from .interfaces import IMailDataStoreGetter
        @provider(IMailDataStoreGetter)
        def get_data(request, order, mtype):
            return data
        self.config.registry.registerUtility(get_data, IMailDataStoreGetter)



"""
失敗した時にはexceptionが出てくれる？
"""
def _make_request(context_factory, *args, **kwargs):
    from mock import Mock
    request = DummyRequest()
    request.context = context_factory(request, *args, **kwargs)
    return request

def _make_order_for_delivery(self, delivery_plugin_id, total_amount=10000):
    from altair.app.ticketing.core.models import (
        PaymentDeliveryMethodPair, 
        DeliveryMethod, 
        ShippingAddress
    )
    from altair.app.ticketing.orders.models import (
        Order,
        )
    delivery_method = DeliveryMethod(delivery_plugin_id=delivery_plugin_id)
    pdmp = PaymentDeliveryMethodPair(delivery_method=delivery_method)
    shipping_address = ShippingAddress() #xxx:
    return Order(payment_delivery_pair=pdmp, 
                 shipping_address=shipping_address, 
                 total_amount=total_amount
    )

def _make_lot_entry_for_delivery(self, delivery_plugin_id):
    from altair.app.ticketing.lots.models import LotEntry
    from altair.app.ticketing.orders.models import Order
    from altair.app.ticketing.core.models import (
        PaymentDeliveryMethodPair, 
        DeliveryMethod, 
        ShippingAddress
    )
    delivery_method = DeliveryMethod(delivery_plugin_id=delivery_plugin_id)
    pdmp = PaymentDeliveryMethodPair(delivery_method=delivery_method)
    shipping_address = ShippingAddress() #xxx:
    return LotEntry(
        payment_delivery_method_pair=pdmp,
        shipping_address=shipping_address,
        order=Order(
            payment_delivery_pair=pdmp,
            shipping_address=shipping_address
            )
        )

def _make_order_for_payment(self, payment_plugin_id, total_amount=10000):
    from altair.app.ticketing.core.models import (
        PaymentDeliveryMethodPair, 
        PaymentMethod, 
        DeliveryMethod, 
        ShippingAddress
    )
    from altair.app.ticketing.orders.models import Order
    from altair.app.ticketing.payments.plugins import SEJ_DELIVERY_PLUGIN_ID
    payment_method = PaymentMethod(payment_plugin_id=payment_plugin_id)
    delivery_method = DeliveryMethod(delivery_plugin_id=SEJ_DELIVERY_PLUGIN_ID)
    pdmp = PaymentDeliveryMethodPair(payment_method=payment_method, delivery_method=delivery_method)
    shipping_address = ShippingAddress() #xxx:
    return Order(payment_delivery_pair=pdmp,
                 shipping_address=shipping_address, 
                 total_amount=total_amount)

def _make_lot_entry_for_payment(self, payment_plugin_id):
    from altair.app.ticketing.lots.models import LotEntry
    from altair.app.ticketing.orders.models import Order
    from altair.app.ticketing.core.models import (
        PaymentDeliveryMethodPair, 
        PaymentMethod, 
        DeliveryMethod,
        ShippingAddress
    )
    from altair.app.ticketing.payments.plugins import SEJ_DELIVERY_PLUGIN_ID
    payment_method = PaymentMethod(payment_plugin_id=payment_plugin_id)
    delivery_method = DeliveryMethod(delivery_plugin_id=SEJ_DELIVERY_PLUGIN_ID)
    pdmp = PaymentDeliveryMethodPair(payment_method=payment_method, delivery_method=delivery_method)
    shipping_address = ShippingAddress() #xxx:
    return LotEntry(
        payment_delivery_method_pair=pdmp,
        shipping_address=shipping_address,
        order=Order(
            payment_delivery_pair=pdmp,
            shipping_address=shipping_address
            )
        )

class DeliveryFinishedViewletTest(PluginViewletTestBase):
    _make_subject = _make_order_for_delivery
    def _getTarget(self):
        from .helpers import render_delivery_finished_mail_viewlet
        return render_delivery_finished_mail_viewlet

    def _make_request(self, subject):
        from .complete import PurchaseCompleteMailResource
        return _make_request(PurchaseCompleteMailResource, subject)

    def test_shipping(self):
        from altair.app.ticketing.payments import plugins
        k = plugins.SHIPPING_DELIVERY_PLUGIN_ID
        subject = self._make_subject(k)

        data = {"D{}notice".format(k): "*notice*"}
        self.register_fake_storedata(data)

        request = self._make_request(subject)
        result = self._getTarget()(request)
        self.assertIn("*notice*", result)

    def test_sej(self):
        from altair.app.ticketing.models import DBSession
        order_no = "SEJ:TEST:DEMO"

        def setup():
            DBSession.add(SejOrder(order_no=order_no))

        def teardown():
            import transaction
            transaction.abort()

        from altair.app.ticketing.payments import plugins
        from altair.app.ticketing.sej.models import SejOrder
        k = plugins.SEJ_DELIVERY_PLUGIN_ID

        with SetUpTearDownManager(setup=setup, teardown=teardown):
            data = {"D{}notice".format(k): "*notice*"}
            self.register_fake_storedata(data)

            subject = self._make_subject(k)
            subject.order_no = order_no
            from altair.app.ticketing.core.models import PaymentMethod
            k = plugins.SEJ_PAYMENT_PLUGIN_ID
            subject.payment_delivery_pair.payment_method = PaymentMethod(payment_plugin_id=k)

            request = self._make_request(subject)
            result = self._getTarget()(request)
            self.assertIn("*notice*", result)

    def test_reserve_number(self):
        from altair.app.ticketing.payments import plugins
        k = plugins.RESERVE_NUMBER_DELIVERY_PLUGIN_ID
        subject = self._make_subject(k)

        data = {"D{}notice".format(k): "*notice*"}
        self.register_fake_storedata(data)

        request = self._make_request(subject)
        result = self._getTarget()(request)
        self.assertIn("*notice*", result)

    def test_qr(self):
        from altair.app.ticketing.payments import plugins
        k = plugins.QR_DELIVERY_PLUGIN_ID
        subject = self._make_subject(k)

        data = {"D{}notice".format(k): "*notice*"}
        self.register_fake_storedata(data)

        request = self._make_request(subject)
        result = self._getTarget()(request)
        self.assertIn("*notice*", result)

class DeliveryCancelViewletTest(PluginViewletTestBase):
    _make_subject = _make_order_for_delivery

    def _make_request(self, subject):
        from .order_cancel import OrderCancelMailResource
        return _make_request(OrderCancelMailResource, subject)

    def _getTarget(self):
        from .helpers import render_delivery_cancel_mail_viewlet
        return render_delivery_cancel_mail_viewlet

    def test_shipping(self):
        from altair.app.ticketing.payments import plugins
        k = plugins.SHIPPING_DELIVERY_PLUGIN_ID
        subject = self._make_subject(k)

        data = {"D{}notice".format(k): "*notice*"}
        self.register_fake_storedata(data)

        request = self._make_request(subject)
        result = self._getTarget()(request)
        self.assertIn("*notice*", result)

    def test_sej(self):
        from altair.app.ticketing.models import DBSession
        order_no = "SEJ:TEST:DEMO"

        def setup():
            DBSession.add(SejOrder(order_no=order_no))

        def teardown():
            import transaction
            transaction.abort()

        from altair.app.ticketing.payments import plugins
        from altair.app.ticketing.sej.models import SejOrder
        k = plugins.SEJ_DELIVERY_PLUGIN_ID

        with SetUpTearDownManager(setup=setup, teardown=teardown):
            data = {"D{}notice".format(k): "*notice*"}
            self.register_fake_storedata(data)

            subject = self._make_subject(k)
            subject.order_no = order_no

            request = self._make_request(subject)
            result = self._getTarget()(request)
            self.assertIn("*notice*", result)

    def test_reserve_number(self):
        from altair.app.ticketing.payments import plugins
        k = plugins.RESERVE_NUMBER_DELIVERY_PLUGIN_ID
        subject = self._make_subject(k)

        data = {"D{}notice".format(k): "*notice*"}
        self.register_fake_storedata(data)

        request = self._make_request(subject)
        result = self._getTarget()(request)
        self.assertIn("*notice*", result)

    def test_qr(self):
        from altair.app.ticketing.payments import plugins
        k = plugins.QR_DELIVERY_PLUGIN_ID
        subject = self._make_subject(k)

        data = {"D{}notice".format(k): "*notice*"}
        self.register_fake_storedata(data)

        request = self._make_request(subject)
        result = self._getTarget()(request)
        self.assertIn("*notice*", result)

class DeliveryLotsAcceptedViewletTest(PluginViewletTestBase):
    def _make_subject(self, delivery_plugin_id):
        return (
            _make_lot_entry_for_delivery(self, delivery_plugin_id),
            None
            )

    def _make_request(self, subject):
        from .lots_mail import LotsAcceptedMailResource
        return _make_request(LotsAcceptedMailResource, subject)

    def _getTarget(self):
        from .helpers import render_delivery_lots_accepted_mail_viewlet
        return render_delivery_lots_accepted_mail_viewlet

    def test_shipping(self):
        from altair.app.ticketing.payments import plugins
        k = plugins.SHIPPING_DELIVERY_PLUGIN_ID
        subject = self._make_subject(k)

        data = {"D{}notice".format(k): "*notice*"}
        self.register_fake_storedata(data)

        request = self._make_request(subject)
        result = self._getTarget()(request)
        self.assertIn("*notice*", result)

    def test_sej(self):## sej order無いはず
        from altair.app.ticketing.payments import plugins
        k = plugins.SEJ_DELIVERY_PLUGIN_ID

        data = {"D{}notice".format(k): "*notice*"}
        self.register_fake_storedata(data)

        subject = self._make_subject(k)

        request = self._make_request(subject)
        result = self._getTarget()(request)
        self.assertIn("*notice*", result)

    def test_reserve_number(self):
        from altair.app.ticketing.payments import plugins
        k = plugins.RESERVE_NUMBER_DELIVERY_PLUGIN_ID
        subject = self._make_subject(k)

        data = {"D{}notice".format(k): "*notice*"}
        self.register_fake_storedata(data)

        request = self._make_request(subject)
        result = self._getTarget()(request)
        self.assertIn("*notice*", result)

    def test_qr(self):
        from altair.app.ticketing.payments import plugins
        k = plugins.QR_DELIVERY_PLUGIN_ID
        subject = self._make_subject(k)

        data = {"D{}notice".format(k): "*notice*"}
        self.register_fake_storedata(data)

        request = self._make_request(subject)
        result = self._getTarget()(request)
        self.assertIn("*notice*", result)

class DeliveryLotsElectedViewletTest(PluginViewletTestBase):
    def _make_subject(self, delivery_plugin_id):
        from mock import Mock
        lot_entry_wish = Mock()
        return (
            _make_lot_entry_for_delivery(self, delivery_plugin_id),
            lot_entry_wish
            )

    def _make_request(self, subject):
        from .lots_mail import LotsElectedMailResource
        return _make_request(LotsElectedMailResource, subject)

    def _getTarget(self):
        from .helpers import render_delivery_lots_elected_mail_viewlet
        return render_delivery_lots_elected_mail_viewlet

    def test_shipping(self):
        from altair.app.ticketing.payments import plugins
        k = plugins.SHIPPING_DELIVERY_PLUGIN_ID
        subject = self._make_subject(k)

        data = {"D{}notice".format(k): "*notice*"}
        self.register_fake_storedata(data)

        request = self._make_request(subject)
        result = self._getTarget()(request)
        self.assertIn("*notice*", result)

    def test_sej(self):
        from altair.app.ticketing.models import DBSession
        order_no = "SEJ:TEST:DEMO"

        def setup():
            DBSession.add(SejOrder(order_no=order_no))
        def teardown():
            import transaction
            transaction.abort()

        from altair.app.ticketing.payments import plugins
        from altair.app.ticketing.sej.models import SejOrder
        k = plugins.SEJ_DELIVERY_PLUGIN_ID

        with SetUpTearDownManager(setup=setup, teardown=teardown):
            data = {"D{}notice".format(k): "*notice*"}
            self.register_fake_storedata(data)

            subject = self._make_subject(k)
            subject[0].order = _make_order_for_delivery(self, k, total_amount=10000)
            from altair.app.ticketing.core.models import PaymentMethod
            k = plugins.MULTICHECKOUT_PAYMENT_PLUGIN_ID #check with sej?
            subject[0].order.payment_delivery_pair.payment_method = PaymentMethod(payment_plugin_id=k)
            subject[0].order.order_no = order_no

            request = self._make_request(subject)
            result = self._getTarget()(request)
            self.assertIn("*notice*", result)

    def test_reserve_number(self):
        from altair.app.ticketing.payments import plugins
        k = plugins.RESERVE_NUMBER_DELIVERY_PLUGIN_ID
        subject = self._make_subject(k)

        data = {"D{}notice".format(k): "*notice*"}
        self.register_fake_storedata(data)

        request = self._make_request(subject)
        result = self._getTarget()(request)
        self.assertIn("*notice*", result)

    def test_qr(self):
        from altair.app.ticketing.payments import plugins
        k = plugins.QR_DELIVERY_PLUGIN_ID
        subject = self._make_subject(k)

        data = {"D{}notice".format(k): "*notice*"}
        self.register_fake_storedata(data)

        request = self._make_request(subject)
        result = self._getTarget()(request)
        self.assertIn("*notice*", result)

class DeliveryLotsRejectedViewletTest(PluginViewletTestBase):
    def _make_subject(self, delivery_plugin_id):
        return (
            _make_lot_entry_for_delivery(self,delivery_plugin_id),
            None
            )


    def _make_request(self, subject):
        from .lots_mail import LotsRejectedMailResource
        return _make_request(LotsRejectedMailResource, subject)

    def _getTarget(self):
        from .helpers import render_delivery_lots_rejected_mail_viewlet
        return render_delivery_lots_rejected_mail_viewlet

    def test_shipping(self):
        from altair.app.ticketing.payments import plugins
        k = plugins.SHIPPING_DELIVERY_PLUGIN_ID
        subject = self._make_subject(k)

        data = {"D{}notice".format(k): "*notice*"}
        self.register_fake_storedata(data)

        request = self._make_request(subject)
        result = self._getTarget()(request)
        self.assertIn("*notice*", result)

    def test_sej(self):## sej order無いはず
        from altair.app.ticketing.payments import plugins
        k = plugins.SEJ_DELIVERY_PLUGIN_ID

        data = {"D{}notice".format(k): "*notice*"}
        self.register_fake_storedata(data)

        subject = self._make_subject(k)

        request = self._make_request(subject)
        result = self._getTarget()(request)
        self.assertIn("*notice*", result)

    def test_reserve_number(self):
        from altair.app.ticketing.payments import plugins
        k = plugins.RESERVE_NUMBER_DELIVERY_PLUGIN_ID
        subject = self._make_subject(k)

        data = {"D{}notice".format(k): "*notice*"}
        self.register_fake_storedata(data)

        request = self._make_request(subject)
        result = self._getTarget()(request)
        self.assertIn("*notice*", result)

    def test_qr(self):
        from altair.app.ticketing.payments import plugins
        k = plugins.QR_DELIVERY_PLUGIN_ID
        subject = self._make_subject(k)

        data = {"D{}notice".format(k): "*notice*"}
        self.register_fake_storedata(data)

        request = self._make_request(subject)
        result = self._getTarget()(request)
        self.assertIn("*notice*", result)

class PaymentFinishedViewletTest(PluginViewletTestBase):
    _make_subject = _make_order_for_payment

    def _make_request(self, subject):
        from .complete import PurchaseCompleteMailResource
        return _make_request(PurchaseCompleteMailResource, subject)

    def _getTarget(self):
        from .helpers import render_payment_finished_mail_viewlet
        return render_payment_finished_mail_viewlet

    def test_multicheckout(self):
        from altair.app.ticketing.payments import plugins
        k = plugins.MULTICHECKOUT_PAYMENT_PLUGIN_ID
        subject = self._make_subject(k, total_amount=10000)

        data = {"P{}notice".format(k): "*notice*"}
        self.register_fake_storedata(data)

        request = self._make_request(subject)
        result = self._getTarget()(request)
        self.assertIn("*notice*", result)
        self.assertIn("10,000", result)

    def test_checkout(self):
        from altair.app.ticketing.payments import plugins
        k = plugins.CHECKOUT_PAYMENT_PLUGIN_ID
        subject = self._make_subject(k, total_amount=10000)

        data = {"P{}notice".format(k): "*notice*"}
        self.register_fake_storedata(data)

        request = self._make_request(subject)
        result = self._getTarget()(request)
        self.assertIn("*notice*", result)
        self.assertIn("10,000", result)

    def test_sej(self):
        from altair.app.ticketing.models import DBSession
        order_no = "SEJ:TEST:DEMO"

        def setup():
            DBSession.add(SejOrder(order_no=order_no))
        def teardown():
            import transaction
            transaction.abort()

        from altair.app.ticketing.payments import plugins
        from altair.app.ticketing.sej.models import SejOrder
        k = plugins.SEJ_PAYMENT_PLUGIN_ID

        with SetUpTearDownManager(setup=setup, teardown=teardown):
            data = {"P{}notice".format(k): "*notice*"}
            self.register_fake_storedata(data)

            subject = self._make_subject(k)
            subject.order_no = order_no

            request = self._make_request(subject)
            result = self._getTarget()(request)
            self.assertIn("*notice*", result)

    def test_reserve_number(self):
        from altair.app.ticketing.payments import plugins
        k = plugins.RESERVE_NUMBER_PAYMENT_PLUGIN_ID
        subject = self._make_subject(k)

        data = {"P{}notice".format(k): "*notice*"}
        self.register_fake_storedata(data)

        request = self._make_request(subject)
        result = self._getTarget()(request)
        self.assertIn("*notice*", result)

class PaymentCancelViewletTest(PluginViewletTestBase):
    _make_subject = _make_order_for_payment

    def _make_request(self, subject):
        from .order_cancel import OrderCancelMailResource
        return _make_request(OrderCancelMailResource, subject)

    def _getTarget(self):
        from .helpers import render_payment_cancel_mail_viewlet
        return render_payment_cancel_mail_viewlet

    def test_multicheckout(self):
        from altair.app.ticketing.payments import plugins
        k = plugins.MULTICHECKOUT_PAYMENT_PLUGIN_ID
        subject = self._make_subject(k, total_amount=10000)

        data = {"P{}notice".format(k): "*notice*"}
        self.register_fake_storedata(data)

        request = self._make_request(subject)
        result = self._getTarget()(request)
        self.assertIn("*notice*", result)
        # self.assertIn("10,000", result)

    def test_checkout(self):
        from altair.app.ticketing.payments import plugins
        k = plugins.CHECKOUT_PAYMENT_PLUGIN_ID
        subject = self._make_subject(k, total_amount=10000)

        data = {"P{}notice".format(k): "*notice*"}
        self.register_fake_storedata(data)

        request = self._make_request(subject)
        result = self._getTarget()(request)
        self.assertIn("*notice*", result)
        # self.assertIn("10,000", result)

    def test_sej(self):
        from altair.app.ticketing.models import DBSession
        order_no = "SEJ:TEST:DEMO"

        def setup():
            DBSession.add(SejOrder(order_no=order_no))
        def teardown():
            import transaction
            transaction.abort()

        from altair.app.ticketing.payments import plugins
        from altair.app.ticketing.sej.models import SejOrder
        k = plugins.SEJ_PAYMENT_PLUGIN_ID

        with SetUpTearDownManager(setup=setup, teardown=teardown):
            data = {"P{}notice".format(k): "*notice*"}
            self.register_fake_storedata(data)

            subject = self._make_subject(k)
            subject.order_no = order_no

            request = self._make_request(subject)
            result = self._getTarget()(request)
            self.assertIn("*notice*", result)

    def test_reserve_number(self):
        from altair.app.ticketing.payments import plugins
        k = plugins.RESERVE_NUMBER_PAYMENT_PLUGIN_ID
        subject = self._make_subject(k)

        data = {"P{}notice".format(k): "*notice*"}
        self.register_fake_storedata(data)

        request = self._make_request(subject)
        result = self._getTarget()(request)
        self.assertIn("*notice*", result)

class PaymentLotsAcceptViewletTest(PluginViewletTestBase):
    def _make_subject(self, payment_plugin_id):
        return (
            _make_lot_entry_for_payment(self, payment_plugin_id),
            None
            )

    def _make_request(self, subject):
        from .lots_mail import LotsAcceptedMailResource
        return _make_request(LotsAcceptedMailResource, subject)

    def _getTarget(self):
        from .helpers import render_payment_lots_accepted_mail_viewlet
        return render_payment_lots_accepted_mail_viewlet

    def test_multicheckout(self):
        from altair.app.ticketing.payments import plugins
        k = plugins.MULTICHECKOUT_PAYMENT_PLUGIN_ID
        subject = self._make_subject(k)

        data = {"P{}notice".format(k): "*notice*"}
        self.register_fake_storedata(data)

        request = self._make_request(subject)
        result = self._getTarget()(request)
        self.assertIn("*notice*", result)


    def test_checkout(self):
        from altair.app.ticketing.payments import plugins
        k = plugins.CHECKOUT_PAYMENT_PLUGIN_ID
        subject = self._make_subject(k)

        data = {"P{}notice".format(k): "*notice*"}
        self.register_fake_storedata(data)

        request = self._make_request(subject)
        result = self._getTarget()(request)
        self.assertIn("*notice*", result)


    def test_sej(self):
        from altair.app.ticketing.models import DBSession
        order_no = "SEJ:TEST:DEMO"

        def setup():
            DBSession.add(SejOrder(order_no=order_no))
        def teardown():
            import transaction
            transaction.abort()

        from altair.app.ticketing.payments import plugins
        from altair.app.ticketing.sej.models import SejOrder
        k = plugins.SEJ_PAYMENT_PLUGIN_ID

        with SetUpTearDownManager(setup=setup, teardown=teardown):
            data = {"P{}notice".format(k): "*notice*"}
            self.register_fake_storedata(data)

            subject = self._make_subject(k)

            request = self._make_request(subject)
            result = self._getTarget()(request)
            self.assertIn("*notice*", result)

    def test_reserve_number(self):
        from altair.app.ticketing.payments import plugins
        k = plugins.RESERVE_NUMBER_PAYMENT_PLUGIN_ID
        subject = self._make_subject(k)

        data = {"P{}notice".format(k): "*notice*"}
        self.register_fake_storedata(data)

        request = self._make_request(subject)
        result = self._getTarget()(request)
        self.assertIn("*notice*", result)

class PaymentLotsElectedViewletTest(PluginViewletTestBase):
    def _make_subject(self, payment_plugin_id):
        from mock import Mock
        lot_entry_wish = Mock()
        return (
            _make_lot_entry_for_payment(self, payment_plugin_id),
            lot_entry_wish
            )

    def _make_request(self, subject):
        from .lots_mail import LotsElectedMailResource
        return _make_request(LotsElectedMailResource, subject)

    def _getTarget(self):
        from .helpers import render_payment_lots_elected_mail_viewlet
        return render_payment_lots_elected_mail_viewlet

    def test_multicheckout(self):
        from altair.app.ticketing.payments import plugins
        k = plugins.MULTICHECKOUT_PAYMENT_PLUGIN_ID
        subject = self._make_subject(k)
        subject[0].order = _make_order_for_payment(self, k, total_amount=10000)

        data = {"P{}notice".format(k): "*notice*"}
        self.register_fake_storedata(data)

        request = self._make_request(subject)
        result = self._getTarget()(request)
        self.assertIn("*notice*", result)
        self.assertIn("10,000", result)


    def test_checkout(self):
        from altair.app.ticketing.payments import plugins
        k = plugins.CHECKOUT_PAYMENT_PLUGIN_ID
        subject = self._make_subject(k)
        subject[0].order = _make_order_for_payment(self, k, total_amount=10000)

        data = {"P{}notice".format(k): "*notice*"}
        self.register_fake_storedata(data)

        request = self._make_request(subject)
        result = self._getTarget()(request)
        self.assertIn("*notice*", result)
        self.assertIn("10,000", result)


    def test_sej(self):
        from altair.app.ticketing.models import DBSession
        order_no = "SEJ:TEST:DEMO"

        def setup():
            DBSession.add(SejOrder(order_no=order_no))
        def teardown():
            import transaction
            transaction.abort()

        from altair.app.ticketing.payments import plugins
        from altair.app.ticketing.sej.models import SejOrder
        k = plugins.SEJ_PAYMENT_PLUGIN_ID

        with SetUpTearDownManager(setup=setup, teardown=teardown):
            data = {"P{}notice".format(k): "*notice*"}
            self.register_fake_storedata(data)

            subject = self._make_subject(k)
            subject[0].order = _make_order_for_payment(self, k, total_amount=10000)
            subject[0].order.order_no = order_no

            request = self._make_request(subject)
            result = self._getTarget()(request)
            self.assertIn("*notice*", result)

    def test_reserve_number(self):
        from altair.app.ticketing.payments import plugins
        k = plugins.RESERVE_NUMBER_PAYMENT_PLUGIN_ID
        subject = self._make_subject(k)

        data = {"P{}notice".format(k): "*notice*"}
        self.register_fake_storedata(data)

        request = self._make_request(subject)
        result = self._getTarget()(request)
        self.assertIn("*notice*", result)

class PaymentLotsRejectViewletTest(PluginViewletTestBase):
    def _make_subject(self, payment_plugin_id):
        return (
            _make_lot_entry_for_payment(self, payment_plugin_id),
            None
            )

    def _make_request(self, subject):
        from .lots_mail import LotsRejectedMailResource
        return _make_request(LotsRejectedMailResource, subject)

    def _getTarget(self):
        from .helpers import render_payment_lots_rejected_mail_viewlet
        return render_payment_lots_rejected_mail_viewlet

    def test_multicheckout(self):
        from altair.app.ticketing.payments import plugins
        k = plugins.MULTICHECKOUT_PAYMENT_PLUGIN_ID
        subject = self._make_subject(k)

        data = {"P{}notice".format(k): "*notice*"}
        self.register_fake_storedata(data)

        request = self._make_request(subject)
        result = self._getTarget()(request)
        self.assertIn("*notice*", result)

    def test_checkout(self):
        from altair.app.ticketing.payments import plugins
        k = plugins.CHECKOUT_PAYMENT_PLUGIN_ID
        subject = self._make_subject(k)

        data = {"P{}notice".format(k): "*notice*"}
        self.register_fake_storedata(data)

        request = self._make_request(subject)
        result = self._getTarget()(request)
        self.assertIn("*notice*", result)

    def test_sej(self):
        from altair.app.ticketing.models import DBSession
        order_no = "SEJ:TEST:DEMO"

        def setup():
            DBSession.add(SejOrder(order_no=order_no))
        def teardown():
            import transaction
            transaction.abort()

        from altair.app.ticketing.payments import plugins
        from altair.app.ticketing.sej.models import SejOrder
        k = plugins.SEJ_PAYMENT_PLUGIN_ID

        with SetUpTearDownManager(setup=setup, teardown=teardown):
            data = {"P{}notice".format(k): "*notice*"}
            self.register_fake_storedata(data)

            subject = self._make_subject(k)

            request = self._make_request(subject)
            result = self._getTarget()(request)
            self.assertIn("*notice*", result)

    def test_reserve_number(self):
        from altair.app.ticketing.payments import plugins
        k = plugins.RESERVE_NUMBER_PAYMENT_PLUGIN_ID
        subject = self._make_subject(k)

        data = {"P{}notice".format(k): "*notice*"}
        self.register_fake_storedata(data)

        request = self._make_request(subject)
        result = self._getTarget()(request)
        self.assertIn("*notice*", result)
