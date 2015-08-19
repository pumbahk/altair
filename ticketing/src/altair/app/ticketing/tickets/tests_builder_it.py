# -*- coding:utf-8 -*-
## iff slow, move.

import unittest
import transaction
from datetime import datetime
import mock
from contextlib import nested
###

import altair.app.ticketing.operators.models
import altair.app.ticketing.core.models
from altair.app.ticketing.tickets.utils import datetime_as_dict

class _IntegrationAssertionMixin(object):
    def assert_basic_renderable_placeholder(self, data):
        self.assertEquals(data[u"イベント名"], u":Event:title")
        self.assertEquals(data[u"イベント名略称"], u":abbreviated_title")

        self.assertEquals(data[u"aux"][u"key"], u"value")

        self.assertEquals(data[u"パフォーマンス名"], u":Performance:name")
        self.assertEquals(data[u"対戦名"], u":Performance:name")
        self.assertEquals(data[u"公演コード"], u":code")
        self.assertEquals(data[u"開催日"], u"2000年 01月 01日 (土)")
        self.assertEquals(data[u"開場時刻"], u"00時 00分")
        self.assertEquals(data[u"開始時刻"], u"10時 00分")
        self.assertEquals(data[u"終了時刻"], u"23時 00分")
        self.assertEquals(data[u"開催日s"], u"2000/01/01 (土)")
        self.assertEquals(data[u"開場時刻s"], u"00:00")
        self.assertEquals(data[u"開始時刻s"], u"10:00")
        self.assertEquals(data[u"終了時刻s"], u"23:00")

        self.assertEqual(data[u"公演名略称"], u":PerformanceSetting:abbreviated_title")
        self.assertEqual(data[u"公演名備考"], u":PerformanceSetting:note")
        self.assertEqual(data[u"公演名副題"], u":PerformanceSetting:subtitle")

        self.assertEquals(data[u"会場名"], u":Venue:name")

        self.assertEquals(data[u"商品名"], u":ProductItem:name")
        self.assertEquals(data[u"商品価格"], u"12,000円")
        self.assertEquals(data[u"券種名"], u":ProductItem:name")
        self.assertEquals(data[u"チケット価格"], u"14,000円")

        self.assertEquals(data[u"予約番号"], u":order_no")
        self.assertEquals(data[u"受付番号"], u":order_no")
        self.assertEquals(data[u"注文番号"], u":order_no")
        self.assertEquals(data[u"注文日時"], u"2000年 01月 01日 (土) 01時 00分")
        self.assertEquals(data[u"受付日時"], u"2000年 01月 01日 (土) 01時 00分")
        self.assertEquals(data[u"注文日時s"], u"2000/01/01 (土) 01:00")
        self.assertEquals(data[u"受付日時s"], u"2000/01/01 (土) 01:00")

        self.assertEquals(data[u"住所"], u":zip:prefecture:city:address_1:address_2")
        self.assertEquals(data[u"氏名"], u":last_name :first_name")
        self.assertEquals(data[u"氏名カナ"], u":last_name_kana :first_name_kana")
        self.assertEquals(data[u"電話番号"], u":tel_1")
        self.assertEquals(data[u"メールアドレス"], u"my@test.mail.com")

class BuilderItTest(_IntegrationAssertionMixin, unittest.TestCase):
    def tearDown(self):
        transaction.abort()

    def _getTarget(self):
        from altair.app.ticketing.tickets.vars_builder import TicketDictBuilder
        return TicketDictBuilder

    def _makeOne(self, *args, **kwargs):
        from altair.app.ticketing.formatter import Japanese_Japan_Formatter
        return self._getTarget()(Japanese_Japan_Formatter(), *args, **kwargs)

    def test__build_user_profile__none(self):
        target = self._makeOne()
        data = {}
        model = None
        result = target.build_user_profile_dict(data, model)
        self.assertEqual(result["userProfile"], {})

    def test__build_user_profile(self):
        from altair.app.ticketing.users.models import UserProfile
        model = UserProfile(email_1=":email_1",
                            email_2=":email_2",
                            nick_name=":nick_name",
                            first_name=":first_name",
                            last_name=":last_name",
                            first_name_kana=":first_name_kana",
                            last_name_kana=":last_name_kana",
                            birthday=datetime(2000, 1, 1),
                            sex=1,
                            zip=u":zip",
                            country=":country",
                            prefecture=u":prefecture",
                            city=u":city",
                            address_1=u":address_1",
                            tel_1=":tel_1",
                            address_2=u":address_2",
                            tel_2=":tel_2",
                            fax=":fax",
                            status=1,
                            rakuten_point_account=":rakuten_point_account"
                            )
        target = self._makeOne()
        data = {}
        result = target.build_user_profile_dict(data, model)

        sub = result["userProfile"]
        self.assertEqual(sub["email_1"], ":email_1")
        self.assertEqual(sub["email_2"],  ":email_2")
        self.assertEqual(sub["email"],  ":email_1")
        self.assertEqual(sub["nick_name"],  ":nick_name")
        self.assertEqual(sub["first_name"],  ":first_name")
        self.assertEqual(sub["last_name"],  ":last_name")
        self.assertEqual(sub["first_name_kana"],  ":first_name_kana")
        self.assertEqual(sub["last_name_kana"],  ":last_name_kana")
        self.assertEqual(sub["birthday"],  datetime_as_dict(datetime(2000, 1, 1)))
        self.assertEqual(sub["sex"],  u"男性")
        self.assertEqual(sub["zip"],  ":zip")
        self.assertEqual(sub["country"],  ":country")
        self.assertEqual(sub["prefecture"],  ":prefecture")
        self.assertEqual(sub["city"],  ":city")
        self.assertEqual(sub["address_1"],  ":address_1")
        self.assertEqual(sub["address_2"],  ":address_2")
        self.assertEqual(sub["tel_1"],  ":tel_1")
        self.assertEqual(sub["tel_2"],  ":tel_2")
        self.assertEqual(sub["fax"],  ":fax")
        self.assertEqual(sub["status"],  1)


    def test__build_shipping_address__none(self):
        target = self._makeOne()
        data = {}
        model = None
        result = target.build_shipping_address_dict(data, model)
        self.assertEqual(result["shippingAddress"], {})

    def test__build_shipping_address_model(self):
        from altair.app.ticketing.core.models import ShippingAddress
        target = self._makeOne()
        data = {}
        model = ShippingAddress(
            email_1=":email_1",
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
            fax=":fax",
            )
        result = target.build_shipping_address_dict(data, model)
        sub = result["shippingAddress"]
        self.assertEqual(sub["email_1"],  ":email_1")
        self.assertEqual(sub["email_2"],  ":email_2")
        self.assertEqual(sub["email"],  ":email_1")
        self.assertEqual(sub["nick_name"],  ":nick_name")
        self.assertEqual(sub["first_name"],  ":first_name")
        self.assertEqual(sub["last_name"],  ":last_name")
        self.assertEqual(sub["first_name_kana"],  ":first_name_kana")
        self.assertEqual(sub["last_name_kana"],  ":last_name_kana")
        self.assertEqual(sub["zip"],  ":zip")
        self.assertEqual(sub["country"],  ":country")
        self.assertEqual(sub["prefecture"],  ":prefecture")
        self.assertEqual(sub["city"],  ":city")
        self.assertEqual(sub["address_1"],  ":address_1")
        self.assertEqual(sub["address_2"],  ":address_2")
        self.assertEqual(sub["tel_1"],  ":tel_1")
        self.assertEqual(sub["tel_2"],  ":tel_2")
        self.assertEqual(sub["fax"],  ":fax")

    def test__build_stock__none(self):
        target = self._makeOne()
        data = {}
        model = None
        result = target.build_dict_from_stock(model, retval=data)
        self.assertEqual(result["stock"], {})

    def test__build_stock(self):
        from altair.app.ticketing.core.models import Stock
        from altair.app.ticketing.core.models import StockStatus
        from altair.app.ticketing.core.models import StockType
        from altair.app.ticketing.core.models import StockHolder

        target = self._makeOne()
        data = {}
        model = Stock(quantity=10)
        model.stock_type = StockType(name=":StockType:name", type=":type", display_order=50, quantity_only=True)
        model.stock_holder = StockHolder(name=":StockHolder:name")
        model.stock_status = StockStatus(quantity=10)
        result = target.build_dict_from_stock(model, retval=data)

        sub = result["stock"]
        self.assertEqual(sub["quantity"], 10)

        sub = result["stockStatus"]
        self.assertEqual(sub["quantity"], 10)

        sub = result["stockHolder"]
        self.assertEqual(sub["name"], ":StockHolder:name")

        sub = result["stockType"]
        self.assertEqual(sub["name"], ":StockType:name")
        self.assertEqual(sub["type"], ":type")
        self.assertEqual(sub["display_order"], 50)
        self.assertEqual(sub["quantity_only"], True)

        self.assertEqual(result[u"席種名"], ":StockType:name")

    def test_build_organization__none(self):
        target = self._makeOne()
        data = {}
        model = None
        result = target.build_dict_from_organization(model, retval=data)
        self.assertEqual(result["organization"], {})

    def test_build_organization(self):
        from altair.app.ticketing.core.models import Organization
        target = self._makeOne()
        data = {}
        model = Organization(name=":name",
                             code=":code")
        result = target.build_dict_from_organization(model, retval=data)
        sub = result["organization"]
        self.assertEqual(sub["name"], ":name")
        self.assertEqual(sub["code"], ":code")

    def test_build_event__none(self):
        target = self._makeOne()
        data = {}
        model = None
        result = target.build_dict_from_event(model, retval=data)
        self.assertEqual(result["event"], {})
        self.assertEqual(result["organization"], {})

    def test_build_event(self):
        from altair.app.ticketing.core.models import Event
        from altair.app.ticketing.core.models import Organization
        target = self._makeOne()
        data = {}
        model = Event(title=":title",
                      abbreviated_title=":abbreviated_title",
                      code=":Event:code")
        model.organization = Organization(name=":name",
                                          code=":Organization:code")

        result = target.build_dict_from_event(model, retval=data)

        sub = result["organization"]
        self.assertEqual(sub["name"], ":name")
        self.assertEqual(sub["code"], ":Organization:code")

        sub = result["event"]
        self.assertEqual(sub["title"], ":title")
        self.assertEqual(sub["abbreviated_title"], ":abbreviated_title")
        self.assertEqual(sub["code"], ":Event:code")

        self.assertEqual(result[u"イベント名"], ":title")
        self.assertEqual(result[u"イベント名略称"], ":abbreviated_title")

    def test_build_performance__none(self):
        target = self._makeOne()
        data = {}
        model = None
        result = target.build_dict_from_performance(model, retval=data)
        self.assertEqual(result["performance"], {})

    def test_build_performance(self):
        from altair.app.ticketing.core.models import Performance
        target = self._makeOne()
        data = {}
        model = Performance(name=":name",
                            code=":code",
                            open_on=datetime(2000, 1, 1),
                            start_on=datetime(2000, 1, 1, 10),
                            end_on=datetime(2000, 1, 1, 23),
                            abbreviated_title=":abbreviated_title",
                            subtitle=":subtitle",
                            note=":note")
        with mock.patch.object(target, "build_dict_from_event") as m, mock.patch.object(target, "build_dict_from_performance_setting") as n:
            m.side_effect = lambda _, retval:retval
            n.side_effect = lambda _, retval:retval

            result = target.build_dict_from_performance(model, retval=data)

            sub = result["performance"]
            self.assertEqual(sub['name'],  ":name")
            self.assertEqual(sub['code'],  ":code")
            self.assertEqual(sub['open_on'],  datetime_as_dict(datetime(2000, 1, 1)))
            self.assertEqual(sub['start_on'],  datetime_as_dict(datetime(2000, 1, 1, 10)))
            self.assertEqual(sub['end_on'],  datetime_as_dict(datetime(2000, 1, 1, 23)))

            self.assertEqual(result[u'パフォーマンス名'],  ":name")
            self.assertEqual(result[u'対戦名'],  ":name")
            self.assertEqual(result[u'公演コード'],  ":code")
            self.assertEqual(result[u'開催日'],  target.formatter.format_date(model.start_on))
            self.assertEqual(result[u'開催日c'],  target.formatter.format_date_compressed(model.start_on))
            self.assertEqual(result[u'開催日s'],  target.formatter.format_date_short(model.start_on))
            self.assertEqual(result[u'開場時刻'],  target.formatter.format_time(model.open_on))
            self.assertEqual(result[u'開場時刻s'],  target.formatter.format_time_short(model.open_on))
            self.assertEqual(result[u'開始時刻'],  target.formatter.format_time(model.start_on))
            self.assertEqual(result[u'開始時刻s'],  target.formatter.format_time_short(model.start_on))
            self.assertEqual(result[u'終了時刻'],  target.formatter.format_time(model.end_on))
            self.assertEqual(result[u'終了時刻s'],  target.formatter.format_time_short(model.end_on))
            self.assertEqual(result[u"公演名略称"], ":abbreviated_title")
            self.assertEqual(result[u"公演名副題"], ":subtitle")
            self.assertEqual(result[u"公演名備考"], ":note")

            m.assert_called_once_with(model.event, retval=result)
            n.assert_called_once_with(None, retval=result)


    def test_build_performance_setting__none(self):
        target = self._makeOne()
        data = {}
        model = None
        result = target.build_dict_from_performance_setting(model, retval=data)
        self.assertEqual(result, {})

    def test_build_performance_setting(self):
        from altair.app.ticketing.core.models import PerformanceSetting
        target = self._makeOne()
        data = {}
        model = PerformanceSetting()
        result = target.build_dict_from_performance_setting(model, retval=data)
        self.assertEqual(result, {})

    def test_build_venue__none(self):
        target = self._makeOne()
        data = {}
        model = None
        result = target.build_dict_from_venue(model, retval=data)
        self.assertEqual(result["venue"], {})

    def test_build_venue(self):
        from altair.app.ticketing.core.models import Venue
        target = self._makeOne()
        data = {}
        model = Venue(name=":name",
                      sub_name=":sub_name")
        with mock.patch.object(target, "build_dict_from_performance") as m:
            m.side_effect = lambda _, retval: retval
            result = target.build_dict_from_venue(model, retval=data)

            sub = result["venue"]
            self.assertEqual(sub[u'name'],  ":name")
            self.assertEqual(sub[u'sub_name'], ":sub_name")

            self.assertEqual(result[u"会場名"], ":name")
            m.assert_called_once_with(model.performance, retval=result)

    def test_build_seat__none(self):
        target = self._makeOne()
        model = None
        data = {}
        result = target.build_dict_from_seat(model, retval=data)
        self.assertEqual(result["seat"], {})

    def test_build_seat(self):
        from altair.app.ticketing.core.models import Seat
        target = self._makeOne()
        data = {}
        model = Seat(l0_id=":l0_id",
                     seat_no=":seat_no",
                     name=":name")
        model.attributes = {"key": "value"}

        with mock.patch.object(target, "build_dict_from_venue") as n:
            n.side_effect = lambda _, retval: retval
            result = target.build_dict_from_seat(model, retval=data)

            sub = result["seat"]
            self.assertEqual(sub[u'l0_id'],  ":l0_id")
            self.assertEqual(sub[u'seat_no'],  ":seat_no")
            self.assertEqual(sub[u'name'],  ":name")

            sub = result["seatAttributes"]
            self.assertEqual(sub["key"], "value")

            self.assertEqual(result[u"席番"], ":name")

            n.assert_called_once_with(model.venue, retval=result)

    def test_build_product__none(self):
        target = self._makeOne()
        model = None
        data = {}
        result = target.build_dict_from_product(model, retval=data)
        self.assertEqual(result["product"], {})

    def test_build_product(self):
        from altair.app.ticketing.core.models import Product
        target = self._makeOne()
        data = {}
        model = Product(name=":name",
                        price=10000.0)

        with mock.patch.object(target, "build_dict_from_sales_segment") as m:
            m.side_effect = lambda _, retval: retval
            result = target.build_dict_from_product(model, retval=data)

            sub = result["product"]
            self.assertEqual(sub[u'name'],  ":name")
            self.assertEqual(sub[u'price'],  10000.0)

            self.assertEqual(result[u"券種名"], ":name")
            self.assertEqual(result[u"商品名"], ":name")
            self.assertEqual(result[u"商品価格"], target.formatter.format_currency(model.price))
            self.assertEqual(result[u"チケット価格"], target.formatter.format_currency(model.price))

            m.assert_called_once_with(model.sales_segment, retval=result)


    def test_build_sales_segment__none(self):
        target = self._makeOne()
        model = None
        data = {}
        result = target.build_dict_from_sales_segment(model, retval=data)
        self.assertEqual(result["salesSegment"], {})

    def test_build_sales_segment(self):
        from altair.app.ticketing.core.models import SalesSegment
        from altair.app.ticketing.core.models import SalesSegmentGroup
        target = self._makeOne()
        data = {}
        model = SalesSegment(start_at=datetime(2000, 1, 1),
                             end_at=datetime(2000, 1, 1, 23),
                             max_quantity=8,
                             seat_choice=True
                             )
        model.sales_segment_group = SalesSegmentGroup(
            name=":name",
            kind=":kind")
        result = target.build_dict_from_sales_segment(model, retval=data)

        sub = result["salesSegment"]

        self.assertEqual(sub[u'name'],  ":name")
        self.assertEqual(sub[u'kind'],  ":kind")
        self.assertEqual(sub[u'start_at'],  datetime_as_dict(datetime(2000, 1, 1)))
        self.assertEqual(sub[u'end_at'],  datetime_as_dict(datetime(2000, 1, 1, 23)))
        self.assertEqual(sub[u'max_quantity'],  8)
        self.assertEqual(sub[u'seat_choice'],  True)

    def test_build_product_item__none(self):
        target = self._makeOne()
        model = None
        data = {}
        result = target.build_dict_from_product_item(model, retval=data)
        self.assertEqual(result["productItem"], {})

    def test_build_product_item(self):
        from altair.app.ticketing.core.models import Performance
        from altair.app.ticketing.core.models import Product
        from altair.app.ticketing.core.models import ProductItem
        target = self._makeOne()
        data = {}
        model = ProductItem(name=":ProductItem:name",
                            price=12000,
                            quantity=8,
                            )
        model.product = Product(name=":Product:name",
                                price=10000)
        model.performance = Performance()
        with nested(mock.patch.object(target, "build_dict_from_product"),
                    mock.patch.object(target, "build_dict_from_ticket_bundle"),
                    mock.patch.object(target, "build_dict_from_stock"),
                    mock.patch.object(target, "build_dict_from_venue"),
                    ) as (m, n, o, p):
            m.side_effect = lambda _, retval: retval
            n.side_effect = lambda _, retval: retval
            o.side_effect = lambda _, retval: retval
            p.side_effect = lambda _, retval: retval
            result = target.build_dict_from_product_item(model, retval=data)

            sub = result["productItem"]

            self.assertEqual(sub[u'name'],  ":ProductItem:name")
            self.assertEqual(sub[u'price'],  12000)
            self.assertEqual(sub[u'quantity'], 8)

            self.assertEqual(result[u"券種名"], ":ProductItem:name")
            self.assertEqual(result[u"商品名"], ":ProductItem:name")
            self.assertEqual(result[u"チケット価格"], target.formatter.format_currency(12000))
            self.assertEqual(result[u"商品価格"], target.formatter.format_currency(10000))

            m.assert_called_once_with(model.product, retval=result)
            n.assert_called_once_with(model.ticket_bundle, retval=result)
            o.assert_called_once_with(model.stock, retval=result)
            p.assert_called_once_with(model.performance.venue, retval=result)

    def test_build_ticket_bundle__none(self):
        target = self._makeOne()
        model = None
        data = {}
        result = target.build_dict_from_ticket_bundle(model, retval=data)
        self.assertEqual(result["aux"], {})

    def test_build_ticket_bundle(self):
        from altair.app.ticketing.core.models import TicketBundle
        target = self._makeOne()
        data = {}
        model = TicketBundle()
        model.attributes = {"key": "value"}

        result = target.build_dict_from_ticket_bundle(model, retval=data)
        sub = result["aux"]
        self.assertEqual(sub["key"], "value")

    def test_build_order__none(self):
        target = self._makeOne()
        model = None
        data = {}
        result = target.build_dict_from_order(model, retval=data)
        self.assertEqual(result["order"], {})


    def test_build_order(self):
        from altair.app.ticketing.orders.models import Order
        target = self._makeOne()
        data = {}
        model = Order(total_amount=600,
                      system_fee=100,
                      special_fee=400,
                      special_fee_name=u'特別手数料',
                      transaction_fee=200,
                      delivery_fee=300,
                      order_no=":order_no",
                      paid_at=datetime(2000, 1, 1, 1, 10),
                      delivered_at=None,
                      canceled_at=None,
                      created_at=datetime(2000, 1, 1, 1),
                      issued_at=datetime(2000, 1, 1, 1, 13),
                      )
        with nested(mock.patch.object(target, "build_shipping_address_dict"),
                    mock.patch.object(target, "build_user_profile_dict"),
                    mock.patch.object(target, "build_dict_from_payment_delivery_method_pair")) as (m, n, p):
            m.side_effect = lambda retval, _: retval
            n.side_effect = lambda retval, _: retval
            p.side_effect = lambda _, retval: retval

            user_profile = object()
            result = target.build_dict_from_order(model, retval=data, user_profile=user_profile)
            sub = result["order"]
            self.assertEqual(sub[u'total_amount'],  600)
            self.assertEqual(sub[u'system_fee'],  100)
            self.assertEqual(sub[u'special_fee'],  400)
            self.assertEqual(sub[u'special_fee_name'],  u'特別手数料')
            self.assertEqual(sub[u'transaction_fee'],  200)
            self.assertEqual(sub[u'delivery_fee'],  300)
            self.assertEqual(sub[u'order_no'],  ":order_no")
            self.assertEqual(sub[u'paid_at'],  datetime_as_dict(datetime(2000, 1, 1, 1, 10)))
            self.assertEqual(sub[u'delivered_at'],  datetime_as_dict(None))
            self.assertEqual(sub[u'canceled_at'],  datetime_as_dict(None))

            self.assertEqual(result[u'注文番号'], ":order_no")
            self.assertEqual(result[u'注文日時'], target.formatter.format_datetime(datetime(2000, 1, 1, 1)))
            self.assertEqual(result[u'注文日時s'], target.formatter.format_datetime_short(datetime(2000, 1, 1, 1)))
            self.assertEqual(result[u'受付番号'], ":order_no")
            self.assertEqual(result[u'受付日時'], target.formatter.format_datetime(datetime(2000, 1, 1, 1)))
            self.assertEqual(result[u'受付日時s'], target.formatter.format_datetime_short(datetime(2000, 1, 1, 1)))
            self.assertEqual(result[u'発券日時'], target.formatter.format_datetime(datetime(2000, 1, 1, 1, 13)))
            self.assertEqual(result[u'発券日時s'], target.formatter.format_datetime_short(datetime(2000, 1, 1, 1, 13)))
            self.assertEqual(result[u'予約番号'], ":order_no")

            m.assert_called_once_with(result, model.shipping_address)
            n.assert_called_once_with(result, user_profile)
            p.assert_called_once_with(model.payment_delivery_pair, retval=result)


    def test_build_order_attribute(self):
        from altair.app.ticketing.orders.models import Order
        target = self._makeOne()
        model = Order()
        model.attributes["memo_on_order1"] = u":memo_on_order1"
        model.attributes["memo_on_order2"] = u":memo_on_order2"
        model.attributes["memo_on_order3"] = u":memo_on_order3"
        data = {}
        result = target.build_dict_from_order(model, retval=data)
        self.assertEqual(result[u"予約時補助文言1"], u":memo_on_order1")
        self.assertEqual(result[u"予約時補助文言2"], u":memo_on_order2")
        self.assertEqual(result[u"予約時補助文言3"], u":memo_on_order3")

    def test_build_payment_delivery_method_pair__none(self):
        target = self._makeOne()
        model = None
        data = {}
        result = target.build_dict_from_payment_delivery_method_pair(model, retval=data)
        self.assertEqual(result, {})

    def test_build_payment_delivery_method_pair(self):
        from altair.app.ticketing.core.models import PaymentDeliveryMethodPair
        from altair.app.ticketing.core.models import FeeTypeEnum
        target = self._makeOne()
        model = PaymentDeliveryMethodPair(
            system_fee=100,
            special_fee=400,
            special_fee_name=u'特別手数料',
            special_fee_type=FeeTypeEnum.PerUnit.v[0],
            transaction_fee=200,
            delivery_fee_per_order=0,
            delivery_fee_per_principal_ticket=300,
            delivery_fee_per_subticket=0
            )
        data = {}
        with nested(mock.patch.object(target, "build_dict_from_payment_method"),
                    mock.patch.object(target, "build_dict_from_delivery_method")) as (m, n):
            m.side_effect = lambda _, retval: retval
            n.side_effect = lambda _, retval: retval

            result = target.build_dict_from_payment_delivery_method_pair(model, retval=data)
            self.assertEqual(result, {})


    def test_build_payment_method__none(self):
        target = self._makeOne()
        model = None
        data = {}
        result = target.build_dict_from_payment_method(model, retval=data)
        self.assertEqual(result["paymentMethod"], {})

    def test_build_payment_method(self):
        from altair.app.ticketing.core.models import PaymentMethod
        target = self._makeOne()
        model = PaymentMethod(name=":name",
                              fee=300,
                              fee_type=1,
                              payment_plugin_id=2)
        data = {}
        result = target.build_dict_from_payment_method(model, retval=data)

        sub = result["paymentMethod"]
        self.assertEqual(sub[u'name'],  ":name")
        self.assertEqual(sub[u'fee'],  300)
        self.assertEqual(sub[u'fee_type'],  1)
        self.assertEqual(sub[u'plugin_id'],  2)


    def test_build_delivery_method__none(self):
        target = self._makeOne()
        model = None
        data = {}
        result = target.build_dict_from_delivery_method(model, retval=data)
        self.assertEqual(result["deliveryMethod"], {})

    def test_build_delivery_method(self):
        from altair.app.ticketing.core.models import DeliveryMethod
        target = self._makeOne()
        model = DeliveryMethod(name=":name", fee_per_order=0, fee_per_principal_ticket=300, fee_per_subticket=0, delivery_plugin_id=2)
        data = {}
        result = target.build_dict_from_delivery_method(model, retval=data)

        sub = result["deliveryMethod"]
        self.assertEqual(sub[u'name'],  ":name")
        self.assertEqual(sub[u'fee'],  300)
        self.assertEqual(sub[u'fee_type'],  1)
        self.assertEqual(sub[u'plugin_id'],  2)


    def test_build_ordered_product_item__none(self):
        target = self._makeOne()
        model = None
        data = {}
        result = target.build_basic_dict_from_ordered_product_item(model, retval=data)
        self.assertEqual(result["orderedProductItem"], {})

    def test_build_ordered_product_item(self):
        from altair.app.ticketing.orders.models import (
            OrderedProductItem,
            OrderedProduct,
            )
        target = self._makeOne()
        data = {}
        model = OrderedProductItem(price=14000,
                                   )
        model.ordered_product = OrderedProduct(price=12000,
                                               quantity=8)
        model.attributes["key"] = "value"
        with nested(mock.patch.object(target, "build_dict_from_order"),
                    mock.patch.object(target, "build_dict_from_product_item"),
                    ) as (m, n):
            m.side_effect = lambda _, user_profile, retval: retval
            n.side_effect = lambda _, retval: retval
            user_profile = object()
            result = target.build_basic_dict_from_ordered_product_item(model, user_profile=user_profile, retval=data)

            sub = result["orderedProductItem"]
            self.assertEqual(sub[u'price'],  14000)

            sub = result["orderedProductItemAttributes"]
            self.assertEqual(sub["key"], "value")

            sub = result["orderedProduct"]
            self.assertEqual(sub[u'price'],  12000)
            self.assertEqual(sub[u'quantity'],  8)

            self.assertEqual(result[u"商品価格"], target.formatter.format_currency(12000))
            self.assertEqual(result[u"チケット価格"], target.formatter.format_currency(14000))

            m.assert_called_once_with(model.ordered_product.order, user_profile=user_profile, retval=result)
            n.assert_called_once_with(model.product_item, retval=result)


ORGANIZATION_ID = 12345

def setup_organization(organization_id=ORGANIZATION_ID):
    from altair.app.ticketing.core.models import Organization
    organization = Organization(name=":Organization:name",
                                short_name=":Organization:short_name",
                                code=":Organization:code",
                                id=organization_id)
    return organization

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
    from altair.app.ticketing.core.models import FeeTypeEnum

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
            fee_per_principal_ticket=300,
            fee_per_order=0,
            fee_per_subticket=0,
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
    payment_method = payment_delivery_method_pair.payment_method = PaymentMethod(name=":PaymentMethod:name",
                          fee=300,
                          fee_type=1,
                          payment_plugin_id=2)
    delivery_method = payment_delivery_method_pair.delivery_method = DeliveryMethod(name=":DeliveryMethod:name",
                          fee_per_order=0,
                          fee_per_principal_ticket=300,
                          fee_per_subticket=0,
                          delivery_plugin_id=2)
    performance.setting = PerformanceSetting()

    product_item = ProductItem(
        name=":ProductItem:name",
        price=14000,
        quantity=quantity,
        performance=performance,
        product=Product(
            sales_segment=sales_segment,
            name=":Product:name",
            price=12000),
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
    from altair.app.ticketing.orders.models import (
        OrderedProductItem,
        OrderedProduct,
        Order,
        )

    product_item = product_item or setup_product_item(quantity, quantity_only, organization) #xxx:
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

def setup_ticket_bundle(product_item):
    from altair.app.ticketing.core.models import TicketBundle
    event = product_item.performance.event
    ticket_bundle = event.ticket_bundle = product_item.ticket_bundle = TicketBundle()
    ticket_bundle.attributes["key"] = "value"
    return ticket_bundle

def setup_carted_product_item(quantity, quantity_only, organization, product_item=None, order_no="Cart:orderno"):
    from altair.app.ticketing.cart.models import CartedProductItem
    from altair.app.ticketing.cart.models import CartedProduct
    from altair.app.ticketing.cart.models import Cart

    product_item = product_item or setup_product_item(quantity, quantity_only, organization) #xxx:
    shipping_address=setup_shipping_address() #xxx:
    sales_segment = product_item.product.sales_segment #xxx:

    cart = Cart(
        shipping_address=shipping_address,
        _order_no=order_no,
        created_at=datetime(2000, 1, 1, 1),
        sales_segment=sales_segment
    )
    carted_product_item = CartedProductItem(
        quantity=quantity,
        product_item=product_item,
        carted_product=CartedProduct(
            cart=cart,
            quantity=quantity,
            product=product_item.product
        )
    )
    return carted_product_item


def get_ordered_product_item__full_relation(quantity, quantity_only):
    organization = setup_organization()
    product_item = setup_product_item(quantity, quantity_only, organization)
    setup_ticket_bundle(product_item)
    return setup_ordered_product_item(quantity, quantity_only, organization, product_item=product_item, order_no=":order_no")

def get_carted_product_item__full_relation(quantity, quantity_only):
    organization = setup_organization()
    product_item = setup_product_item(quantity, quantity_only, organization)
    setup_ticket_bundle(product_item)
    return setup_carted_product_item(quantity, quantity_only, organization, product_item=product_item, order_no=":order_no")

def setup_ordered_product_token_from_ordered_product_item(ordered_product_item):
    from altair.app.ticketing.orders.models import OrderedProductItemToken
    from altair.app.ticketing.core import api as core_api
    for i, seat in core_api.iterate_serial_and_seat(ordered_product_item):
        token = OrderedProductItemToken(
            item = ordered_product_item,
            serial = i,
            seat = seat,
            valid=True #valid=Falseの時は何時だろう？
        )


def setup_seat_from_ordered_product_item(ordered_product_item):
    from altair.app.ticketing.core.models import Seat
    seat = Seat(l0_id=":l0_id",
                seat_no=":seat_no",
                name=":Seat:name",
                stock = ordered_product_item.product_item.stock,
                venue = ordered_product_item.product_item.performance.venue)
    ordered_product_item.seats.append(seat)
    return seat

class BuilderItTicketCreateTest(_IntegrationAssertionMixin, unittest.TestCase):
    def tearDown(self):
        transaction.abort()

    def _getTarget(self):
        from altair.app.ticketing.tickets.vars_builder import TicketDictBuilder
        return TicketDictBuilder

    def _makeOne(self, *args, **kwargs):
        from altair.app.ticketing.formatter import Japanese_Japan_Formatter
        return self._getTarget()(Japanese_Japan_Formatter(), *args, **kwargs)

    def _makeIssuer(self):
        return lambda x: "*NumberIssuer*"

    def test_build_ordered_product_item_token__without_seat(self):
        target = self._makeOne()
        ordered_product_item = get_ordered_product_item__full_relation(quantity=2, quantity_only=True)
        setup_ordered_product_token_from_ordered_product_item(ordered_product_item)

        model = ordered_product_item.tokens[0]
        result = target.build_dict_from_ordered_product_item_token(model, ticket_number_issuer=self._makeIssuer())

        self.assertTrue(result)
        data = result
        # import json
        # print json.dumps(data, ensure_ascii=False, indent=2)

        self.assert_basic_renderable_placeholder(data)

        self.assertEquals(data[u"席種名"], u":StockType:name")
        # self.assertEquals(data[u"席番"], u"") #xxx!
        self.assertEquals(data[u"発券日時"], u"2000年 01月 01日 (土) 01時 13分")
        self.assertEquals(data[u"発券日時s"], u"2000/01/01 (土) 01:13")

        self.assertEquals(data[u"発券番号"], "*NumberIssuer*")



    def test_build_ordered_product_item_token__with_seat(self):
        target = self._makeOne()
        ordered_product_item = get_ordered_product_item__full_relation(quantity=2, quantity_only=False)
        seat = setup_seat_from_ordered_product_item(ordered_product_item)
        setup_ordered_product_token_from_ordered_product_item(ordered_product_item)
        model = ordered_product_item.tokens[0]

        result = target.build_dict_from_ordered_product_item_token(model, ticket_number_issuer=self._makeIssuer())

        self.assertTrue(result)
        data = result
        # import json
        # print json.dumps(data, ensure_ascii=False, indent=2)

        self.assert_basic_renderable_placeholder(data)

        self.assertEquals(data[u"席種名"], u":StockType:name")
        self.assertEquals(data[u"席番"], u":Seat:name") #xxx!
        self.assertEquals(data[u"発券日時"], u"2000年 01月 01日 (土) 01時 13分")
        self.assertEquals(data[u"発券日時s"], u"2000/01/01 (土) 01:13")

        self.assertEquals(data[u"発券番号"], "*NumberIssuer*")


class BuilderItTicketListCreateTest(_IntegrationAssertionMixin, unittest.TestCase):
    """see: https://redmine.ticketstar.jp/issues/5138"""
    def tearDown(self):
        transaction.abort()

    def _getTarget(self):
        from altair.app.ticketing.tickets.vars_builder import TicketDictListBuilder
        return TicketDictListBuilder

    def _makeOne(self, *args, **kwargs):
        from altair.app.ticketing.formatter import Japanese_Japan_Formatter
        from altair.app.ticketing.tickets.vars_builder import TicketDictBuilder
        builder = TicketDictBuilder(Japanese_Japan_Formatter(), *args, **kwargs)
        return self._getTarget()(builder)

    def _makeIssuer(self):
        return lambda x: "*NumberIssuer*"

    def test_build_ordered_product_item__without_seat(self):
        target = self._makeOne()
        ordered_product_item = get_ordered_product_item__full_relation(quantity=2, quantity_only=True)
        setup_ordered_product_token_from_ordered_product_item(ordered_product_item)
        model = ordered_product_item
        result = target.build_dicts_from_ordered_product_item(model, ticket_number_issuer=self._makeIssuer())
        self.assertEqual(len(result), 2)
        seat_result, data = result[0]
        # import json
        # print json.dumps(data, ensure_ascii=False, indent=2)

        self.assert_basic_renderable_placeholder(data)
        self.assertEquals(data[u"席種名"], u":StockType:name")
        # self.assertEquals(data[u"席番"], u"") #xxx!

        self.assertEquals(data[u"発券番号"], "*NumberIssuer*")

    def test_build_ordered_product_item__with_seat(self):
        target = self._makeOne()
        ordered_product_item = get_ordered_product_item__full_relation(quantity=1, quantity_only=False)
        setup_seat_from_ordered_product_item(ordered_product_item)
        setup_ordered_product_token_from_ordered_product_item(ordered_product_item)

        model = ordered_product_item
        result = target.build_dicts_from_ordered_product_item(model, ticket_number_issuer=self._makeIssuer())
        # import json
        # print json.dumps(result, ensure_ascii=False, indent=2)

        self.assertEqual(len(result), 1)
        seat_result, data = result[0]

        self.assert_basic_renderable_placeholder(data)

        self.assertEquals(data[u"席種名"], u":StockType:name")
        self.assertEquals(data[u"席番"], u":Seat:name") #xxx!
        self.assertEquals(data[u"発券日時"], u"2000年 01月 01日 (土) 01時 13分")
        self.assertEquals(data[u"発券日時s"], u"2000/01/01 (土) 01:13")

        self.assertEquals(data[u"発券番号"], "*NumberIssuer*")

    def test_build_ordered_product_item__without_seat__and_without_token(self): #BC
        target = self._makeOne()
        ordered_product_item = get_ordered_product_item__full_relation(quantity=2, quantity_only=True)
        setup_ordered_product_token_from_ordered_product_item(ordered_product_item)
        model = ordered_product_item

        ts = list(model.tokens)
        for t in ts:
            model.tokens.remove(t)

        result = target.build_dicts_from_ordered_product_item(model, ticket_number_issuer=self._makeIssuer())
        self.assertEqual(len(result), 2)
        seat_result, data = result[0]

        self.assert_basic_renderable_placeholder(data)
        self.assertEquals(data[u"席種名"], u":StockType:name")
        # self.assertEquals(data[u"席番"], u"") #xxx!

        self.assertEquals(data[u"発券番号"], "*NumberIssuer*")

    def test_build_ordered_product_item__with_seat__and_without_token(self):
        target = self._makeOne()
        ordered_product_item = get_ordered_product_item__full_relation(quantity=1, quantity_only=False)
        setup_seat_from_ordered_product_item(ordered_product_item)
        setup_ordered_product_token_from_ordered_product_item(ordered_product_item)

        model = ordered_product_item

        ts = list(model.tokens)
        for t in ts:
            model.tokens.remove(t)

        result = target.build_dicts_from_ordered_product_item(model, ticket_number_issuer=self._makeIssuer())


        self.assertEqual(len(result), 1)
        seat_result, data = result[0]

        self.assert_basic_renderable_placeholder(data)

        self.assertEquals(data[u"席種名"], u":StockType:name")
        self.assertEquals(data[u"席番"], u":Seat:name") #xxx!
        self.assertEquals(data[u"発券日時"], u"2000年 01月 01日 (土) 01時 13分")
        self.assertEquals(data[u"発券日時s"], u"2000/01/01 (土) 01:13")

        self.assertEquals(data[u"発券番号"], "*NumberIssuer*")


    ## carted product
    def test_build_carted_product_item__without_seat(self):
        from altair.app.ticketing.core.models import PaymentDeliveryMethodPair
        from altair.app.ticketing.core.models import PaymentMethod
        from altair.app.ticketing.core.models import DeliveryMethod
        from altair.app.ticketing.core.models import FeeTypeEnum
        target = self._makeOne()
        carted_product_item = get_carted_product_item__full_relation(quantity=2, quantity_only=True)
        payment_delivery_method_pair = PaymentDeliveryMethodPair(
            delivery_fee_per_order=0,
            delivery_fee_per_principal_ticket=300,
            delivery_fee_per_subticket=0,
            transaction_fee=200,
            system_fee=100,
            special_fee=300,
            special_fee_name=u'特別手数料',
            special_fee_type=FeeTypeEnum.PerUnit.v[0],
            payment_method = PaymentMethod(name=":PaymentMethod:name",
                                           fee=300,
                                           fee_type=1,
                                           payment_plugin_id=2),
            delivery_method = DeliveryMethod(name=":DeliveryMethod:name",
                                             fee_per_order=0,
                                             fee_per_principal_ticket=300,
                                             fee_per_subticket=0,
                                             delivery_plugin_id=2)
            )
        #hmm
        carted_product_item.carted_product.cart.payment_delivery_pair = payment_delivery_method_pair
        model = carted_product_item
        with mock.patch("altair.app.ticketing.core.models.Product.num_principal_tickets") as m: #xxx
            m.return_value = 0
            result = target.build_dicts_from_carted_product_item(model,
                                                                 payment_delivery_method_pair=payment_delivery_method_pair,
                                                                 now=datetime(2000, 1, 1, 1),
                                                                 ticket_number_issuer=self._makeIssuer()
                                                                 ) #attribute, number issuer, now

        self.assertEqual(len(result), 2)
        seat_result, data = result[0]
        # import json
        # print json.dumps(data, ensure_ascii=False, indent=2)

        self.assert_basic_renderable_placeholder(data)

        self.assertEquals(data[u"席種名"], u":StockType:name")
        # self.assertEquals(data[u"席番"], u":Seat:name") #xxx!
        self.assertEquals(data[u"発券日時"], u"\ufeff{{発券日時}}\ufeff")
        self.assertEquals(data[u"発券日時s"], u"\ufeff{{発券日時s}}\ufeff")
        # self.assertEquals(data[u"発券日時s"], u"2000/01/01 (土) 01:13")

        self.assertEquals(data[u"発券番号"], "*NumberIssuer*")


    def test_build_carted_product_item__with_seat(self):
        from altair.app.ticketing.core.models import PaymentDeliveryMethodPair
        from altair.app.ticketing.core.models import PaymentMethod
        from altair.app.ticketing.core.models import DeliveryMethod
        from altair.app.ticketing.core.models import Seat
        from altair.app.ticketing.core.models import FeeTypeEnum

        target = self._makeOne()
        carted_product_item = get_carted_product_item__full_relation(quantity=2, quantity_only=False)
        setup_seat_from_ordered_product_item(carted_product_item)
        payment_delivery_method_pair = PaymentDeliveryMethodPair(
            delivery_fee_per_order=0,
            delivery_fee_per_principal_ticket=300,
            delivery_fee_per_subticket=0,
            transaction_fee=200,
            system_fee=100,
            special_fee=400,
            special_fee_name=u'特別手数料',
            special_fee_type=FeeTypeEnum.PerUnit.v[0],
            payment_method = PaymentMethod(name=":PaymentMethod:name",
                                           fee=300,
                                           fee_type=1,
                                           payment_plugin_id=2),
            delivery_method = DeliveryMethod(name=":DeliveryMethod:name",
                                             fee_per_order=0,
                                             fee_per_principal_ticket=300,
                                             fee_per_subticket=0,
                                             delivery_plugin_id=2)
            )
        #hmm
        carted_product_item.carted_product.cart.payment_delivery_pair = payment_delivery_method_pair
        model = carted_product_item
        with mock.patch("altair.app.ticketing.core.models.Product.num_principal_tickets") as m: #xxx
            m.return_value = 0
            result = target.build_dicts_from_carted_product_item(model,
                                                                 payment_delivery_method_pair=payment_delivery_method_pair,
                                                                 now=datetime(2000, 1, 1, 1),
                                                                 ticket_number_issuer=self._makeIssuer()
                                                                 ) #attribute, number issuer, now

        self.assertEqual(len(result), 1)
        seat_result, data = result[0]
        # import json
        # print json.dumps(data, ensure_ascii=False, indent=2)
        self.assertEquals(data[u"イベント名"], u":Event:title")
        self.assertEquals(data[u"イベント名略称"], u":abbreviated_title")

        self.assertEquals(data[u"aux"][u"key"], u"value")

        self.assertEquals(data[u"パフォーマンス名"], u":Performance:name")
        self.assertEquals(data[u"対戦名"], u":Performance:name")
        self.assertEquals(data[u"公演コード"], u":code")
        self.assertEquals(data[u"開催日"], u"2000年 01月 01日 (土)")
        self.assertEquals(data[u"開場時刻"], u"00時 00分")
        self.assertEquals(data[u"開始時刻"], u"10時 00分")
        self.assertEquals(data[u"終了時刻"], u"23時 00分")
        self.assertEquals(data[u"開催日s"], u"2000/01/01 (土)")
        self.assertEquals(data[u"開場時刻s"], u"00:00")
        self.assertEquals(data[u"開始時刻s"], u"10:00")
        self.assertEquals(data[u"終了時刻s"], u"23:00")

        self.assertEqual(data[u"公演名略称"], u":PerformanceSetting:abbreviated_title")
        self.assertEqual(data[u"公演名備考"], u":PerformanceSetting:note")
        self.assertEqual(data[u"公演名副題"], u":PerformanceSetting:subtitle")

        self.assertEquals(data[u"会場名"], u":Venue:name")

        self.assertEquals(data[u"席種名"], u":StockType:name")
        self.assertEquals(data[u"席番"], u":Seat:name") #xxx!

        self.assertEquals(data[u"商品名"], u":ProductItem:name")
        self.assertEquals(data[u"商品価格"], u"12,000円")
        self.assertEquals(data[u"券種名"], u":ProductItem:name")
        self.assertEquals(data[u"チケット価格"], u"14,000円")

        self.assertEquals(data[u"予約番号"], u":order_no")
        self.assertEquals(data[u"受付番号"], u":order_no")
        self.assertEquals(data[u"注文番号"], u":order_no")
        self.assertEquals(data[u"注文日時"], u"2000年 01月 01日 (土) 01時 00分")
        self.assertEquals(data[u"受付日時"], u"2000年 01月 01日 (土) 01時 00分")
        self.assertEquals(data[u"発券日時"], u"\ufeff{{発券日時}}\ufeff")
        # self.assertEquals(data[u"発券日時"], u"2000年 01月 01日 (土) 01時 13分")
        self.assertEquals(data[u"注文日時s"], u"2000/01/01 (土) 01:00")
        self.assertEquals(data[u"受付日時s"], u"2000/01/01 (土) 01:00")
        self.assertEquals(data[u"発券日時s"], u"\ufeff{{発券日時s}}\ufeff")
        # self.assertEquals(data[u"発券日時s"], u"2000/01/01 (土) 01:13")

        #self.assertEquals(data[u"発券番号"], "*NumberIssuer*")

class BuilderItCoverCreateTest(_IntegrationAssertionMixin, unittest.TestCase):
    """see: https://redmine.ticketstar.jp/issues/5138"""
    def tearDown(self):
        transaction.abort()

    def _getTarget(self):
        from altair.app.ticketing.tickets.vars_builder import TicketCoverDictBuilder
        return TicketCoverDictBuilder

    def _makeOne(self, *args, **kwargs):
        from altair.app.ticketing.formatter import Japanese_Japan_Formatter
        return self._getTarget()(Japanese_Japan_Formatter(), *args, **kwargs)

    def _makeIssuer(self):
        return lambda x: "*NumberIssuer*"

    def test(self):
        ordered_product_item = get_ordered_product_item__full_relation(1, False)
        target = self._makeOne()
        result = target.build_dict_from_order(ordered_product_item.ordered_product.order)
        self.assertEqual(result[u'氏名'], u':last_name :first_name')
        self.assertEqual(result[u'氏名カナ'], u':last_name_kana :first_name_kana')
