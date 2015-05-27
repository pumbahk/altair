# -*- coding:utf-8 -*-


"""
テストメールの共通部分の文面がレンダリング可能かどうか調べている。
* 注文番号(受付番号)が含まれているかだけチェックしている
* PDMPごとの分岐箇所はtest_create_main__pdmp_part.pyで
"""

"""
LotEntry.entry_noとOrder.order_noは同じ
  mysql> select le.* from `Order` as o join LotEntry as le on o.id = le.order_id where le.entry_no <> o.order_no limit 10;
  Empty set (0.48 sec)
"""

import unittest
from pyramid import testing
from datetime import datetime
import mock

from altair.app.ticketing.testing import _setup_db, _teardown_db, DummyRequest

ORGANIZATION_ID = 12345
AUTH_ID = 23456

def setup_operator(auth_id=AUTH_ID, organization_id=ORGANIZATION_ID):
    from altair.app.ticketing.operators.models import OperatorAuth
    from altair.app.ticketing.operators.models import Operator
    from altair.app.ticketing.core.models import Organization
    from altair.app.ticketing.core.models import OrganizationSetting
    from altair.app.ticketing.cart.models import CartSetting
    operator = Operator.query.first()
    if operator is None:
        organization = Organization(name=":Organization:name",
                                    short_name=":Organization:short_name",
                                    code=":Organization:code",
                                    id=organization_id)
        organization.settings = [
            OrganizationSetting(
                name="default",
                contact_pc_url=u'mailto:pc@example.com',
                contact_mobile_url=u'mailto:mobile@example.com',
                cart_setting=CartSetting(
                    lots_orderreview_page_url='http://example.com/review/'
                    )
                )
            ]
        operator = Operator(organization_id=organization_id, organization=organization)
        OperatorAuth(operator=operator, login_id=auth_id)
    return operator

def setup_product_item(quantity, quantity_only, organization, stock_type=None):
    from altair.app.ticketing.core.models import (
        Stock,
        StockStatus,
        StockType,
        StockHolder,
        Performance,
        PerformanceSetting,
        Product,
        ProductItem,
        SalesSegment,
        SalesSegmentGroup,
        Event,
        EventSetting,
        Venue,
        Site,
        PaymentDeliveryMethodPair,
        PaymentMethod,
        DeliveryMethod,
        )

    sales_segment = SalesSegment(start_at=datetime(2000, 1, 1),
                         end_at=datetime(2000, 1, 1, 23),
                         max_quantity=8,
                         seat_choice=True
                         )
    sales_segment.sales_segment_group = SalesSegmentGroup(
        name=":SalesSegmentGroup:name",
        kind=":kind")

    payment_delivery_method_pair = PaymentDeliveryMethodPair(
        system_fee=100,
        transaction_fee=200,
        delivery_fee_per_order=0,
        delivery_fee_per_principal_ticket=300,
        delivery_fee_per_subticket=0,
        discount=0,
        payment_method=PaymentMethod(
            name=":PaymentMethod:name",
            fee=300,
            fee_type=1,
            payment_plugin_id=2),
        delivery_method=DeliveryMethod(
            name=":DeliveryMethod:name",
            fee_per_order=0,
            fee_per_principal_ticket=300,
            fee_per_subticket=0,
            delivery_plugin_id=2)
    )

    sales_segment.payment_delivery_method_pairs.append(payment_delivery_method_pair)

    event_setting = EventSetting()

    performance = Performance(
        name=":Performance:name",
        code=":code",
        open_on=datetime(2000, 1, 1),
        start_on=datetime(2000, 1, 1, 10),
        end_on=datetime(2000, 1, 1, 23),
        abbreviated_title=":PerformanceSetting:abbreviated_title",
        subtitle=":PerformanceSetting:subtitle",
        note=":PerformanceSetting:note",
        event=Event(
            title=":Event:title",
            abbreviated_title=":abbreviated_title",
            organization=organization,
            setting=event_setting,
            code=":Event:code"),
        venue=Venue(
            name=":Venue:name",
            organization=organization,
            sub_name=":sub_name",
            site=Site()
        )
    )
    performance.setting = PerformanceSetting()

    product_item = ProductItem(
        name=":ProductItem:name",
        price=12000,
        quantity=quantity,
        performance=performance,
        product=Product(
            sales_segment=sales_segment,
            name=":Product:name",
            price=10000),
        stock=Stock(
            quantity=10,
            performance=performance,
            stock_type=StockType(
                name=":StockType:name",
                type=":type",
                display_order=50,
                quantity_only=quantity_only
            ),
            stock_holder=StockHolder(name=":StockHolder:name"),
            stock_status=StockStatus(quantity=10)
        )
    )
    product_item.product.seat_stock_type = stock_type or StockType()
    return product_item

def setup_shipping_address(mail_address="my@test.mail.com"):
    from altair.app.ticketing.core.models import ShippingAddress
    return ShippingAddress(
            email_1=mail_address, #xxx:
            email_2=":email_2",
            nick_name=":nick_name",
            first_name=":first_name",
            last_name=":last_name",
            first_name_kana=":first_name_kana",
            last_name_kana=":last_name_kana",
            zip=":zip",
            country=":country",
            prefecture=":prefecture",
            city=":city",
            address_1=":address_1",
            address_2=":address_2",
            tel_1=":tel_1",
            tel_2=":tel_2",
            fax=":fax")


def setup_ordered_product_item(quantity, quantity_only, organization, order_no="Order:order_no", product_item=None, stock_type=None):
    """copied. from altair/ticketing/src/altair/app/ticketing/printqr/test_functional.py"""
    from altair.app.ticketing.orders.models import (
        OrderedProductItem,
        OrderedProduct,
        Order,
        )

    product_item = product_item or setup_product_item(quantity, quantity_only, organization, stock_type) #xxx:
    payment_delivery_method_pair = product_item.product.sales_segment.payment_delivery_method_pairs[0] #xxx:
    order = Order(
        shipping_address=setup_shipping_address(), #xxx:
        total_amount=600,
        system_fee=100,
        transaction_fee=200,
        delivery_fee=300,
        special_fee=400,
        order_no=order_no,
        paid_at=datetime(2000, 1, 1, 1, 10),
        delivered_at=None,
        canceled_at=None,
        created_at=datetime(2000, 1, 1, 1),
        issued_at=datetime(2000, 1, 1, 1, 13),
        organization_id=organization.id,
        ordered_from=organization,  #xxx:
        payment_delivery_pair = payment_delivery_method_pair,
        performance=product_item.performance,
    )
    ordered_product = OrderedProduct(
        price=12000,
        product=product_item.product,
        order=order,
        quantity=quantity
    )
    return OrderedProductItem(price=14000, quantity=quantity, product_item=product_item, ordered_product=ordered_product)

def setup_order(quantity, quantity_only, organization, order_no="Order:order_no", product_item=None, stock_type=None):
    ordered_product_item = setup_ordered_product_item(quantity, quantity_only, organization, order_no=order_no, product_item=product_item, stock_type=stock_type)
    return ordered_product_item.ordered_product.order

def setup_lot_entry(quantity, quantity_only, organization, entry_no="LotEntry:entry_no", product_item=None, stock_type=None):
    from altair.app.ticketing.lots.models import (
        LotEntryWish,
        LotEntry,
        Lot
    )
    product_item = product_item or setup_product_item(quantity, quantity_only, organization, stock_type)
    sales_segment = product_item.product.sales_segment
    payment_delivery_method_pair = sales_segment.payment_delivery_method_pairs[0] #xxx:
    lot_entry = LotEntry(
        organization=organization,
        created_at=datetime(2000, 1, 1, 1),
        payment_delivery_method_pair=payment_delivery_method_pair,
        shipping_address=setup_shipping_address(), #xxx:
        entry_no=entry_no,
        lot=Lot(
            name="Lot:name",
            created_at=datetime(2000, 1, 1, 1),
            sales_segment=sales_segment,
            event=product_item.performance.event
        )
    )
    LotEntryWish(
        lot_entry=lot_entry,
        wish_order=0,
        performance=product_item.performance
    )
    return lot_entry

def setup_eleted_wish(lot_entry, order):
    wish = lot_entry.wishes[0]
    wish.elected_at = datetime(2000, 1, 1)
    wish.order = order
    return wish

def _make_request(organization): #xxx:
    request = DummyRequest()
    request.organization = organization
    request.view_context = testing.DummyResource()
    context = testing.DummyResource(
        organization=organization,
        cart_setting=testing.DummyResource(
            lots_orderreview_page_url=u'http://example.com/review'
            )
        )
    request.context = context
    return request


class MailTemplateCreationTest(unittest.TestCase):
    def setUp(self):
        from mock import patch
        from altair.sqlahelper import register_sessionmaker_with_engine
        session = _setup_db([
            'altair.app.ticketing.core.models',
            'altair.app.ticketing.orders.models',
            'altair.app.ticketing.lots.models'
            ])
        self.config = testing.setUp(settings={"altair.mailer": "pyramid_mailer.testing", "altair.sej.template_file": ""})
        self.config.include('pyramid_mako')
        self.config.include('altair.pyramid_dynamic_renderer')
        self.config.add_mako_renderer('.html')
        self.config.add_mako_renderer('.txt')
        self.config.include('altair.app.ticketing.mails.install_mail_utility')
        self.config.include('altair.app.ticketing.payments')
        self.config.include('altair.app.ticketing.payments.plugins')
        register_sessionmaker_with_engine(
            self.config.registry,
            'slave',
            session.bind
            )
        self.session = session
        self._patch_get_cart_setting_from_order_like = patch('altair.app.ticketing.cart.api.get_cart_setting_from_order_like')
        p = self._patch_get_cart_setting_from_order_like.start()
        p.return_value.type = 'standard'

    def tearDown(self):
        self._patch_get_cart_setting_from_order_like.stop()
        testing.tearDown()
        _teardown_db()

    def _getTarget(self, request, mtype):
        from .api import get_mail_utility
        return get_mail_utility(request, mtype)

    def _callAction(self, request, subject, mtype):
        from pyramid_mako import MakoRenderingException
        try:
            target = self._getTarget(request, mtype)
            return target.build_message(request, subject)
        except MakoRenderingException as e:
            raise AssertionError(e.text)

    def test_purchase_complete_mail(self):
        from altair.app.ticketing.core.models import MailTypeEnum, StockType, StockTypeEnum
        operator = setup_operator()
        self.session.add(operator)
        order_no = "*orderno*"
        stock_type = StockType()
        stock_type.type = StockTypeEnum.Other.v
        order = setup_order(quantity=2,
                            quantity_only=True,
                            organization=operator.organization,
                            order_no=order_no,
                            stock_type=stock_type)
        request = _make_request(operator.organization)

        with mock.patch("altair.app.ticketing.mails.complete.ch.render_payment_finished_mail_viewlet") as prender:
            with mock.patch("altair.app.ticketing.mails.complete.ch.render_delivery_finished_mail_viewlet") as drender:
                result = self._callAction(request, order, MailTypeEnum.PurchaseCompleteMail)
                self.assertTrue(result.body.data, str) #xxx:
                self.assertIn("*orderno*", result.body.data)
                self.assertTrue(prender.called)
                self.assertTrue(drender.called)

        stock_type = StockType()
        stock_type.type = StockTypeEnum.Seat.v
        order = setup_order(quantity=2,
                            quantity_only=True,
                            organization=operator.organization,
                            order_no=order_no,
                            stock_type=stock_type)
        with mock.patch("altair.app.ticketing.mails.complete.ch.render_payment_finished_mail_viewlet") as prender:
            with mock.patch("altair.app.ticketing.mails.complete.ch.render_delivery_finished_mail_viewlet") as drender:
                result = self._callAction(request, order, MailTypeEnum.PurchaseCompleteMail)
                self.assertTrue(result.body.data, str) #xxx:
                self.assertIn("*orderno*", result.body.data)
                self.assertTrue(prender.called)
                self.assertTrue(drender.called)


    def test_purchase_cancel_mail(self):
        from altair.app.ticketing.core.models import MailTypeEnum
        operator = setup_operator()
        self.session.add(operator)
        order_no = "*orderno*"
        order = setup_order(quantity=2,
                            quantity_only=True,
                            organization=operator.organization,
                            order_no=order_no)
        request = _make_request(operator.organization)

        result = self._callAction(request, order, MailTypeEnum.PurchaseCancelMail)
        self.assertTrue(result.body.data, str) #xxx:
        self.assertIn("*orderno*", result.body.data)
        self.assertIn(order.payment_delivery_pair.payment_method.name, result.body.data)
        self.assertIn(order.payment_delivery_pair.delivery_method.name, result.body.data)


    def test_lot_accepted_mail(self):
        from altair.app.ticketing.core.models import MailTypeEnum
        operator = setup_operator()
        self.session.add(operator)
        entry_no = "*entryno*"
        lot_entry = setup_lot_entry(quantity=2,
                                    quantity_only=True,
                                    organization=operator.organization,
                                    entry_no=entry_no)
        request = _make_request(operator.organization)
        with mock.patch("altair.app.ticketing.mails.lots_mail.ch.render_payment_lots_accepted_mail_viewlet") as prender:
            with mock.patch("altair.app.ticketing.mails.lots_mail.ch.render_delivery_lots_accepted_mail_viewlet") as drender:
                result = self._callAction(request, (lot_entry, None), MailTypeEnum.LotsAcceptedMail)
                self.assertTrue(result.body.data, str) #xxx:
                self.assertIn("*entryno*", result.body.data)
                self.assertTrue(prender.called)
                self.assertTrue(drender.called)

    def test_lot_elected_mail(self):
        from altair.app.ticketing.core.models import MailTypeEnum
        operator = setup_operator()
        self.session.add(operator)
        entry_no = "*entryno*"

        quantity_settings=dict(
            quantity=2,
            quantity_only=True,
            organization=operator.organization
        )
        product_item = setup_product_item(**quantity_settings)
        order = setup_order(
            order_no=entry_no,
            product_item=product_item,
            **quantity_settings
        )
        lot_entry = setup_lot_entry(
            entry_no=entry_no,
            product_item=product_item,
            **quantity_settings
        )
        elected_wish = setup_eleted_wish(lot_entry=lot_entry, order=order)
        request = _make_request(operator.organization)

        with mock.patch("altair.app.ticketing.mails.lots_mail.ch.render_payment_lots_elected_mail_viewlet") as prender:
            with mock.patch("altair.app.ticketing.mails.lots_mail.ch.render_delivery_lots_elected_mail_viewlet") as drender:
                result = self._callAction(request, (lot_entry, elected_wish), MailTypeEnum.LotsElectedMail)
                self.assertTrue(result.body.data, str) #xxx:
                self.assertIn("*entryno*", result.body.data) #order_no == entry_no らしい
                self.assertTrue(prender.called)
                self.assertTrue(drender.called)

    def test_lot_rejected_mail(self):
        from altair.app.ticketing.core.models import MailTypeEnum
        operator = setup_operator()
        self.session.add(operator)
        entry_no = "*entryno*"

        lot_entry = setup_lot_entry(quantity=2,
                                    quantity_only=True,
                                    organization=operator.organization,
                                    entry_no=entry_no)
        request = _make_request(operator.organization)

        with mock.patch("altair.app.ticketing.mails.lots_mail.ch.render_payment_lots_rejected_mail_viewlet") as prender:
            with mock.patch("altair.app.ticketing.mails.lots_mail.ch.render_delivery_lots_rejected_mail_viewlet") as drender:
                result = self._callAction(request, (lot_entry, None), MailTypeEnum.LotsRejectedMail)
                self.assertTrue(result.body.data, str) #xxx:
                self.assertIn("*entryno*", result.body.data)

                ## 落選メールは呼ばれないのが正しい？
                self.assertFalse(prender.called)
                self.assertFalse(drender.called)
