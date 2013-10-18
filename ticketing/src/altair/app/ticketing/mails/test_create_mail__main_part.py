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

from altair.app.ticketing.testing import _setup_db, _teardown_db

def setUpModule():
    _setup_db(['altair.app.ticketing.core.models',
               'altair.app.ticketing.lots.models'])

def tearDownModule():
    _teardown_db()

ORGANIZATION_ID = 12345
AUTH_ID = 23456
    
def setup_operator(auth_id=AUTH_ID, organization_id=ORGANIZATION_ID):
    from altair.app.ticketing.operators.models import OperatorAuth
    from altair.app.ticketing.operators.models import Operator
    from altair.app.ticketing.core.models import Organization
    from altair.app.ticketing.core.models import OrganizationSetting
    operator = Operator.query.first()
    if operator is None:
        organization = Organization(name=":Organization:name",
                                    short_name=":Organization:short_name", 
                                    code=":Organization:code", 
                                    id=organization_id)
        OrganizationSetting(organization=organization, name="default")
        operator = Operator(organization_id=organization_id, organization=organization)
        OperatorAuth(operator=operator, login_id=auth_id)
    return operator

def setup_product_item(quantity, quantity_only, organization):
    from altair.app.ticketing.core.models import Stock
    from altair.app.ticketing.core.models import StockStatus
    from altair.app.ticketing.core.models import StockType
    from altair.app.ticketing.core.models import StockHolder
    from altair.app.ticketing.core.models import Performance
    from altair.app.ticketing.core.models import PerformanceSetting
    from altair.app.ticketing.core.models import Product
    from altair.app.ticketing.core.models import ProductItem
    from altair.app.ticketing.core.models import SalesSegment
    from altair.app.ticketing.core.models import SalesSegmentGroup
    from altair.app.ticketing.core.models import Event
    from altair.app.ticketing.core.models import Venue
    from altair.app.ticketing.core.models import Site
    from altair.app.ticketing.core.models import PaymentDeliveryMethodPair
    from altair.app.ticketing.core.models import PaymentMethod
    from altair.app.ticketing.core.models import DeliveryMethod

    sales_segment = SalesSegment(start_at=datetime(2000, 1, 1), 
                         end_at=datetime(2000, 1, 1, 23), 
                         upper_limit=8, 
                         seat_choice=True
                         )
    sales_segment.sales_segment_group = SalesSegmentGroup(
        name=":SalesSegmentGroup:name", 
        kind=":kind")

    payment_delivery_method_pair = PaymentDeliveryMethodPair(
        system_fee=100, 
        transaction_fee=200, 
        delivery_fee=300, 
        discount=0, 
        payment_method=PaymentMethod(
            name=":PaymentMethod:name", 
            fee=300, 
            fee_type=1, 
            payment_plugin_id=2), 
        delivery_method=DeliveryMethod(
            name=":DeliveryMethod:name", 
            fee=300, 
            fee_type=1, 
            delivery_plugin_id=2)
    )

    sales_segment.payment_delivery_method_pairs.append(payment_delivery_method_pair)
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
            code=":Event:code"), 
        venue=Venue(
            name=":Venue:name", 
            organization=organization, 
            sub_name=":sub_name", 
            site=Site()
        )
    )
    performance.settings.append(PerformanceSetting())

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


def setup_ordered_product_item(quantity, quantity_only, organization, order_no="Order:order_no", product_item=None):
    """copied. from altair/ticketing/src/altair/app/ticketing/printqr/test_functional.py"""
    from altair.app.ticketing.core.models import OrderedProductItem
    from altair.app.ticketing.core.models import OrderedProduct
    from altair.app.ticketing.core.models import Order

    product_item = product_item or setup_product_item(quantity, quantity_only, organization) #xxx:
    payment_delivery_method_pair = product_item.product.sales_segment.payment_delivery_method_pairs[0] #xxx:
    order = Order(
        shipping_address=setup_shipping_address(), #xxx:
        total_amount=600, 
        system_fee=100, 
        transaction_fee=200, 
        delivery_fee=300, 
        special_fee=400, 
        multicheckout_approval_no=":multicheckout_approval_no", 
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

def setup_order(quantity, quantity_only, organization, order_no="Order:order_no", product_item=None):
    ordered_product_item = setup_ordered_product_item(quantity, quantity_only, organization, order_no=order_no, product_item=product_item)
    return ordered_product_item.ordered_product.order

def setup_lot_entry(quantity, quantity_only, organization, entry_no="LotEntry:entry_no", product_item=None):
    from altair.app.ticketing.lots.models import (
        LotEntryWish, 
        LotEntry, 
        Lot
    )
    product_item = product_item or setup_product_item(quantity, quantity_only, organization)
    sales_segment = product_item.product.sales_segment
    payment_delivery_method_pair = sales_segment.payment_delivery_method_pairs[0] #xxx:
    lot_entry = LotEntry(
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
    request = testing.DummyRequest()
    request.organization = organization
    class context:
        organization = request.organization
    request.context = context
    return request


class MailTemplateCreationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = testing.setUp(settings={"altair.mailer": "pyramid_mailer.testing", "altair.sej.template_file": ""})
        cls.config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')
        cls.config.add_renderer('.txt' , 'pyramid.mako_templating.renderer_factory')
        cls.config.include('altair.app.ticketing.mails.install_mail_utility')
        cls.config.include('altair.app.ticketing.payments')
        cls.config.include('altair.app.ticketing.payments.plugins')
        
    @classmethod
    def tearDownClass(cls):
        testing.tearDown()

    def _getTarget(self, request, mtype):
        from .api import get_mail_utility        
        return get_mail_utility(request, mtype)

    def _callAction(self, request, subject, mtype):
        from pyramid.mako_templating import MakoRenderingException
        try:
            target = self._getTarget(request, mtype)
            return target.build_message(request, subject)
        except MakoRenderingException as e:
            raise AssertionError(e.text)

    def test_purchase_complete_mail(self):
        from altair.app.ticketing.core.models import MailTypeEnum
        operator = setup_operator()
        order_no = "*orderno*"
        order = setup_order(quantity=2,
                            quantity_only=True,
                            organization=operator.organization, 
                            order_no=order_no)
        request = _make_request(operator.organization)

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
        order_no = "*orderno*"
        order = setup_order(quantity=2,
                            quantity_only=True,
                            organization=operator.organization, 
                            order_no=order_no)
        request = _make_request(operator.organization)

        with mock.patch("altair.app.ticketing.mails.order_cancel.ch.render_payment_cancel_mail_viewlet") as prender:
            with mock.patch("altair.app.ticketing.mails.order_cancel.ch.render_delivery_cancel_mail_viewlet") as drender:
                result = self._callAction(request, order, MailTypeEnum.PurchaseCancelMail)
                self.assertTrue(result.body.data, str) #xxx:
                self.assertIn("*orderno*", result.body.data)
                self.assertTrue(prender.called)
                self.assertTrue(drender.called)


    def test_lot_accepted_mail(self):
        from altair.app.ticketing.core.models import MailTypeEnum
        operator = setup_operator()
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
