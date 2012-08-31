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

def _build_order(*args, **kwargs):
    from ticketing.core.models import (
        Order, 
        OrderedProduct, 
        OrderedProductItem, 
        Seat, 
        Product, 
        Organization, 
        ShippingAddress, 
        Performance, 
        Event, 
        Venue
     )
    shipping_address = ShippingAddress(
        first_name=kwargs.get("shipping_address__first_name", u"first-name"), 
        last_name=kwargs.get("shipping_address__last_name", u"last-name"), 
        first_name_kana=kwargs.get("shipping_address__first_name_kana", u"first-name_kana"), 
        last_name_kana=kwargs.get("shipping_address__last_name_kana", u"last-name_kana"), 
        email=kwargs.get("shipping_address__email"), 
        tel_1=kwargs.get("shipping_address__tel1"), 
        tel_2=kwargs.get("shipping_address__tel2"), 
        zip=kwargs.get("shipping_address__zip"),
        prefecture=kwargs.get("shipping_address__prefecture"),
        city=kwargs.get("shipping_address__city"),
        address_1=kwargs.get("shipping_address__address_1"),
        address_2=kwargs.get("shipping_address__address_2")
        )

    ordered_from = Organization(name=kwargs.get("ordered_from__name", u"ordered-from-name"), 
                                contact_email=kwargs.get("ordered_from__contact_email"))

    performance = Performance(name=kwargs.get("performance__name"),
                              start_on=kwargs.get("performance__start_on", datetime(1900, 1, 1)),  #xxx:
                              venue=Venue(name=kwargs.get("venue__name")), 
                              event=Event(title=kwargs.get("event__title")))

    order = Order(ordered_from=ordered_from,
                  id=111, 
                  shipping_address=shipping_address, 
                  performance=performance, 
                  order_no=kwargs.get("order__order_no"), 
                  system_fee=kwargs.get("order__system_fee", 200.00), 
                  transaction_fee=kwargs.get("order__transaction_fee", 300.00), 
                  delivery_fee=kwargs.get("order__delivery_fee"), 
                  total_amount=kwargs.get("order__total_amount", 9999), 
                  created_at=kwargs.get("order__created_at", datetime.now()) ## xxx:
                      )

    ordererd_product0 = OrderedProduct(
        quantity=kwargs.get("product0__quantity", "product-quantity"), 
        product=Product(
            name=kwargs.get("product0__name", "product-name"), 
            price=kwargs.get("product0__price", 400.00)))
    ordered_product_item0 = OrderedProductItem()
    ordered_product_item0.seats.append(Seat(name=kwargs.get("seat0__name")))
    ordererd_product0.ordered_product_items.append(ordered_product_item0)
    order.ordered_products.append(ordererd_product0)

    ordererd_product1 = OrderedProduct(
        quantity=kwargs.get("product1__quantity", "product-quantity"), 
        product=Product(
            name=kwargs.get("product1__name", "product-name"), 
            price=kwargs.get("product1__price", 400.00)))
    ordered_product_item1 = OrderedProductItem()
    ordered_product_item1.seats.append(Seat(name=kwargs.get("seat1__name")))
    ordererd_product1.ordered_product_items.append(ordered_product_item1)
    order.ordered_products.append(ordererd_product1)
    return order

def _build_sej(*args, **kwargs):
    from ticketing.sej.models import SejOrder
    sejorder = SejOrder(**kwargs)
    import sqlahelper
    sqlahelper.get_session().add(sejorder)
    return sejorder

class SendCompleteMailTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(settings={"altair.mailer": "pyramid_mailer.testing"})
        self.config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')
        self.config.include("ticketing.cart.import_mail_module")

        ## TBA
        self.config.add_route("qr.make", "__________")

        self.config.include("ticketing.cart.plugins")
        self.config.add_subscriber('ticketing.cart.subscribers.add_helpers', 'pyramid.events.BeforeRender')

    def tearDown(self):
        self._get_mailer().outbox = []
        import transaction
        transaction.abort()
        testing.tearDown()

    def _get_mailer(self):
        from pyramid_mailer import get_mailer
        return get_mailer(self.config)
        
    def _callFUT(self, *args, **kwargs):
        from ticketing.cart.events import notify_order_completed
        notify_order_completed(*args, **kwargs)
        
    def test_notify_success(self):
        from pyramid.interfaces import IRequest
        from ticketing.mails.interfaces import ICompleteMail

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
        """ メール作成中にエラーが出たときにorderのidがログに出ていることを確認する。
        """
        import mock
        from pyramid.interfaces import IRequest
        from ticketing.mails.interfaces import ICompleteMail

        class RaiseExceptionCompleteMail(object):
            def __init__(self, request):
                self.request = request
                
            def build_message(self, order):
                raise Exception("wooo-wheee")

        with mock.patch("ticketing.cart.sendmail.logger") as m:
            self.config.registry.adapters.register([IRequest], ICompleteMail, "", RaiseExceptionCompleteMail)
            request = testing.DummyRequest()
            order = testing.DummyResource(id=121212)
            self._callFUT(request, order)

            self.assertTrue(m.error.called)
            self.assertIn("121212", m.error.call_args[0][0])

        
    def test_normal_success_around_header(self):
        """ card支払いqr受け取りだけれど。このテストは送り先などのチェックに利用。
        """
        from ticketing.core.models import (
            PaymentDeliveryMethodPair, 
            PaymentMethod, 
            DeliveryMethod
         )
        request = testing.DummyRequest()

        order = _build_order(
            shipping_address__email="purchase@user.ne.jp", 
            ordered_from__name = u"ordered-from-name",
            ordered_from__contact_email="from@organization.ne.jp"
            )
        
        payment_method = PaymentMethod(payment_plugin_id=1)
        delivery_method = DeliveryMethod(delivery_plugin_id=4)
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

        order = _build_order(
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
            order__delivery_fee=40.0, 
            order__total_amount=99999, ##
            ordered_from__name = u"ordered-from-name",
            ordered_from__contact_email="from@organization.ne.jp", 
            performance__name = u"何かパフォーマンス名", 
            performance__start_on = datetime(2000, 1, 1), 
            event__title = u"何かイベント名", 
            venue__name = u"何か会場名", 
            product0__name = u"商品名0", 
            product0__price = 10000.00, 
            product0__quantity = 1, 
            product1__name = u"商品名1", 
            product1__price = 20000.00, 
            product1__quantity = 2, 
            seat0__name = u"2階A:1", 
            seat1__name = u"2階A:2", 
            )
        
        payment_method = PaymentMethod(payment_plugin_id=1, name=u"クレジットカード決済")
        delivery_method = DeliveryMethod(delivery_plugin_id=4, name=u"QR受け取り")
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

        ## 受付情報
        self.assertIn(u"xxx-xxxx-xxxx", body, u"xxx-xxxx-xxxx")
        self.assertIn(h.mail_date(datetime(1900, 1, 1)), body, h.mail_date(datetime(1900, 1, 1)))

        ## 公演情報
        self.assertIn(u"何かイベント名", body, u"何かイベント名",)
        self.assertIn(u"何かパフォーマンス名", body, u"何かパフォーマンス名",)
        self.assertIn(u"何か会場名", body, u"何か会場名")
        self.assertIn(h.japanese_datetime(datetime(2000, 1, 1)), body, h.japanese_datetime(datetime(2000, 1, 1)))

        ## 座席情報
        self.assertIn(u"2階A:1", body, u"2階A:1")
        self.assertIn(u"2階A:2", body, u"2階A:2")

        ## 商品情報
        self.assertIn(u"商品名0", body, u"商品名0")
        self.assertIn(h.format_currency(10000.00), body, h.format_currency(10000.00))
        self.assertIn(u"商品名1", body, u"商品名1")
        self.assertIn(h.format_currency(20000.00), body, h.format_currency(20000.00))

        ## 利用料
        self.assertIn(h.format_currency(20), body, h.format_currency(20))
        self.assertIn(h.format_currency(30), body, h.format_currency(30))
        self.assertIn(h.format_currency(40), body, h.format_currency(40))

        ## 合計金額
        self.assertIn(h.format_currency(99999), body, h.format_currency(99999))

        ## pugin
        self.assertIn(u"クレジットカード決済", body, u"クレジットカード決済")
        self.assertIn(u"QR受け取り", body, u"QR受け取り")

        
    def test_payment_by_card_delivery_by_qr(self):
        from ticketing.core.models import (
            PaymentDeliveryMethodPair, 
            PaymentMethod, 
            DeliveryMethod
         )
        request = testing.DummyRequest()

        order = _build_order()
        
        payment_method = PaymentMethod(payment_plugin_id=1, name=u"クレジットカード決済")
        from ticketing.cart.plugins.multicheckout import PAYMENT_ID
        self.assertEquals(payment_method.payment_plugin_id, PAYMENT_ID)

        delivery_method = DeliveryMethod(delivery_plugin_id=4, name=u"QR受け取り")
        from ticketing.cart.plugins.qr import DELIVERY_PLUGIN_ID
        self.assertEquals(delivery_method.delivery_plugin_id, DELIVERY_PLUGIN_ID)

        method_pair = PaymentDeliveryMethodPair(payment_method=payment_method, 
                                                delivery_method=delivery_method)
        order.payment_delivery_pair = method_pair

        self._callFUT(request, order)
        result = self._get_mailer().outbox.pop()

        body = result.body
        self.assertIn(u"＜クレジットカードでのお支払いの方＞", body)
        self.assertIn(u"＜試合当日窓口受取の方＞", body)


    def test_payment_by_card_delivery_by_seven(self):
        from ticketing.core.models import (
            PaymentDeliveryMethodPair, 
            PaymentMethod, 
            DeliveryMethod
         )
        request = testing.DummyRequest()

        order = _build_order()

        sejorder = _build_sej(order_id=101010,
                              exchange_number="707070", 
                              ticketing_start_at=datetime(3000, 1, 1), 
                              ticketing_due_at=datetime(4000, 1, 1), 
                              )
        order.order_no = sejorder.order_id
        
        payment_method = PaymentMethod(payment_plugin_id=1, name=u"クレジットカード決済")
        from ticketing.cart.plugins.multicheckout import PAYMENT_ID
        self.assertEquals(payment_method.payment_plugin_id, PAYMENT_ID)

        delivery_method = DeliveryMethod(delivery_plugin_id=2, name=u"セブン受け取り")
        from ticketing.cart.plugins.sej import DELIVERY_PLUGIN_ID
        self.assertEquals(delivery_method.delivery_plugin_id, DELIVERY_PLUGIN_ID)

        method_pair = PaymentDeliveryMethodPair(payment_method=payment_method, 
                                                delivery_method=delivery_method)
        order.payment_delivery_pair = method_pair

        self._callFUT(request, order)
        result = self._get_mailer().outbox.pop()

        body = result.body
        self.assertIn(u"＜クレジットカードでのお支払いの方＞", body)

        self.assertIn(u"＜セブン-イレブンでお引取りの方＞", body)
        # self.assertIn(u"次の日から", body)
        self.assertIn(u"707070", body)
        # self.assertIn(h.japanese_datetime(datetime(3000, 1, 1)), body)
        # self.assertIn(h.japanese_datetime(datetime(4000, 1, 1)), body)


    def test_payment_by_card_delivery_home(self):
        from ticketing.core.models import (
            PaymentDeliveryMethodPair, 
            PaymentMethod, 
            DeliveryMethod
         )
        request = testing.DummyRequest()

        order = _build_order(
            shipping_address__first_name=u"first-name", 
            shipping_address__last_name=u"family-name", 
            shipping_address__first_name_kana=u"名前", 
            shipping_address__last_name_kana=u"苗字", 
            shipping_address__email="purchase@user.ne.jp", 
            shipping_address__zip=u"100-0001", 
            shipping_address__prefecture=u"東京都", 
            shipping_address__city=u"千代田区", 
            shipping_address__address_1=u"千代田1番1号", 
            shipping_address__address_2=u"()", 
            )
        
        payment_method = PaymentMethod(payment_plugin_id=1, name=u"クレジットカード決済")
        from ticketing.cart.plugins.multicheckout import PAYMENT_ID
        self.assertEquals(payment_method.payment_plugin_id, PAYMENT_ID)

        delivery_method = DeliveryMethod(delivery_plugin_id=1, name=u"郵送")
        from ticketing.cart.plugins.shipping import PLUGIN_ID
        self.assertEquals(delivery_method.delivery_plugin_id, PLUGIN_ID)

        method_pair = PaymentDeliveryMethodPair(payment_method=payment_method, 
                                                delivery_method=delivery_method)
        order.payment_delivery_pair = method_pair

        self._callFUT(request, order)
        result = self._get_mailer().outbox.pop()

        body = result.body
        self.assertIn(u"＜クレジットカードでのお支払いの方＞", body)
        self.assertIn(u"＜配送にてお引取りの方＞", body)

        self.assertIn(u"苗字 名前", body)
        self.assertIn(u"100-0001", body)
        self.assertIn(u"東京都 千代田区 千代田1番1号 ()", body)

    def test_payment_by_seven_delivery_by_seven(self):
        from ticketing.core.models import (
            PaymentDeliveryMethodPair, 
            PaymentMethod, 
            DeliveryMethod
         )
        request = testing.DummyRequest()

        order = _build_order()
        
        ## extra info
        sejorder = _build_sej(order_id=101010,
                              billing_number="909090", 
                              payment_due_at=datetime(2000, 1, 1), 
                              exchange_number="707070", 
                              ticketing_start_at=datetime(3000, 1, 1), 
                              ticketing_due_at=datetime(4000, 1, 1))
        order.order_no = sejorder.order_id
        
        payment_method = PaymentMethod(payment_plugin_id=3, name=u"セブン支払い")
        from ticketing.cart.plugins.sej import PAYMENT_PLUGIN_ID
        self.assertEquals(payment_method.payment_plugin_id, PAYMENT_PLUGIN_ID)


        delivery_method = DeliveryMethod(delivery_plugin_id=2, name=u"セブン受け取り")
        from ticketing.cart.plugins.sej import DELIVERY_PLUGIN_ID
        self.assertEquals(delivery_method.delivery_plugin_id, DELIVERY_PLUGIN_ID)

        method_pair = PaymentDeliveryMethodPair(payment_method=payment_method, 
                                                delivery_method=delivery_method)
        order.payment_delivery_pair = method_pair

        self._callFUT(request, order)
        result = self._get_mailer().outbox.pop()

        body = result.body
        self.assertIn(u"＜コンビニでのお支払いの方＞", body)
        self.assertIn(u"909090", body)
        self.assertIn(h.japanese_date(datetime(2000, 1, 1)), body)

        self.assertIn(u"＜セブン-イレブンでお引取りの方＞", body)
        self.assertIn(u"707070", body)
        self.assertNotIn(u"次の日から", body)
        # self.assertIn(h.japanese_datetime(datetime(3000, 1, 1)), body, u"3000")
        # self.assertIn(h.japanese_datetime(datetime(4000, 1, 1)), body, u"4000")

    def test_payment_unknown_delivery_by_unknown(self):
        """存在していないpluginが渡されたデータでもメールは飛ぶ。(支払い方法などの欄はほぼ空欄)
        """
        from ticketing.core.models import (
            PaymentDeliveryMethodPair, 
            PaymentMethod, 
            DeliveryMethod
         )
        request = testing.DummyRequest()

        order = _build_order()
        
        payment_method = PaymentMethod(payment_plugin_id=9999, name=u"存在していないpayment plugin")
        delivery_method = DeliveryMethod(delivery_plugin_id=9999, name=u"存在していないdeliveery plugin")
        method_pair = PaymentDeliveryMethodPair(payment_method=payment_method, 
                                                delivery_method=delivery_method)
        order.payment_delivery_pair = method_pair

        self._callFUT(request, order)
        result = self._get_mailer().outbox.pop()
        self.assertTrue(result.body) ## xxx:

    def test_with_extra_mail_info(self):
        from ticketing.core.models import (
            PaymentDeliveryMethodPair, 
            PaymentMethod, 
            DeliveryMethod, 
            ExtraMailInfo, 
            MailTypeEnum
         )
        request = testing.DummyRequest()

        order = _build_order()
        order.ordered_from.extra_mailinfo = ExtraMailInfo(
            data={MailTypeEnum.CompleteMail: {u"footer": u"this-is-footer-message"}}
        )
        payment_method = PaymentMethod(payment_plugin_id=9999)
        delivery_method = DeliveryMethod(delivery_plugin_id=9999)
        method_pair = PaymentDeliveryMethodPair(payment_method=payment_method, 
                                                delivery_method=delivery_method)
        order.payment_delivery_pair = method_pair

        self._callFUT(request, order)
        result = self._get_mailer().outbox.pop()

        self.assertIn(u"this-is-footer-message", result.body)
        



if __name__ == "__main__":
    # setUpModule()
    unittest.main()
    
