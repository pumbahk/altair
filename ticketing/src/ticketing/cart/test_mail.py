# -*- coding:utf-8 -*-

""" integreation test
"""

import unittest
from pyramid import testing
from datetime import datetime
from ticketing.cart import helpers as h

def setUpModule():
    from ticketing.testing import _setup_db
    _setup_db(modules=[
            "ticketing.models",
            "ticketing.core.models",
            "ticketing.cart.models",
            ])

def tearDownModule():
    from ticketing.testing import _teardown_db
    _teardown_db()

class SendCompleteMailTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(settings={"altair.mailer": "pyramid_mailer.testing"})
        self.config.include("ticketing.cart.import_mail_module")
        self.config.add_subscriber('ticketing.cart.subscribers.add_helpers', 'pyramid.events.BeforeRender')

    def tearDown(self):
        self._get_mailer().outbox = []
        testing.tearDown()

    def _get_mailer(self):
        from pyramid_mailer import get_mailer
        return get_mailer(self.config)
        
    def _callFUT(self, *args, **kwargs):
        from ticketing.cart.events import notify_order_completed
        notify_order_completed(*args, **kwargs)
        
    def test_notify_success(self):
        from pyramid.interfaces import IRequest
        from ticketing.cart.interfaces import ICompleteMail

        class DummyCompleteMail(object):
            def __init__(self, request):
                self.request = request

            def build_message(self, order):
                self.__class__._called = "build_message"
                self.__class__._order = order
                return testing.DummyResource(recipients="")
               
        self.config.registry.adapters.register([IRequest], ICompleteMail, "", DummyCompleteMail)
        request = testing.DummyRequest()
        order = object()
        self._callFUT(request, order)

        self.assertEquals(DummyCompleteMail._called, "build_message")
        self.assertEquals(DummyCompleteMail._order, order)

        
    def test_exception_in_send_mail_action(self):
        pass

    def _build_order(self, *args, **kwargs):
        from ticketing.core.models import (
            Order, 
            OrderedProduct, 
            Product, 
            Organization, 
            ShippingAddress, 
            Performance, 
         )
        shipping_address = ShippingAddress(
            first_name=kwargs.get("shipping_address__first_name", u"first-name"), 
            last_name=kwargs.get("shipping_address__last_name", u"last-name"), 
            first_name_kana=kwargs.get("shipping_address__first_name_kana", u"first-name_kana"), 
            last_name_kana=kwargs.get("shipping_address__last_name_kana", u"last-name_kana"), 
            email=kwargs.get("shipping_address__email"), 
            tel_1=kwargs.get("shipping_address__tel1"), 
            tel_2=kwargs.get("shipping_address__tel2"), 
            )

        ordered_from = Organization(name=kwargs.get("ordered_from__name", u"ordered-from-name"), 
                                    contact_email=kwargs.get("ordered_from__contact_email"))

        performance = Performance(name=kwargs.get("performance__name"))

        order = Order(ordered_from=ordered_from,
                      shipping_address=shipping_address, 
                      performance=performance, 
                      order_no=kwargs.get("order__order_no"), 
                      system_fee=kwargs.get("order__system_fee", 200.00), 
                      transaction_fee=kwargs.get("order__transaction_fee", 300.00), 
                      total_amount=kwargs.get("order__total_amount", 9999), 
                      created_at=kwargs.get("order__created_at", datetime.now()) ## xxx:
                          )
        
        order.ordered_products.append(
            OrderedProduct(
                product=Product(
                    name=kwargs.get("product0__name", "product-name"), 
                    price=kwargs.get("product0__price", 400.00))))
        order.ordered_products.append(
            OrderedProduct(
                product=Product(
                    name=kwargs.get("product1__name", "product-name"), 
                    price=kwargs.get("product1__price", 400.00))))

        return order

    def test_normal_success_around_header(self):
        """ card支払いqr受け取りだけれど。このテストは送り先などのチェックに利用。
        """
        from ticketing.core.models import (
            PaymentDeliveryMethodPair, 
            PaymentMethod, 
            DeliveryMethod
         )
        request = testing.DummyRequest()

        order = self._build_order(
            shipping_address__email="purchase@user.ne.jp", 
            ordered_from__name = u"ordered-from-name",
            ordered_from__contact_email="from@organization.ne.jp"
            )
        
        payment_method = PaymentMethod(payment_plugin_id=1)
        delivery_method = DeliveryMethod(delivery_plugin_id=5)
        method_pair = PaymentDeliveryMethodPair(payment_method=payment_method, 
                                                delivery_method=delivery_method)
        order.payment_delivery_pair = method_pair

        self._callFUT(request, order)
        result = self._get_mailer().outbox.pop()

        self.assertIn(u"ordered-from-name", result.subject)
        self.assertEquals(result.recipients, ["purchase@user.ne.jp"])
        self.assertEquals(result.bcc, ["from@organization.ne.jp"])
        self.assertEquals(result.sender, "from@organization.ne.jp")

    def test_normal_success_check_body(self):
        """ card支払いqr受け取りだけれど。このテストは共通部分の表示のテスト
        """
        from ticketing.core.models import (
            PaymentDeliveryMethodPair, 
            PaymentMethod, 
            DeliveryMethod
         )
        request = testing.DummyRequest()

        order = self._build_order(
            shipping_address__first_name=u"first-name", 
            shipping_address__last_name=u"family-name", 
            shipping_address__first_name_kana=u"名前", 
            shipping_address__last_name_kana=u"苗字", 
            shipping_address__email="purchase@user.ne.jp", 
            shipping_address__tel1="0120-1234", 
            shipping_address__tel2="08012341234", 
            order__order_no="xxx-xxxx-xxxx", 
            order__created_at=datetime(1900, 1, 1), 
            order__system_fee=20.0, 
            order__transaction_fee=30.0, 
            order__total_amount=99999, ##
            ordered_from__name = u"ordered-from-name",
            ordered_from__contact_email="from@organization.ne.jp", 
            performance__name = u"何かパフォーマンス名", 
            product0__name = u"商品名0", 
            product0__price = 10000.00, 
            product1__name = u"商品名1", 
            product1__price = 20000.00
            )
        
        payment_method = PaymentMethod(payment_plugin_id=1, name=u"クレジットカード決済")
        delivery_method = DeliveryMethod(delivery_plugin_id=5, name=u"QR受け取り")
        method_pair = PaymentDeliveryMethodPair(payment_method=payment_method, 
                                                delivery_method=delivery_method)
        order.payment_delivery_pair = method_pair

        self._callFUT(request, order)
        result = self._get_mailer().outbox.pop()
        body = result.body

        ## 基本情報
        self.assertIn(u"family-name first-name", body)
        self.assertIn(u"苗字 名前", body)
        self.assertIn(u"0120-1234", body)
        self.assertIn(u"08012341234", body)

        ## 受付情報
        self.assertIn(u"xxx-xxxx-xxxx", body)
        self.assertIn(h.mail_date(datetime(1900, 1, 1)), body)

        ## 公演情報
        self.assertIn(u"何かパフォーマンス名", body)

        ## 商品情報
        self.assertIn(u"商品名0", body)
        self.assertIn(h.format_currency(10000.00), body)
        self.assertIn(u"商品名1", body)
        self.assertIn(h.format_currency(20000.00), body)

        ## 利用料
        self.assertIn(h.format_currency(20), body)
        self.assertIn(h.format_currency(30), body)

        ## 合計金額
        self.assertIn(h.format_currency(99999), body)

        ##
        self.assertIn(u"クレジットカード決済", body)
        self.assertIn(u"QR受け取り", body)

    # def test_payment_by_card_delivery_by_qr(self):
    #     from ticketing.core.models import (
    #         PaymentDeliveryMethodPair, 
    #         PaymentMethod, 
    #         DeliveryMethod
    #      )
    #     request = testing.DummyRequest()

    #     order = self._build_order()
        
    #     payment_method = PaymentMethod(payment_plugin_id=1)
    #     from ticketing.cart.plugins.multicheckout import PAYMENT_ID
    #     self.assertEquals(payment_method.payment_plugin_id, PAYMENT_ID)

    #     delivery_method = DeliveryMethod(delivery_plugin_id=5)
    #     from ticketing.cart.plugins.qr import PLUGIN_ID
    #     self.assertEquals(delivery_method.delivery_plugin_id, PLUGIN_ID)

    #     method_pair = PaymentDeliveryMethodPair(payment_method=payment_method, 
    #                                             delivery_method=delivery_method)
    #     order.payment_delivery_pair = method_pair

    #     self._callFUT(request, order)
    #     result = self._get_mailer().outbox.pop()
    #     print dir(result)
    #     ##

    def test_payment_by_card_delivery_by_seven(self):
        pass

    def test_payment_by_card_delivery_home(self):
        pass

    def test_payment_by_seven_delivery_by_seven(self):
        pass

    def test_payment_unknown_delivery_by_unknown(self):
        pass

if __name__ == "__main__":
    # setUpModule()
    unittest.main()
    
