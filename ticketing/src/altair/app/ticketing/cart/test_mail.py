# -*- coding:utf-8 -*-

""" integreation test

these tests are obsolete, partially?
"""

import unittest
from pyramid import testing
from datetime import datetime
from altair.app.ticketing.testing import DummyRequest
from altair.app.ticketing.mails.testing import MailTestMixin
from . import helpers as h

def _build_order(*args, **kwargs):
    from altair.app.ticketing.orders.models import (
        Order,
        OrderedProduct,
        OrderedProductItem,
        )
    from altair.app.ticketing.core.models import (
        Seat,
        Product,
        SalesSegment,
        SalesSegmentSetting,
        Organization,
        OrganizationSetting,
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
        email_1=kwargs.get("shipping_address__email_1", u"dummy@example.com"),
        tel_1=kwargs.get("shipping_address__tel1"), 
        tel_2=kwargs.get("shipping_address__tel2"), 
        zip=kwargs.get("shipping_address__zip"),
        prefecture=kwargs.get("shipping_address__prefecture"),
        city=kwargs.get("shipping_address__city"),
        address_1=kwargs.get("shipping_address__address_1"),
        address_2=kwargs.get("shipping_address__address_2")
        )

    ordered_from = Organization(name=kwargs.get("ordered_from__name", u"ordered-from-name"), 
                                settings=[
                                    OrganizationSetting(
                                        name='default', 
                                        bcc_recipient=kwargs.get("bcc_recipient"),
                                        default_mail_sender=kwargs.get("ordered_from__setting__default_mail_sender")
                                        )
                                    ])

    performance = Performance(name=kwargs.get("performance__name"),
                              start_on=kwargs.get("performance__start_on", datetime(1900, 1, 1)),  #xxx:
                              venue=Venue(name=kwargs.get("venue__name")), 
                              event=Event(title=kwargs.get("event__title"), 
                                          organization=ordered_from))

    order = Order(ordered_from=ordered_from,
                  id=111, 
                  shipping_address=shipping_address, 
                  performance=performance, 
                  order_no=kwargs.get("order__order_no"), 
                  system_fee=kwargs.get("order__system_fee", 200.00), 
                  special_fee_name=kwargs.get("order__special_fee_name", 200.00), 
                  special_fee=kwargs.get("order__special_fee", 200.00), 
                  transaction_fee=kwargs.get("order__transaction_fee", 300.00), 
                  delivery_fee=kwargs.get("order__delivery_fee", 0.), 
                  total_amount=kwargs.get("order__total_amount", 9999), 
                  created_at=kwargs.get("order__created_at", datetime.now()) ## xxx:
                      )

    ordererd_product0 = OrderedProduct(
        quantity=kwargs.get("product0__quantity", "product-quantity"), 
        product=Product(
            name=kwargs.get("product0__name", "product-name"), 
            price=kwargs.get("product0__price", 400.00),
            sales_segment=SalesSegment(
                seat_choice=kwargs.get("product0__seat_choice", True),
                setting=SalesSegmentSetting(
                    display_seat_no=kwargs.get("product0__display_seat_no", True)
                    )
                )))
    ordered_product_item0 = OrderedProductItem()
    ordered_product_item0.seats.append(Seat(name=kwargs.get("seat0__name")))
    ordererd_product0.elements.append(ordered_product_item0)
    order.items.append(ordererd_product0)

    ordererd_product1 = OrderedProduct(
        quantity=kwargs.get("product1__quantity", "product-quantity"), 
        product=Product(
            name=kwargs.get("product1__name", "product-name"), 
            price=kwargs.get("product1__price", 400.00),
            sales_segment=SalesSegment(
                seat_choice=kwargs.get("product1__seat_choice", True),
                setting=SalesSegmentSetting(
                    display_seat_no=kwargs.get("product1__display_seat_no", True)
                    )
                )))
    ordered_product_item1 = OrderedProductItem()
    ordered_product_item1.seats.append(Seat(name=kwargs.get("seat1__name")))
    ordererd_product1.elements.append(ordered_product_item1)
    order.items.append(ordererd_product1)
    return order

def _build_sej(request, order_no=None, user_name=u'name', user_name_kana=u'name_kana', tel='0300000000', zip_code='0000000', email='test@example.com', total_price=0, ticket_price=0, commission_fee=0, payment_type='1', ticketing_fee=0, payment_due_at=None, ticketing_start_at=None, ticketing_due_at=None, regrant_number_due_at=None):
    from altair.app.ticketing.sej.api import create_sej_order
    sej_order = create_sej_order(
        request,
        order_no=order_no,
        user_name=user_name,
        user_name_kana=user_name_kana,
        tel=tel,
        zip_code=zip_code,
        email=email,
        total_price=total_price,
        ticket_price=ticket_price,
        commission_fee=commission_fee,
        payment_type=payment_type,
        ticketing_fee=ticketing_fee,
        payment_due_at=payment_due_at,
        ticketing_start_at=ticketing_start_at,
        ticketing_due_at=ticketing_due_at,
        regrant_number_due_at=regrant_number_due_at
        )
    sej_order.order_at = datetime(2015, 1, 1)
    sej_order.shop_id = '00000'
    sej_order.shop_name = 'shop_name'
    sej_order.contact_01 = 'contact_01'
    sej_order.contact_02 = 'contact_02'
    return sej_order

class SendPurchaseCompleteMailTest(unittest.TestCase, MailTestMixin):
    def setUp(self):
        from altair.app.ticketing.testing import _setup_db
        self.session = _setup_db(modules=[
                "altair.app.ticketing.lots.models",
                "altair.app.ticketing.core.models",
                "altair.app.ticketing.orders.models",
                "altair.app.ticketing.cart.models",
                ])

        self.config = testing.setUp(settings={
            "altair.sej.template_file": "xxx",
            "altair.multicheckout.endpoint.base_url": "http://example.com/",
            "altair.multicheckout.endpoint.timeout": "0",
            })
        self.config.include('altair.pyramid_dynamic_renderer')
        self.config.include('pyramid_mako')
        self.config.add_mako_renderer('.html')
        self.config.add_mako_renderer('.txt')
        self.config.include('altair.app.ticketing.renderers')
        self.config.include('altair.app.ticketing.cart.import_mail_module')

        ## TBA
        self.config.add_route("qr.make", "__________")

        self.config.include('altair.app.ticketing.sej')
        self.config.include('altair.multicheckout')
        self.config.include('altair.app.ticketing.payments')
        self.config.include('altair.app.ticketing.payments.plugins')
        self.config.add_subscriber('altair.app.ticketing.cart.subscribers.add_helpers', 'pyramid.events.BeforeRender')

        self.registerDummyMailer()
        from mock import patch
        self._patch_get_cart_setting_from_order_like = patch('altair.app.ticketing.cart.api.get_cart_setting_from_order_like')
        p = self._patch_get_cart_setting_from_order_like.start()
        p.return_value.type = 'standard'

    def tearDown(self):
        from altair.app.ticketing.testing import _teardown_db
        from altair.multicheckout import api as multicheckout_api
        from altair.app.ticketing.sej import api as sej_api
        import transaction
        self._patch_get_cart_setting_from_order_like.stop()
        self._get_mailer().outbox = []
        transaction.abort()
        testing.tearDown()
        multicheckout_api.remove_default_session()
        sej_api.remove_default_session()
        _teardown_db()

    def _get_mailer(self):
        from pyramid_mailer import get_mailer
        return get_mailer(self.config)
        
    def _callFUT(self, *args, **kwargs):
        from altair.app.ticketing.cart.events import notify_order_completed
        notify_order_completed(*args, **kwargs)
        
    def test_notify_success(self):
        from pyramid.interfaces import IRequest
        from altair.app.ticketing.mails.interfaces import ICompleteMail, IPurchaseInfoMail
        from zope.interface import implementer

        class DummyMailUtilityModule(object):
            from altair.app.ticketing.mails.api import create_or_update_mailinfo

            def get_mailtype_description():
                return u''

            def get_subject_info_default():
                return 

        @implementer(IPurchaseInfoMail)
        class DummyPurchaseCompleteMail(object):
            request = None
            _called = None
            _order = None

            def __init__(self, mail_template):
                pass

            def build_mail_body(self, request, order, traverser):
                pass

            def build_message_from_mail_body(self, request, order, traverser, mail_body):
                pass

            def build_message(self, request, order, traverser):
                self.__class__._called = "build_message"
                self.__class__._order = order
                return testing.DummyResource(recipients="")
               
        from altair.app.ticketing.mails.config import register_order_mailutility
        from altair.app.ticketing.core.models import MailTypeEnum
        register_order_mailutility(self.config, MailTypeEnum.PurchaseCompleteMail, DummyMailUtilityModule, DummyPurchaseCompleteMail, None)
        request = DummyRequest()

        order = _build_order()
        self._callFUT(request, order)

        self.assertEquals(DummyPurchaseCompleteMail._called, "build_message")
        self.assertEquals(DummyPurchaseCompleteMail._order, order)

        
    def test_exception_in_send_mail_action(self):
        """ メール作成中にエラーが出たときにorderのidがログに出ていることを確認する。
        """
        import mock
        from pyramid.interfaces import IRequest
        from altair.app.ticketing.mails.interfaces import ICompleteMail

        class RaiseExceptionPurchaseCompleteMail(object):
            def __init__(self, request):
                self.request = request
                
            def build_message(self, order):
                raise Exception("wooo-wheee")

        with mock.patch("altair.app.ticketing.cart.sendmail.logger") as m:
            self.config.registry.adapters.register([IRequest], ICompleteMail, "", RaiseExceptionPurchaseCompleteMail)
            request = DummyRequest()
            order = testing.DummyResource(id=121212)
            self._callFUT(request, order)

            self.assertTrue(m.error.called)
            self.assertIn("121212", m.error.call_args[0][0])

        
    def test_normal_success_around_header(self):
        """ card支払いqr受け取りだけれど。このテストは送り先などのチェックに利用。
        """
        from altair.app.ticketing.core.models import (
            PaymentDeliveryMethodPair, 
            PaymentMethod, 
            DeliveryMethod
         )
        request = DummyRequest()

        order = _build_order(
            shipping_address__email_1="purchase@user.ne.jp", 
            ordered_from__name = u"ordered-from-name",
            ordered_from__setting__default_mail_sender="from@organization.ne.jp",
            bcc_recipient="bcc@organization.ne.jp"
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
        self.assertEquals(result.bcc, ["bcc@organization.ne.jp"])
        self.assertEquals(result.sender, "from@organization.ne.jp")

    def test_normal_success_check_body(self):
        """ card支払いqr受け取りだけれど。このテストは共通部分の表示のテスト
        """
        from altair.app.ticketing.core.models import (
            PaymentDeliveryMethodPair, 
            PaymentMethod, 
            DeliveryMethod
         )
        request = DummyRequest()

        order = _build_order(
            shipping_address__first_name=u"first-name", 
            shipping_address__last_name=u"family-name", 
            shipping_address__first_name_kana=u"名前", 
            shipping_address__last_name_kana=u"苗字", 
            shipping_address__email_1="purchase@user.ne.jp", 
            shipping_address__tel1="0120-1234", 
            shipping_address__tel2="08012341234", 
            order__order_no="xxx-xxxx-xxxx", 
            order__created_at=datetime(1900, 1, 1), 
            order__system_fee=20.0,
            order__special_fee=30.0,
            order__special_fee_name=u"特別手数料",
            order__transaction_fee=30.0, 
            order__delivery_fee=40.0, 
            order__total_amount=99999, ##
            ordered_from__name = u"ordered-from-name",
            ordered_from__setting__default_mail_sender="from@organization.ne.jp",
            bcc_recipient="bcc@organization.ne.jp", 
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
        self.assertBodyContains(u"family-name first-name", body)
        self.assertBodyContains(u"苗字 名前", body)
        self.assertBodyContains(u"0120-1234", body)

        ## 受付情報
        self.assertBodyContains(u"xxx-xxxx-xxxx", body, u"xxx-xxxx-xxxx")
        self.assertBodyContains(h.mail_date(datetime(1900, 1, 1)), body, h.mail_date(datetime(1900, 1, 1)))

        ## 公演情報
        self.assertBodyContains(u"何かイベント名", body, u"何かイベント名",)
        self.assertBodyContains(u"何かパフォーマンス名", body, u"何かパフォーマンス名",)
        self.assertBodyContains(u"何か会場名", body, u"何か会場名")
        self.assertBodyContains(h.japanese_datetime(datetime(2000, 1, 1)), body, h.japanese_datetime(datetime(2000, 1, 1)))

        ## 座席情報
        self.assertBodyContains(u"2階A:1", body, u"2階A:1")
        self.assertBodyContains(u"2階A:2", body, u"2階A:2")

        ## 商品情報
        self.assertBodyContains(u"商品名0", body, u"商品名0")
        self.assertBodyContains(h.format_currency(10000.00), body, h.format_currency(10000.00))
        self.assertBodyContains(u"商品名1", body, u"商品名1")
        self.assertBodyContains(h.format_currency(20000.00), body, h.format_currency(20000.00))

        ## 利用料
        self.assertBodyContains(h.format_currency(20), body, h.format_currency(20))
        self.assertBodyContains(h.format_currency(30), body, h.format_currency(30))
        self.assertBodyContains(h.format_currency(40), body, h.format_currency(40))

        ## 合計金額
        self.assertBodyContains(h.format_currency(99999), body, h.format_currency(99999))

        ## pugin
        self.assertBodyContains(u"クレジットカード決済", body, u"クレジットカード決済")
        self.assertBodyContains(u"QR受け取り", body, u"QR受け取り")

        
    def test_payment_by_card_delivery_by_qr(self):
        from altair.app.ticketing.core.models import (
            PaymentDeliveryMethodPair, 
            PaymentMethod, 
            DeliveryMethod
         )
        request = DummyRequest()

        order = _build_order()
        
        from altair.app.ticketing.payments.plugins import MULTICHECKOUT_PAYMENT_PLUGIN_ID, QR_DELIVERY_PLUGIN_ID
        payment_method = PaymentMethod(payment_plugin_id=1, name=u"クレジットカード決済")
        self.assertEquals(payment_method.payment_plugin_id, MULTICHECKOUT_PAYMENT_PLUGIN_ID)
        delivery_method = DeliveryMethod(delivery_plugin_id=4, name=u"QR受け取り")
        self.assertEquals(delivery_method.delivery_plugin_id, QR_DELIVERY_PLUGIN_ID)

        method_pair = PaymentDeliveryMethodPair(payment_method=payment_method, 
                                                delivery_method=delivery_method)
        order.payment_delivery_pair = method_pair

        self._callFUT(request, order)
        result = self._get_mailer().outbox.pop()

        body = result.body
        self.assertBodyContains(u"＜クレジットカードでお支払いの方＞", body)
        # self.assertBodyContains(u"＜試合当日窓口受取の方＞", body)


    def test_payment_by_card_delivery_by_seven(self):
        from altair.app.ticketing.core.models import (
            PaymentDeliveryMethodPair, 
            PaymentMethod, 
            DeliveryMethod
         )
        request = DummyRequest()

        order = _build_order()

        from altair.app.ticketing.sej.models import SejPaymentType
        sej_order = _build_sej(
            request,
            order_no='101010',
            payment_type=SejPaymentType.Paid.v,
            ticketing_start_at=datetime(3000, 1, 1), 
            ticketing_due_at=datetime(4000, 1, 1), 
            )
        sej_order.exchange_number = "707070"
        self.session.add(sej_order)
        self.session.flush()
        order.order_no = sej_order.order_no
        
        from altair.app.ticketing.payments.plugins import MULTICHECKOUT_PAYMENT_PLUGIN_ID, SEJ_DELIVERY_PLUGIN_ID
        payment_method = PaymentMethod(payment_plugin_id=1, name=u"クレジットカード決済")
        self.assertEquals(payment_method.payment_plugin_id, MULTICHECKOUT_PAYMENT_PLUGIN_ID)
        delivery_method = DeliveryMethod(delivery_plugin_id=2, name=u"セブン受け取り")
        self.assertEquals(delivery_method.delivery_plugin_id, SEJ_DELIVERY_PLUGIN_ID)

        method_pair = PaymentDeliveryMethodPair(payment_method=payment_method, 
                                                delivery_method=delivery_method)
        order.payment_delivery_pair = method_pair

        self._callFUT(request, order)
        result = self._get_mailer().outbox.pop()

        body = result.body
        self.assertBodyContains(u"＜クレジットカードでお支払いの方＞", body)

        self.assertBodyContains(u"＜セブン-イレブンでお引取りの方＞", body)
        # self.assertIn(u"次の日から", body)
        self.assertBodyContains(u"707070", body)
        # self.assertBodyContains(h.japanese_datetime(datetime(3000, 1, 1)), body)
        # self.assertBodyContains(h.japanese_datetime(datetime(4000, 1, 1)), body)


    def test_payment_by_card_delivery_home(self):
        from altair.app.ticketing.core.models import (
            PaymentDeliveryMethodPair, 
            PaymentMethod, 
            DeliveryMethod
         )
        request = DummyRequest()

        order = _build_order(
            shipping_address__first_name=u"first-name", 
            shipping_address__last_name=u"family-name", 
            shipping_address__first_name_kana=u"名前", 
            shipping_address__last_name_kana=u"苗字", 
            shipping_address__email_1="purchase@user.ne.jp", 
            shipping_address__zip=u"100-0001", 
            shipping_address__prefecture=u"東京都", 
            shipping_address__city=u"千代田区", 
            shipping_address__address_1=u"千代田1番1号", 
            shipping_address__address_2=u"()", 
            )
        
        from altair.app.ticketing.payments.plugins import MULTICHECKOUT_PAYMENT_PLUGIN_ID, SHIPPING_DELIVERY_PLUGIN_ID
        payment_method = PaymentMethod(payment_plugin_id=1, name=u"クレジットカード決済")
        self.assertEquals(payment_method.payment_plugin_id, MULTICHECKOUT_PAYMENT_PLUGIN_ID)
        delivery_method = DeliveryMethod(delivery_plugin_id=1, name=u"郵送")
        self.assertEquals(delivery_method.delivery_plugin_id, SHIPPING_DELIVERY_PLUGIN_ID)

        method_pair = PaymentDeliveryMethodPair(payment_method=payment_method, 
                                                delivery_method=delivery_method)
        order.payment_delivery_pair = method_pair

        self._callFUT(request, order)
        result = self._get_mailer().outbox.pop()

        body = result.body
        self.assertBodyContains(u"＜クレジットカードでお支払いの方＞", body)
        self.assertBodyContains(u"＜配送にてお引取りの方＞", body)

        self.assertBodyContains(u"苗字 名前", body)
        self.assertBodyContains(u"100-0001", body)
        self.assertBodyContains(u"東京都 千代田区 千代田1番1号 ()", body)

    def test_payment_by_seven_delivery_by_seven_cash_on_delivery(self):
        from altair.app.ticketing.core.models import (
            PaymentDeliveryMethodPair, 
            PaymentMethod, 
            DeliveryMethod
         )
        request = DummyRequest()

        order = _build_order()
        
        ## extra info
        from altair.app.ticketing.sej.models import SejPaymentType
        sej_order = _build_sej(
            request,
            order_no='101010',
            payment_type=SejPaymentType.CashOnDelivery.v,
            payment_due_at=datetime(2000, 1, 1), 
            ticketing_start_at=datetime(3000, 1, 1), 
            ticketing_due_at=datetime(4000, 1, 1)
            )
        sej_order.billing_number="909090"
        sej_order.exchange_number="707070"
        self.session.add(sej_order)
        self.session.flush()
        order.order_no = sej_order.order_no
        
        from altair.app.ticketing.payments.plugins import SEJ_PAYMENT_PLUGIN_ID, SEJ_DELIVERY_PLUGIN_ID
        payment_method = PaymentMethod(payment_plugin_id=3, name=u"セブン支払い")
        self.assertEquals(payment_method.payment_plugin_id, SEJ_PAYMENT_PLUGIN_ID)
        delivery_method = DeliveryMethod(delivery_plugin_id=2, name=u"セブン受け取り")
        self.assertEquals(delivery_method.delivery_plugin_id, SEJ_DELIVERY_PLUGIN_ID)

        method_pair = PaymentDeliveryMethodPair(payment_method=payment_method, 
                                                delivery_method=delivery_method)
        order.payment_delivery_pair = method_pair

        self._callFUT(request, order)
        result = self._get_mailer().outbox.pop()

        body = result.body
        self.assertBodyContains(u"＜セブン-イレブンでのお支払いの方＞", body)
        self.assertBodyContains(u"909090", body)
        self.assertBodyContains(h.japanese_date(datetime(2000, 1, 1)), body)

        self.assertBodyContains(u"＜セブン-イレブンでお引取りの方＞", body)
        self.assertBodyContains(u"チケットは代金と引換です", body)
        self.assertBodyDoesNotContain(u"次の日から", body)
        # self.assertIn(h.japanese_datetime(datetime(3000, 1, 1)), body, u"3000")
        # self.assertIn(h.japanese_datetime(datetime(4000, 1, 1)), body, u"4000")

    def test_payment_by_seven_delivery_by_seven_prepayment(self):
        from altair.app.ticketing.core.models import (
            PaymentDeliveryMethodPair, 
            PaymentMethod, 
            DeliveryMethod
         )
        request = DummyRequest()

        order = _build_order()
        
        ## extra info
        from altair.app.ticketing.sej.models import SejPaymentType
        sej_order = _build_sej(
            request,
            order_no='101010',
            payment_type=SejPaymentType.Prepayment.v,
            payment_due_at=datetime(2000, 1, 1), 
            ticketing_start_at=datetime(3000, 1, 1), 
            ticketing_due_at=datetime(4000, 1, 1)
            )
        sej_order.billing_number="909090"
        sej_order.exchange_number="707070"
        self.session.add(sej_order)
        self.session.flush()
        order.order_no = sej_order.order_no
        
        from altair.app.ticketing.payments.plugins import SEJ_PAYMENT_PLUGIN_ID, SEJ_DELIVERY_PLUGIN_ID
        payment_method = PaymentMethod(payment_plugin_id=3, name=u"セブン支払い")
        self.assertEquals(payment_method.payment_plugin_id, SEJ_PAYMENT_PLUGIN_ID)
        delivery_method = DeliveryMethod(delivery_plugin_id=2, name=u"セブン受け取り")
        self.assertEquals(delivery_method.delivery_plugin_id, SEJ_DELIVERY_PLUGIN_ID)

        method_pair = PaymentDeliveryMethodPair(payment_method=payment_method, 
                                                delivery_method=delivery_method)
        order.payment_delivery_pair = method_pair

        self._callFUT(request, order)
        result = self._get_mailer().outbox.pop()

        body = result.body
        self.assertBodyContains(u"＜セブン-イレブンでのお支払いの方＞", body)
        self.assertBodyContains(u"909090", body)
        self.assertBodyContains(h.japanese_date(datetime(2000, 1, 1)), body)

        self.assertBodyContains(u"＜セブン-イレブンでお引取りの方＞", body)
        self.assertBodyContains(u"707070", body)
        self.assertBodyDoesNotContain(u"次の日から", body)
        # self.assertIn(h.japanese_datetime(datetime(3000, 1, 1)), body, u"3000")
        # self.assertIn(h.japanese_datetime(datetime(4000, 1, 1)), body, u"4000")

    def test_payment_unknown_delivery_by_unknown(self):
        """存在していないpluginが渡されたデータでもメールは飛ぶ。(支払い方法などの欄はほぼ空欄)
        """
        from altair.app.ticketing.core.models import (
            PaymentDeliveryMethodPair, 
            PaymentMethod, 
            DeliveryMethod
         )
        request = DummyRequest()

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
        from altair.app.ticketing.core.models import (
            PaymentDeliveryMethodPair, 
            PaymentMethod, 
            DeliveryMethod, 
            ExtraMailInfo, 
            MailTypeEnum
         )
        request = DummyRequest()

        order = _build_order()
        order.ordered_from.extra_mailinfo = ExtraMailInfo(
            data={str(MailTypeEnum.PurchaseCompleteMail):
                  {u"footer": u"this-is-footer-message", 
                   u"header": u"this-is-header-message"}
                  }
        )
        payment_method = PaymentMethod(payment_plugin_id=9999)
        delivery_method = DeliveryMethod(delivery_plugin_id=9999)
        method_pair = PaymentDeliveryMethodPair(payment_method=payment_method, 
                                                delivery_method=delivery_method)
        order.payment_delivery_pair = method_pair

        self._callFUT(request, order)
        result = self._get_mailer().outbox.pop()

        self.assertBodyContains(u"this-is-header-message", result.body)
        self.assertBodyContains(u"this-is-footer-message", result.body)

if __name__ == "__main__":
    # setUpModule()
    unittest.main()
    
