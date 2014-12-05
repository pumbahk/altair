# encoding: utf-8

import unittest
import mock
import itertools
from decimal import Decimal
from pyramid import testing
from datetime import datetime
from altair.app.ticketing.core.testing import CoreTestMixin
from altair.app.ticketing.testing import _setup_db, _teardown_db


class ImportCSVParserTest(unittest.TestCase, CoreTestMixin):
    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _getTarget(self):
        from .importer import ImportCSVParser
        return ImportCSVParser

    def _pick_seats(self, stock, quantity):
        from altair.app.ticketing.core.models import SeatStatusEnum
        assert stock in self.stocks
       
        result = []
        for seat in self.seats:
            if seat.stock == stock and seat.status == SeatStatusEnum.Vacant.v:
                result.append(seat)
                if len(result) == quantity:
                    break
        else:
            assert False, 'len(result) < quantity'
        return result

    def setUp(self):
        self.request = testing.DummyRequest()
        self.session = _setup_db(
            modules=[
                'altair.app.ticketing.core.models',
                'altair.app.ticketing.lots.models',
                'altair.app.ticketing.orders.models',
                'altair.app.ticketing.users.models',
                'altair.app.ticketing.operators.models',
                ]
            )
        CoreTestMixin.setUp(self)
        from altair.app.ticketing.cart.models import CartSetting
        from altair.app.ticketing.users.models import Membership, MemberGroup, Member, User, UserCredential
        from altair.app.ticketing.core.models import SalesSegmentGroup, SalesSegment, Event, OrganizationSetting, EventSetting
        from altair.app.ticketing.operators.models import Operator
        self.cart_settings = [
            CartSetting(
                organization=self.organization,
                name=u'default'
                ),
            CartSetting(
                organization=self.organization,
                name=u'event'
                ),
            CartSetting(
                organization=self.organization,
                name=u'another_event'
                ),
            CartSetting(
                organization=self.organization,
                name=u'duplicate'
                ),
            CartSetting(
                organization=self.organization,
                name=u'duplicate'
                ),
            ]
        for cart_setting in self.cart_settings:
            self.session.add(cart_setting)
        self.session.flush()
        self.organization.settings = [
            OrganizationSetting(cart_setting=self.cart_settings[0]),
            ]
        self.another_event = Event(
            organization=self.organization,
            title=u'他のイベント',
            setting=EventSetting(cart_setting=self.cart_settings[2])
            )
        self.session.add(self.another_event)
        self.stock_types = self._create_stock_types(3)
        self.stocks = self._create_stocks(self.stock_types, 10)
        self.seats = self._create_seats(self.stocks[0:2])
        self.sales_segment_group = SalesSegmentGroup(name=u'存在する販売区分グループ', event=self.event)
        self.session.add(self.sales_segment_group)
        self.another_sales_segment_group = SalesSegmentGroup(name=u'存在する販売区分グループ', event=self.another_event)
        self.session.add(self.another_sales_segment_group)
        self.payment_delivery_method_pairs = self._create_payment_delivery_method_pairs(self.sales_segment_group)
        self.sales_segment = SalesSegment(
            sales_segment_group=self.sales_segment_group,
            payment_delivery_method_pairs=self.payment_delivery_method_pairs,
            performance=self.performance
            )
        self.products = self._create_products(self.stocks, sales_segment=self.sales_segment)
        self.operator = Operator()
        self.session.add(self.operator)
        self.existing_orders = [
            self._create_order(
                [(self.products[0], 2),],
                self.sales_segment,
                self.payment_delivery_method_pairs[0],
                order_no='YY0000000000'
                ),

            self._create_order(
                [(self.products[0], 2), (self.products[1], 1)],
                self.sales_segment,
                self.payment_delivery_method_pairs[0],
                order_no='YY0000000001'
                ),
            ]
        self.membership = Membership(organization=self.organization, name=u'会員種別名')
        self.session.add(self.membership)
        self.membergroup = MemberGroup(membership=self.membership, name=u'会員グループ名')
        self.session.add(self.membergroup)
        self.members = [
            Member(
                user=User(user_credential=[UserCredential(auth_identifier=u'aho', membership=self.membership)]),
                membergroup=self.membergroup
                ),
            Member(
                user=User(user_credential=[UserCredential(auth_identifier=u'alfred', membership=self.membership)]),
                membergroup=self.membergroup
                ),
            ]
        self.session.flush()
        self.config = testing.setUp(settings={
            'altair.cart.completion_page.temporary_store.cookie_name': 'xxx',
            'altair.cart.completion_page.temporary_store.secret': 'xxx',
            })
        self.config.include('altair.app.ticketing.cart.setup_components')

    def tearDown(self):
        testing.tearDown()
        _teardown_db()
    
    @mock.patch('altair.app.ticketing.core.api.get_next_order_no')
    def test_create_no_errors(self, get_next_order_no):
        from .models import OrderImportTask, ImportTypeEnum, ImportStatusEnum, AllocationModeEnum
        from altair.app.ticketing.payments.plugins import RESERVE_NUMBER_PAYMENT_PLUGIN_ID, RESERVE_NUMBER_DELIVERY_PLUGIN_ID
        task = OrderImportTask(
            organization=self.organization,
            operator=self.operator,
            import_type=ImportTypeEnum.Create.v,
            allocation_mode=AllocationModeEnum.NoAutoAllocation.v,
            status=ImportStatusEnum.Waiting.v,
            count=0
            )
        get_next_order_no.return_value = 'XX0000000000'
        target = self._makeOne(self.request, self.session, task, self.organization, performance=self.performance)
        proto_orders, errors = target([
            {
                u'order.order_no': u'予約番号',
                u'order.status': u'ステータス',
                u'order.payment_status': u'決済ステータス',
                u'order.created_at': u'',
                u'order.paid_at': u'',
                u'order.delivered_at': u'配送日時',
                u'order.canceled_at': u'キャンセル日時',
                u'order.total_amount': u'110',
                u'order.transaction_fee': u'30',
                u'order.delivery_fee': u'20',
                u'order.system_fee': u'10',
                u'order.special_fee': u'40',
                u'order.margin': u'内手数料金額',
                u'order.note': u'メモ',
                u'order.special_fee_name': u'特別手数料名',
                u'sej_order.billing_number': u'SEJ払込票番号',
                u'sej_order.exchange_number': u'SEJ引換票番号',
                u'user_profile.last_name': u'姓',
                u'user_profile.first_name': u'名',
                u'user_profile.last_name_kana': u'姓(カナ)',
                u'user_profile.first_name_kana': u'名(カナ)',
                u'user_profile.nick_name': u'ニックネーム',
                u'user_profile.sex': u'性別',
                u'membership.name': u'会員種別名',
                u'membergroup.name': u'会員グループ名',
                u'user_credential.auth_identifier': u'aho',
                u'shipping_address.last_name': u'配送先姓',
                u'shipping_address.first_name': u'配送先名',
                u'shipping_address.last_name_kana': u'配送先姓(カナ)',
                u'shipping_address.first_name_kana': u'配送先名(カナ)',
                u'shipping_address.zip': u'郵便番号',
                u'shipping_address.country': u'国',
                u'shipping_address.prefecture': u'都道府県',
                u'shipping_address.city': u'市区町村',
                u'shipping_address.address_1': u'住所1',
                u'shipping_address.address_2': u'住所2',
                u'shipping_address.tel_1': u'電話番号1',
                u'shipping_address.tel_2': u'電話番号2',
                u'shipping_address.fax': u'FAX',
                u'shipping_address.email_1': u'メールアドレス1',
                u'shipping_address.email_2': u'メールアドレス2',
                u'payment_method.name': u'RESERVE_NUMBER',
                u'delivery_method.name': u'RESERVE_NUMBER',
                u'event.title': u'イベント',
                u'performance.name': u'パフォーマンス',
                u'performance.code': u'ABCDEFGH',
                u'performance.start_on': u'公演日',
                u'venue.name': u'会場',
                u'ordered_product.price': u'10',
                u'ordered_product.quantity': u'1',
                u'ordered_product.product.name': u'A',
                u'ordered_product.product.sales_segment.sales_segment_group.name': u'存在する販売区分グループ',
                u'ordered_product.product.sales_segment.margin_ratio': u'販売手数料率',
                u'ordered_product_item.product_item.name': u'product_item_of_A',
                u'ordered_product_item.price': u'10',
                u'ordered_product_item.quantity': u'1',
                u'ordered_product_item.print_histories': u'発券作業者',
                u'mail_magazine.mail_permission': u'メールマガジン受信可否',
                u'seat.name': u'Seat A-0',
                },
            {
                u'order.order_no': u'予約番号',
                u'order.status': u'ステータス',
                u'order.payment_status': u'決済ステータス',
                u'order.created_at': u'',
                u'order.paid_at': u'',
                u'order.delivered_at': u'配送日時',
                u'order.canceled_at': u'キャンセル日時',
                u'order.total_amount': u'110',
                u'order.transaction_fee': u'30',
                u'order.delivery_fee': u'20',
                u'order.system_fee': u'10',
                u'order.special_fee': u'40',
                u'order.margin': u'内手数料金額',
                u'order.note': u'メモ',
                u'order.special_fee_name': u'特別手数料名',
                u'sej_order.billing_number': u'SEJ払込票番号',
                u'sej_order.exchange_number': u'SEJ引換票番号',
                u'user_profile.last_name': u'姓',
                u'user_profile.first_name': u'名',
                u'user_profile.last_name_kana': u'姓(カナ)',
                u'user_profile.first_name_kana': u'名(カナ)',
                u'user_profile.nick_name': u'ニックネーム',
                u'user_profile.sex': u'性別',
                u'membership.name': u'会員種別名',
                u'membergroup.name': u'会員グループ名',
                u'user_credential.auth_identifier': u'aho',
                u'shipping_address.last_name': u'配送先姓',
                u'shipping_address.first_name': u'配送先名',
                u'shipping_address.last_name_kana': u'配送先姓(カナ)',
                u'shipping_address.first_name_kana': u'配送先名(カナ)',
                u'shipping_address.zip': u'郵便番号',
                u'shipping_address.country': u'国',
                u'shipping_address.prefecture': u'都道府県',
                u'shipping_address.city': u'市区町村',
                u'shipping_address.address_1': u'住所1',
                u'shipping_address.address_2': u'住所2',
                u'shipping_address.tel_1': u'電話番号1',
                u'shipping_address.tel_2': u'電話番号2',
                u'shipping_address.fax': u'FAX',
                u'shipping_address.email_1': u'メールアドレス1',
                u'shipping_address.email_2': u'メールアドレス2',
                u'payment_method.name': u'RESERVE_NUMBER',
                u'delivery_method.name': u'RESERVE_NUMBER',
                u'event.title': u'イベント',
                u'performance.name': u'パフォーマンス',
                u'performance.code': u'ABCDEFGH',
                u'performance.start_on': u'公演日',
                u'venue.name': u'会場',
                u'ordered_product.price': u'10',
                u'ordered_product.quantity': u'1',
                u'ordered_product.product.name': u'B',
                u'ordered_product.product.sales_segment.sales_segment_group.name': u'存在する販売区分グループ',
                u'ordered_product.product.sales_segment.margin_ratio': u'販売手数料率',
                u'ordered_product_item.product_item.name': u'product_item_of_B',
                u'ordered_product_item.price': u'10',
                u'ordered_product_item.quantity': u'1',
                u'ordered_product_item.print_histories': u'発券作業者',
                u'mail_magazine.mail_permission': u'メールマガジン受信可否',
                u'seat.name': u'',
                }
            ])
        self.assertEqual(errors, {})
        self.assertEqual(len(proto_orders), 1)
        stock_a_quantity = self.stocks[0].stock_status.quantity
        stock_b_quantity = self.stocks[1].stock_status.quantity
        proto_order = iter(proto_orders.values()).next()
        self.assertTrue(get_next_order_no.called_with(self.request, self.organization))
        self.assertEqual(proto_order.order_no, 'XX0000000000')
        self.assertEqual(len(proto_order.items), 2)
        self.assertEqual(proto_order.items[0].product, self.products[0])
        self.assertEqual(len(proto_order.items[0].elements), 1)
        self.assertEqual(proto_order.items[0].elements[0].product_item, self.products[0].items[0])
        self.assertEqual(len(proto_order.items[0].elements[0].seats), 1)
        self.assertEqual(len(proto_order.items[0].elements[0].tokens), 1)
        self.assertEqual(proto_order.items[1].product, self.products[1])
        self.assertEqual(proto_order.items[1].elements[0].product_item, self.products[1].items[0])
        self.assertEqual(len(proto_order.items[1].elements), 1)
        self.assertEqual(len(proto_order.items[1].elements[0].seats), 0)
        self.assertEqual(len(proto_order.items[1].elements[0].tokens), 1)
        self.assertEqual(proto_order.note, u'メモ')
        self.assertEqual(proto_order.payment_delivery_pair.payment_method, self.payment_methods[RESERVE_NUMBER_PAYMENT_PLUGIN_ID])
        self.assertEqual(proto_order.payment_delivery_pair.delivery_method, self.delivery_methods[RESERVE_NUMBER_DELIVERY_PLUGIN_ID])
        self.assertEqual(proto_order.shipping_address.last_name,  u'配送先姓')
        self.assertEqual(proto_order.shipping_address.first_name,  u'配送先名')
        self.assertEqual(proto_order.shipping_address.last_name_kana,  u'配送先姓(カナ)')
        self.assertEqual(proto_order.shipping_address.first_name_kana,  u'配送先名(カナ)')
        self.assertEqual(proto_order.shipping_address.zip,  u'郵便番号')
        self.assertEqual(proto_order.shipping_address.country,  u'国')
        self.assertEqual(proto_order.shipping_address.prefecture,  u'都道府県')
        self.assertEqual(proto_order.shipping_address.city,  u'市区町村')
        self.assertEqual(proto_order.shipping_address.address_1,  u'住所1')
        self.assertEqual(proto_order.shipping_address.address_2,  u'住所2')
        self.assertEqual(proto_order.shipping_address.tel_1,  u'電話番号1')
        self.assertEqual(proto_order.shipping_address.tel_2,  u'電話番号2')
        self.assertEqual(proto_order.shipping_address.fax,  u'FAX')
        self.assertEqual(proto_order.shipping_address.email_1,  u'メールアドレス1')
        self.assertEqual(proto_order.shipping_address.email_2,  u'メールアドレス2')
        self.assertEqual(self.stocks[0].stock_status.quantity, stock_a_quantity)
        self.assertEqual(self.stocks[1].stock_status.quantity, stock_b_quantity)

    @mock.patch('altair.app.ticketing.core.api.get_next_order_no')
    def test_create_or_update_no_errors(self, get_next_order_no):
        from .models import OrderImportTask, ImportTypeEnum, ImportStatusEnum, AllocationModeEnum
        from altair.app.ticketing.payments.plugins import RESERVE_NUMBER_PAYMENT_PLUGIN_ID, RESERVE_NUMBER_DELIVERY_PLUGIN_ID
        task = OrderImportTask(
            organization=self.organization,
            operator=self.operator,
            import_type=ImportTypeEnum.Create.v | ImportTypeEnum.Update.v,
            allocation_mode=AllocationModeEnum.NoAutoAllocation.v,
            status=ImportStatusEnum.Waiting.v,
            count=0
            )
        get_next_order_no.return_value = 'XX0000000000'
        target = self._makeOne(self.request, self.session, task, self.organization, performance=self.performance)
        proto_orders, errors = target([
            {
                u'order.order_no': u'予約番号',
                u'order.status': u'ステータス',
                u'order.payment_status': u'決済ステータス',
                u'order.created_at': u'',
                u'order.paid_at': u'',
                u'order.delivered_at': u'配送日時',
                u'order.canceled_at': u'キャンセル日時',
                u'order.total_amount': u'110',
                u'order.transaction_fee': u'30',
                u'order.delivery_fee': u'20',
                u'order.system_fee': u'10',
                u'order.special_fee': u'40',
                u'order.margin': u'内手数料金額',
                u'order.note': u'メモ',
                u'order.special_fee_name': u'特別手数料名',
                u'sej_order.billing_number': u'SEJ払込票番号',
                u'sej_order.exchange_number': u'SEJ引換票番号',
                u'user_profile.last_name': u'姓',
                u'user_profile.first_name': u'名',
                u'user_profile.last_name_kana': u'姓(カナ)',
                u'user_profile.first_name_kana': u'名(カナ)',
                u'user_profile.nick_name': u'ニックネーム',
                u'user_profile.sex': u'性別',
                u'membership.name': u'会員種別名',
                u'membergroup.name': u'会員グループ名',
                u'user_credential.auth_identifier': u'aho',
                u'shipping_address.last_name': u'配送先姓',
                u'shipping_address.first_name': u'配送先名',
                u'shipping_address.last_name_kana': u'配送先姓(カナ)',
                u'shipping_address.first_name_kana': u'配送先名(カナ)',
                u'shipping_address.zip': u'郵便番号',
                u'shipping_address.country': u'国',
                u'shipping_address.prefecture': u'都道府県',
                u'shipping_address.city': u'市区町村',
                u'shipping_address.address_1': u'住所1',
                u'shipping_address.address_2': u'住所2',
                u'shipping_address.tel_1': u'電話番号1',
                u'shipping_address.tel_2': u'電話番号2',
                u'shipping_address.fax': u'FAX',
                u'shipping_address.email_1': u'メールアドレス1',
                u'shipping_address.email_2': u'メールアドレス2',
                u'payment_method.name': u'RESERVE_NUMBER',
                u'delivery_method.name': u'RESERVE_NUMBER',
                u'event.title': u'イベント',
                u'performance.name': u'パフォーマンス',
                u'performance.code': u'ABCDEFGH',
                u'performance.start_on': u'公演日',
                u'venue.name': u'会場',
                u'ordered_product.price': u'10',
                u'ordered_product.quantity': u'1',
                u'ordered_product.product.name': u'A',
                u'ordered_product.product.sales_segment.sales_segment_group.name': u'存在する販売区分グループ',
                u'ordered_product.product.sales_segment.margin_ratio': u'販売手数料率',
                u'ordered_product_item.product_item.name': u'product_item_of_A',
                u'ordered_product_item.price': u'10',
                u'ordered_product_item.quantity': u'1',
                u'ordered_product_item.print_histories': u'発券作業者',
                u'mail_magazine.mail_permission': u'メールマガジン受信可否',
                u'seat.name': u'Seat A-0',
                },
            {
                u'order.order_no': u'予約番号',
                u'order.status': u'ステータス',
                u'order.payment_status': u'決済ステータス',
                u'order.created_at': u'',
                u'order.paid_at': u'',
                u'order.delivered_at': u'配送日時',
                u'order.canceled_at': u'キャンセル日時',
                u'order.total_amount': u'110',
                u'order.transaction_fee': u'30',
                u'order.delivery_fee': u'20',
                u'order.system_fee': u'10',
                u'order.special_fee': u'40',
                u'order.margin': u'内手数料金額',
                u'order.note': u'メモ',
                u'order.special_fee_name': u'特別手数料名',
                u'sej_order.billing_number': u'SEJ払込票番号',
                u'sej_order.exchange_number': u'SEJ引換票番号',
                u'user_profile.last_name': u'姓',
                u'user_profile.first_name': u'名',
                u'user_profile.last_name_kana': u'姓(カナ)',
                u'user_profile.first_name_kana': u'名(カナ)',
                u'user_profile.nick_name': u'ニックネーム',
                u'user_profile.sex': u'性別',
                u'membership.name': u'会員種別名',
                u'membergroup.name': u'会員グループ名',
                u'user_credential.auth_identifier': u'aho',
                u'shipping_address.last_name': u'配送先姓',
                u'shipping_address.first_name': u'配送先名',
                u'shipping_address.last_name_kana': u'配送先姓(カナ)',
                u'shipping_address.first_name_kana': u'配送先名(カナ)',
                u'shipping_address.zip': u'郵便番号',
                u'shipping_address.country': u'国',
                u'shipping_address.prefecture': u'都道府県',
                u'shipping_address.city': u'市区町村',
                u'shipping_address.address_1': u'住所1',
                u'shipping_address.address_2': u'住所2',
                u'shipping_address.tel_1': u'電話番号1',
                u'shipping_address.tel_2': u'電話番号2',
                u'shipping_address.fax': u'FAX',
                u'shipping_address.email_1': u'メールアドレス1',
                u'shipping_address.email_2': u'メールアドレス2',
                u'payment_method.name': u'RESERVE_NUMBER',
                u'delivery_method.name': u'RESERVE_NUMBER',
                u'event.title': u'イベント',
                u'performance.name': u'パフォーマンス',
                u'performance.code': u'ABCDEFGH',
                u'performance.start_on': u'公演日',
                u'venue.name': u'会場',
                u'ordered_product.price': u'10',
                u'ordered_product.quantity': u'1',
                u'ordered_product.product.name': u'B',
                u'ordered_product.product.sales_segment.sales_segment_group.name': u'存在する販売区分グループ',
                u'ordered_product.product.sales_segment.margin_ratio': u'販売手数料率',
                u'ordered_product_item.product_item.name': u'product_item_of_B',
                u'ordered_product_item.price': u'10',
                u'ordered_product_item.quantity': u'1',
                u'ordered_product_item.print_histories': u'発券作業者',
                u'mail_magazine.mail_permission': u'メールマガジン受信可否',
                u'seat.name': u'',
                }
            ])
        self.assertEqual(errors, {})
        self.assertEqual(len(proto_orders), 1)
        stock_a_quantity = self.stocks[0].stock_status.quantity
        stock_b_quantity = self.stocks[1].stock_status.quantity
        proto_order = iter(proto_orders.values()).next()
        self.assertTrue(get_next_order_no.called_with(self.request, self.organization))
        self.assertEqual(proto_order.order_no, 'XX0000000000')
        self.assertEqual(len(proto_order.items), 2)
        self.assertEqual(proto_order.items[0].product, self.products[0])
        self.assertEqual(len(proto_order.items[0].elements), 1)
        self.assertEqual(proto_order.items[0].elements[0].product_item, self.products[0].items[0])
        self.assertEqual(len(proto_order.items[0].elements[0].seats), 1)
        self.assertEqual(len(proto_order.items[0].elements[0].tokens), 1)
        self.assertEqual(proto_order.items[1].product, self.products[1])
        self.assertEqual(proto_order.items[1].elements[0].product_item, self.products[1].items[0])
        self.assertEqual(len(proto_order.items[1].elements), 1)
        self.assertEqual(len(proto_order.items[1].elements[0].seats), 0)
        self.assertEqual(len(proto_order.items[1].elements[0].tokens), 1)
        self.assertEqual(proto_order.note, u'メモ')
        self.assertEqual(proto_order.payment_delivery_pair.payment_method, self.payment_methods[RESERVE_NUMBER_PAYMENT_PLUGIN_ID])
        self.assertEqual(proto_order.payment_delivery_pair.delivery_method, self.delivery_methods[RESERVE_NUMBER_DELIVERY_PLUGIN_ID])
        self.assertEqual(proto_order.shipping_address.last_name,  u'配送先姓')
        self.assertEqual(proto_order.shipping_address.first_name,  u'配送先名')
        self.assertEqual(proto_order.shipping_address.last_name_kana,  u'配送先姓(カナ)')
        self.assertEqual(proto_order.shipping_address.first_name_kana,  u'配送先名(カナ)')
        self.assertEqual(proto_order.shipping_address.zip,  u'郵便番号')
        self.assertEqual(proto_order.shipping_address.country,  u'国')
        self.assertEqual(proto_order.shipping_address.prefecture,  u'都道府県')
        self.assertEqual(proto_order.shipping_address.city,  u'市区町村')
        self.assertEqual(proto_order.shipping_address.address_1,  u'住所1')
        self.assertEqual(proto_order.shipping_address.address_2,  u'住所2')
        self.assertEqual(proto_order.shipping_address.tel_1,  u'電話番号1')
        self.assertEqual(proto_order.shipping_address.tel_2,  u'電話番号2')
        self.assertEqual(proto_order.shipping_address.fax,  u'FAX')
        self.assertEqual(proto_order.shipping_address.email_1,  u'メールアドレス1')
        self.assertEqual(proto_order.shipping_address.email_2,  u'メールアドレス2')
        self.assertEqual(self.stocks[0].stock_status.quantity, stock_a_quantity)
        self.assertEqual(self.stocks[1].stock_status.quantity, stock_b_quantity)

    @mock.patch('altair.app.ticketing.core.api.get_next_order_no')
    def test_update_non_existent(self, get_next_order_no):
        from .models import OrderImportTask, ImportTypeEnum, ImportStatusEnum, AllocationModeEnum
        from altair.app.ticketing.payments.plugins import RESERVE_NUMBER_PAYMENT_PLUGIN_ID, RESERVE_NUMBER_DELIVERY_PLUGIN_ID
        task = OrderImportTask(
            organization=self.organization,
            operator=self.operator,
            import_type=ImportTypeEnum.Update.v,
            allocation_mode=AllocationModeEnum.NoAutoAllocation.v,
            status=ImportStatusEnum.Waiting.v,
            count=0
            )
        get_next_order_no.return_value = 'XX0000000000'
        target = self._makeOne(self.request, self.session, task, self.organization, performance=self.performance)
        proto_orders, errors = target([
            {
                u'order.order_no': u'予約番号',
                u'order.status': u'ステータス',
                u'order.payment_status': u'決済ステータス',
                u'order.created_at': u'',
                u'order.paid_at': u'',
                u'order.delivered_at': u'配送日時',
                u'order.canceled_at': u'キャンセル日時',
                u'order.total_amount': u'110',
                u'order.transaction_fee': u'30',
                u'order.delivery_fee': u'20',
                u'order.system_fee': u'10',
                u'order.special_fee': u'40',
                u'order.margin': u'内手数料金額',
                u'order.note': u'メモ',
                u'order.special_fee_name': u'特別手数料名',
                u'sej_order.billing_number': u'SEJ払込票番号',
                u'sej_order.exchange_number': u'SEJ引換票番号',
                u'user_profile.last_name': u'姓',
                u'user_profile.first_name': u'名',
                u'user_profile.last_name_kana': u'姓(カナ)',
                u'user_profile.first_name_kana': u'名(カナ)',
                u'user_profile.nick_name': u'ニックネーム',
                u'user_profile.sex': u'性別',
                u'membership.name': u'会員種別名',
                u'membergroup.name': u'会員グループ名',
                u'user_credential.auth_identifier': u'aho',
                u'shipping_address.last_name': u'配送先姓',
                u'shipping_address.first_name': u'配送先名',
                u'shipping_address.last_name_kana': u'配送先姓(カナ)',
                u'shipping_address.first_name_kana': u'配送先名(カナ)',
                u'shipping_address.zip': u'郵便番号',
                u'shipping_address.country': u'国',
                u'shipping_address.prefecture': u'都道府県',
                u'shipping_address.city': u'市区町村',
                u'shipping_address.address_1': u'住所1',
                u'shipping_address.address_2': u'住所2',
                u'shipping_address.tel_1': u'電話番号1',
                u'shipping_address.tel_2': u'電話番号2',
                u'shipping_address.fax': u'FAX',
                u'shipping_address.email_1': u'メールアドレス1',
                u'shipping_address.email_2': u'メールアドレス2',
                u'payment_method.name': u'RESERVE_NUMBER',
                u'delivery_method.name': u'RESERVE_NUMBER',
                u'event.title': u'イベント',
                u'performance.name': u'パフォーマンス',
                u'performance.code': u'ABCDEFGH',
                u'performance.start_on': u'公演日',
                u'venue.name': u'会場',
                u'ordered_product.price': u'10',
                u'ordered_product.quantity': u'1',
                u'ordered_product.product.name': u'A',
                u'ordered_product.product.sales_segment.sales_segment_group.name': u'存在する販売区分グループ',
                u'ordered_product.product.sales_segment.margin_ratio': u'販売手数料率',
                u'ordered_product_item.product_item.name': u'product_item_of_A',
                u'ordered_product_item.price': u'10',
                u'ordered_product_item.quantity': u'1',
                u'ordered_product_item.print_histories': u'発券作業者',
                u'mail_magazine.mail_permission': u'メールマガジン受信可否',
                u'seat.name': u'Seat A-0',
                },
            {
                u'order.order_no': u'予約番号',
                u'order.status': u'ステータス',
                u'order.payment_status': u'決済ステータス',
                u'order.created_at': u'',
                u'order.paid_at': u'',
                u'order.delivered_at': u'配送日時',
                u'order.canceled_at': u'キャンセル日時',
                u'order.total_amount': u'110',
                u'order.transaction_fee': u'30',
                u'order.delivery_fee': u'20',
                u'order.system_fee': u'10',
                u'order.special_fee': u'40',
                u'order.margin': u'内手数料金額',
                u'order.note': u'メモ',
                u'order.special_fee_name': u'特別手数料名',
                u'sej_order.billing_number': u'SEJ払込票番号',
                u'sej_order.exchange_number': u'SEJ引換票番号',
                u'user_profile.last_name': u'姓',
                u'user_profile.first_name': u'名',
                u'user_profile.last_name_kana': u'姓(カナ)',
                u'user_profile.first_name_kana': u'名(カナ)',
                u'user_profile.nick_name': u'ニックネーム',
                u'user_profile.sex': u'性別',
                u'membership.name': u'会員種別名',
                u'membergroup.name': u'会員グループ名',
                u'user_credential.auth_identifier': u'aho',
                u'shipping_address.last_name': u'配送先姓',
                u'shipping_address.first_name': u'配送先名',
                u'shipping_address.last_name_kana': u'配送先姓(カナ)',
                u'shipping_address.first_name_kana': u'配送先名(カナ)',
                u'shipping_address.zip': u'郵便番号',
                u'shipping_address.country': u'国',
                u'shipping_address.prefecture': u'都道府県',
                u'shipping_address.city': u'市区町村',
                u'shipping_address.address_1': u'住所1',
                u'shipping_address.address_2': u'住所2',
                u'shipping_address.tel_1': u'電話番号1',
                u'shipping_address.tel_2': u'電話番号2',
                u'shipping_address.fax': u'FAX',
                u'shipping_address.email_1': u'メールアドレス1',
                u'shipping_address.email_2': u'メールアドレス2',
                u'payment_method.name': u'RESERVE_NUMBER',
                u'delivery_method.name': u'RESERVE_NUMBER',
                u'event.title': u'イベント',
                u'performance.name': u'パフォーマンス',
                u'performance.code': u'ABCDEFGH',
                u'performance.start_on': u'公演日',
                u'venue.name': u'会場',
                u'ordered_product.price': u'10',
                u'ordered_product.quantity': u'1',
                u'ordered_product.product.name': u'B',
                u'ordered_product.product.sales_segment.sales_segment_group.name': u'存在する販売区分グループ',
                u'ordered_product.product.sales_segment.margin_ratio': u'販売手数料率',
                u'ordered_product_item.product_item.name': u'product_item_of_B',
                u'ordered_product_item.price': u'10',
                u'ordered_product_item.quantity': u'1',
                u'ordered_product_item.print_histories': u'発券作業者',
                u'mail_magazine.mail_permission': u'メールマガジン受信可否',
                u'seat.name': u'',
                }
            ])
        self.assertEqual(errors[u'予約番号'].message, u'更新対象の注文が存在しません')

    @mock.patch('altair.app.ticketing.core.api.get_next_order_no')
    def test_update_different_payment_method(self, get_next_order_no):
        from .models import OrderImportTask, ImportTypeEnum, ImportStatusEnum, AllocationModeEnum
        from altair.app.ticketing.payments.plugins import RESERVE_NUMBER_PAYMENT_PLUGIN_ID, RESERVE_NUMBER_DELIVERY_PLUGIN_ID
        task = OrderImportTask(
            organization=self.organization,
            operator=self.operator,
            import_type=ImportTypeEnum.Update.v,
            allocation_mode=AllocationModeEnum.NoAutoAllocation.v,
            status=ImportStatusEnum.Waiting.v,
            count=0
            )
        get_next_order_no.return_value = 'XX0000000000'
        target = self._makeOne(self.request, self.session, task, self.organization, performance=self.performance)
        proto_orders, errors = target([
            {
                u'order.order_no': u'YY0000000000',
                u'order.status': u'ステータス',
                u'order.payment_status': u'決済ステータス',
                u'order.created_at': u'',
                u'order.paid_at': u'',
                u'order.delivered_at': u'配送日時',
                u'order.canceled_at': u'キャンセル日時',
                u'order.total_amount': u'110',
                u'order.transaction_fee': u'30',
                u'order.delivery_fee': u'20',
                u'order.system_fee': u'10',
                u'order.special_fee': u'40',
                u'order.margin': u'内手数料金額',
                u'order.note': u'メモ',
                u'order.special_fee_name': u'特別手数料名',
                u'sej_order.billing_number': u'SEJ払込票番号',
                u'sej_order.exchange_number': u'SEJ引換票番号',
                u'user_profile.last_name': u'姓',
                u'user_profile.first_name': u'名',
                u'user_profile.last_name_kana': u'姓(カナ)',
                u'user_profile.first_name_kana': u'名(カナ)',
                u'user_profile.nick_name': u'ニックネーム',
                u'user_profile.sex': u'性別',
                u'membership.name': u'会員種別名',
                u'membergroup.name': u'会員グループ名',
                u'user_credential.auth_identifier': u'aho',
                u'shipping_address.last_name': u'配送先姓',
                u'shipping_address.first_name': u'配送先名',
                u'shipping_address.last_name_kana': u'配送先姓(カナ)',
                u'shipping_address.first_name_kana': u'配送先名(カナ)',
                u'shipping_address.zip': u'郵便番号',
                u'shipping_address.country': u'国',
                u'shipping_address.prefecture': u'都道府県',
                u'shipping_address.city': u'市区町村',
                u'shipping_address.address_1': u'住所1',
                u'shipping_address.address_2': u'住所2',
                u'shipping_address.tel_1': u'電話番号1',
                u'shipping_address.tel_2': u'電話番号2',
                u'shipping_address.fax': u'FAX',
                u'shipping_address.email_1': u'メールアドレス1',
                u'shipping_address.email_2': u'メールアドレス2',
                u'payment_method.name': u'RESERVE_NUMBER',
                u'delivery_method.name': u'RESERVE_NUMBER',
                u'event.title': u'イベント',
                u'performance.name': u'パフォーマンス',
                u'performance.code': u'ABCDEFGH',
                u'performance.start_on': u'公演日',
                u'venue.name': u'会場',
                u'ordered_product.price': u'10',
                u'ordered_product.quantity': u'1',
                u'ordered_product.product.name': u'A',
                u'ordered_product.product.sales_segment.sales_segment_group.name': u'存在する販売区分グループ',
                u'ordered_product.product.sales_segment.margin_ratio': u'販売手数料率',
                u'ordered_product_item.product_item.name': u'product_item_of_A',
                u'ordered_product_item.price': u'10',
                u'ordered_product_item.quantity': u'1',
                u'ordered_product_item.print_histories': u'発券作業者',
                u'mail_magazine.mail_permission': u'メールマガジン受信可否',
                u'seat.name': u'Seat A-0',
                },
            ])
        self.assertIn('YY0000000000', errors)
        self.assertEquals(errors['YY0000000000'].message, u'更新対象の注文の決済方法と新しい注文の決済方法が異なっています')

    @mock.patch('altair.app.ticketing.core.api.get_next_order_no')
    def test_update_different_delivery_method(self, get_next_order_no):
        from .models import OrderImportTask, ImportTypeEnum, ImportStatusEnum, AllocationModeEnum
        from altair.app.ticketing.payments.plugins import RESERVE_NUMBER_PAYMENT_PLUGIN_ID, RESERVE_NUMBER_DELIVERY_PLUGIN_ID
        task = OrderImportTask(
            organization=self.organization,
            operator=self.operator,
            import_type=ImportTypeEnum.Update.v,
            allocation_mode=AllocationModeEnum.NoAutoAllocation.v,
            status=ImportStatusEnum.Waiting.v,
            count=0
            )
        get_next_order_no.return_value = 'XX0000000000'
        target = self._makeOne(self.request, self.session, task, self.organization, performance=self.performance)
        proto_orders, errors = target([
            {
                u'order.order_no': u'YY0000000000',
                u'order.status': u'ステータス',
                u'order.payment_status': u'決済ステータス',
                u'order.created_at': u'',
                u'order.paid_at': u'',
                u'order.delivered_at': u'配送日時',
                u'order.canceled_at': u'キャンセル日時',
                u'order.total_amount': u'110',
                u'order.transaction_fee': u'30',
                u'order.delivery_fee': u'20',
                u'order.system_fee': u'10',
                u'order.special_fee': u'40',
                u'order.margin': u'内手数料金額',
                u'order.note': u'メモ',
                u'order.special_fee_name': u'特別手数料名',
                u'sej_order.billing_number': u'SEJ払込票番号',
                u'sej_order.exchange_number': u'SEJ引換票番号',
                u'user_profile.last_name': u'姓',
                u'user_profile.first_name': u'名',
                u'user_profile.last_name_kana': u'姓(カナ)',
                u'user_profile.first_name_kana': u'名(カナ)',
                u'user_profile.nick_name': u'ニックネーム',
                u'user_profile.sex': u'性別',
                u'membership.name': u'会員種別名',
                u'membergroup.name': u'会員グループ名',
                u'user_credential.auth_identifier': u'aho',
                u'shipping_address.last_name': u'配送先姓',
                u'shipping_address.first_name': u'配送先名',
                u'shipping_address.last_name_kana': u'配送先姓(カナ)',
                u'shipping_address.first_name_kana': u'配送先名(カナ)',
                u'shipping_address.zip': u'郵便番号',
                u'shipping_address.country': u'国',
                u'shipping_address.prefecture': u'都道府県',
                u'shipping_address.city': u'市区町村',
                u'shipping_address.address_1': u'住所1',
                u'shipping_address.address_2': u'住所2',
                u'shipping_address.tel_1': u'電話番号1',
                u'shipping_address.tel_2': u'電話番号2',
                u'shipping_address.fax': u'FAX',
                u'shipping_address.email_1': u'メールアドレス1',
                u'shipping_address.email_2': u'メールアドレス2',
                u'payment_method.name': self.existing_orders[0].payment_delivery_pair.payment_method.name,
                u'delivery_method.name': u'RESERVE_NUMBER',
                u'event.title': u'イベント',
                u'performance.name': u'パフォーマンス',
                u'performance.code': u'ABCDEFGH',
                u'performance.start_on': u'公演日',
                u'venue.name': u'会場',
                u'ordered_product.price': u'10',
                u'ordered_product.quantity': u'1',
                u'ordered_product.product.name': u'A',
                u'ordered_product.product.sales_segment.sales_segment_group.name': u'存在する販売区分グループ',
                u'ordered_product.product.sales_segment.margin_ratio': u'販売手数料率',
                u'ordered_product_item.product_item.name': u'product_item_of_A',
                u'ordered_product_item.price': u'10',
                u'ordered_product_item.quantity': u'1',
                u'ordered_product_item.print_histories': u'発券作業者',
                u'mail_magazine.mail_permission': u'メールマガジン受信可否',
                u'seat.name': u'Seat A-0',
                },
            ])
        self.assertIn('YY0000000000', errors)
        self.assertEquals(errors['YY0000000000'].message, u'更新対象の注文の引取方法と新しい注文の引取方法が異なっています')

    @mock.patch('altair.app.ticketing.core.api.get_next_order_no')
    def test_update(self, get_next_order_no):
        from .models import OrderImportTask, ImportTypeEnum, ImportStatusEnum, AllocationModeEnum
        from altair.app.ticketing.payments.plugins import RESERVE_NUMBER_PAYMENT_PLUGIN_ID, RESERVE_NUMBER_DELIVERY_PLUGIN_ID
        task = OrderImportTask(
            organization=self.organization,
            operator=self.operator,
            import_type=ImportTypeEnum.Update.v,
            allocation_mode=AllocationModeEnum.NoAutoAllocation.v,
            status=ImportStatusEnum.Waiting.v,
            count=0
            )
        target = self._makeOne(self.request, self.session, task, self.organization, performance=self.performance)
        proto_orders, errors = target([
            {
                u'order.order_no': u'YY0000000000',
                u'order.status': u'ステータス',
                u'order.payment_status': u'決済ステータス',
                u'order.created_at': u'',
                u'order.paid_at': u'',
                u'order.delivered_at': u'配送日時',
                u'order.canceled_at': u'キャンセル日時',
                u'order.total_amount': u'110',
                u'order.transaction_fee': u'30',
                u'order.delivery_fee': u'20',
                u'order.system_fee': u'10',
                u'order.special_fee': u'40',
                u'order.margin': u'内手数料金額',
                u'order.note': u'メモ',
                u'order.special_fee_name': u'特別手数料名',
                u'sej_order.billing_number': u'SEJ払込票番号',
                u'sej_order.exchange_number': u'SEJ引換票番号',
                u'user_profile.last_name': u'姓',
                u'user_profile.first_name': u'名',
                u'user_profile.last_name_kana': u'姓(カナ)',
                u'user_profile.first_name_kana': u'名(カナ)',
                u'user_profile.nick_name': u'ニックネーム',
                u'user_profile.sex': u'性別',
                u'membership.name': u'会員種別名',
                u'membergroup.name': u'会員グループ名',
                u'user_credential.auth_identifier': u'aho',
                u'shipping_address.last_name': u'配送先姓',
                u'shipping_address.first_name': u'配送先名',
                u'shipping_address.last_name_kana': u'配送先姓(カナ)',
                u'shipping_address.first_name_kana': u'配送先名(カナ)',
                u'shipping_address.zip': u'郵便番号',
                u'shipping_address.country': u'国',
                u'shipping_address.prefecture': u'都道府県',
                u'shipping_address.city': u'市区町村',
                u'shipping_address.address_1': u'住所1',
                u'shipping_address.address_2': u'住所2',
                u'shipping_address.tel_1': u'電話番号1',
                u'shipping_address.tel_2': u'電話番号2',
                u'shipping_address.fax': u'FAX',
                u'shipping_address.email_1': u'メールアドレス1',
                u'shipping_address.email_2': u'メールアドレス2',
                u'payment_method.name': self.existing_orders[0].payment_delivery_pair.payment_method.name,
                u'delivery_method.name': self.existing_orders[0].payment_delivery_pair.delivery_method.name,
                u'event.title': u'イベント',
                u'performance.name': u'パフォーマンス',
                u'performance.code': u'ABCDEFGH',
                u'performance.start_on': u'公演日',
                u'venue.name': u'会場',
                u'ordered_product.price': u'10',
                u'ordered_product.quantity': u'1',
                u'ordered_product.product.name': u'A',
                u'ordered_product.product.sales_segment.sales_segment_group.name': u'存在する販売区分グループ',
                u'ordered_product.product.sales_segment.margin_ratio': u'販売手数料率',
                u'ordered_product_item.product_item.name': u'product_item_of_A',
                u'ordered_product_item.price': u'10',
                u'ordered_product_item.quantity': u'1',
                u'ordered_product_item.print_histories': u'発券作業者',
                u'mail_magazine.mail_permission': u'メールマガジン受信可否',
                u'seat.name': u'Seat A-0',
                },
            {
                u'order.order_no': u'YY0000000000',
                u'order.status': u'ステータス',
                u'order.payment_status': u'決済ステータス',
                u'order.created_at': u'',
                u'order.paid_at': u'',
                u'order.delivered_at': u'配送日時',
                u'order.canceled_at': u'キャンセル日時',
                u'order.total_amount': u'110',
                u'order.transaction_fee': u'30',
                u'order.delivery_fee': u'20',
                u'order.system_fee': u'10',
                u'order.special_fee': u'40',
                u'order.margin': u'内手数料金額',
                u'order.note': u'メモ',
                u'order.special_fee_name': u'特別手数料名',
                u'sej_order.billing_number': u'SEJ払込票番号',
                u'sej_order.exchange_number': u'SEJ引換票番号',
                u'user_profile.last_name': u'姓',
                u'user_profile.first_name': u'名',
                u'user_profile.last_name_kana': u'姓(カナ)',
                u'user_profile.first_name_kana': u'名(カナ)',
                u'user_profile.nick_name': u'ニックネーム',
                u'user_profile.sex': u'性別',
                u'membership.name': u'会員種別名',
                u'membergroup.name': u'会員グループ名',
                u'user_credential.auth_identifier': u'aho',
                u'shipping_address.last_name': u'配送先姓',
                u'shipping_address.first_name': u'配送先名',
                u'shipping_address.last_name_kana': u'配送先姓(カナ)',
                u'shipping_address.first_name_kana': u'配送先名(カナ)',
                u'shipping_address.zip': u'郵便番号',
                u'shipping_address.country': u'国',
                u'shipping_address.prefecture': u'都道府県',
                u'shipping_address.city': u'市区町村',
                u'shipping_address.address_1': u'住所1',
                u'shipping_address.address_2': u'住所2',
                u'shipping_address.tel_1': u'電話番号1',
                u'shipping_address.tel_2': u'電話番号2',
                u'shipping_address.fax': u'FAX',
                u'shipping_address.email_1': u'メールアドレス1',
                u'shipping_address.email_2': u'メールアドレス2',
                u'payment_method.name': self.payment_delivery_method_pairs[0].payment_method.name,
                u'delivery_method.name': self.payment_delivery_method_pairs[0].delivery_method.name,
                u'event.title': u'イベント',
                u'performance.name': u'パフォーマンス',
                u'performance.code': u'ABCDEFGH',
                u'performance.start_on': u'公演日',
                u'venue.name': u'会場',
                u'ordered_product.price': u'10',
                u'ordered_product.quantity': u'1',
                u'ordered_product.product.name': u'B',
                u'ordered_product.product.sales_segment.sales_segment_group.name': u'存在する販売区分グループ',
                u'ordered_product.product.sales_segment.margin_ratio': u'販売手数料率',
                u'ordered_product_item.product_item.name': u'product_item_of_B',
                u'ordered_product_item.price': u'10',
                u'ordered_product_item.quantity': u'1',
                u'ordered_product_item.print_histories': u'発券作業者',
                u'mail_magazine.mail_permission': u'メールマガジン受信可否',
                u'seat.name': u'',
                }
            ])
        self.assertEqual(errors, {})
        self.assertEqual(len(proto_orders), 1)
        stock_a_quantity = self.stocks[0].stock_status.quantity
        stock_b_quantity = self.stocks[1].stock_status.quantity
        proto_order = iter(proto_orders.values()).next()
        self.assertTrue(get_next_order_no.called_with(self.request, self.organization))
        self.assertEqual(proto_order.order_no, 'YY0000000000')
        self.assertEqual(len(proto_order.items), 2)
        self.assertEqual(proto_order.items[0].product, self.products[0])
        self.assertEqual(len(proto_order.items[0].elements), 1)
        self.assertEqual(proto_order.items[0].elements[0].product_item, self.products[0].items[0])
        self.assertEqual(len(proto_order.items[0].elements[0].seats), 1)
        self.assertEqual(len(proto_order.items[0].elements[0].tokens), 1)
        self.assertEqual(proto_order.items[1].product, self.products[1])
        self.assertEqual(proto_order.items[1].elements[0].product_item, self.products[1].items[0])
        self.assertEqual(len(proto_order.items[1].elements), 1)
        self.assertEqual(len(proto_order.items[1].elements[0].seats), 0)
        self.assertEqual(len(proto_order.items[1].elements[0].tokens), 1)
        self.assertEqual(proto_order.note, u'メモ')
        self.assertEqual(proto_order.payment_delivery_pair.payment_method, self.payment_delivery_method_pairs[0].payment_method)
        self.assertEqual(proto_order.payment_delivery_pair.delivery_method, self.payment_delivery_method_pairs[0].delivery_method)
        self.assertEqual(proto_order.shipping_address.last_name,  u'配送先姓')
        self.assertEqual(proto_order.shipping_address.first_name,  u'配送先名')
        self.assertEqual(proto_order.shipping_address.last_name_kana,  u'配送先姓(カナ)')
        self.assertEqual(proto_order.shipping_address.first_name_kana,  u'配送先名(カナ)')
        self.assertEqual(proto_order.shipping_address.zip,  u'郵便番号')
        self.assertEqual(proto_order.shipping_address.country,  u'国')
        self.assertEqual(proto_order.shipping_address.prefecture,  u'都道府県')
        self.assertEqual(proto_order.shipping_address.city,  u'市区町村')
        self.assertEqual(proto_order.shipping_address.address_1,  u'住所1')
        self.assertEqual(proto_order.shipping_address.address_2,  u'住所2')
        self.assertEqual(proto_order.shipping_address.tel_1,  u'電話番号1')
        self.assertEqual(proto_order.shipping_address.tel_2,  u'電話番号2')
        self.assertEqual(proto_order.shipping_address.fax,  u'FAX')
        self.assertEqual(proto_order.shipping_address.email_1,  u'メールアドレス1')
        self.assertEqual(proto_order.shipping_address.email_2,  u'メールアドレス2')
        self.assertEqual(self.stocks[0].stock_status.quantity, stock_a_quantity)
        self.assertEqual(self.stocks[1].stock_status.quantity, stock_b_quantity)

class OrderImporterTest(unittest.TestCase, CoreTestMixin):
    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _getTarget(self):
        from .importer import OrderImporter
        return OrderImporter

    def _pick_seats(self, stock, quantity):
        from altair.app.ticketing.core.models import SeatStatusEnum
        assert stock in self.stocks
       
        result = []
        for seat in self.seats:
            if seat.stock == stock and seat.status == SeatStatusEnum.Vacant.v:
                result.append(seat)
                if len(result) == quantity:
                    break
        else:
            assert False, 'len(result) < quantity'
        return result

    def setUp(self):
        self.request = testing.DummyRequest()
        self.session = _setup_db(
            modules=[
                'altair.app.ticketing.core.models',
                'altair.app.ticketing.lots.models',
                'altair.app.ticketing.orders.models',
                'altair.app.ticketing.users.models',
                'altair.app.ticketing.operators.models',
                ]
            )
        CoreTestMixin.setUp(self)
        from altair.app.ticketing.cart.models import CartSetting
        from altair.app.ticketing.users.models import Membership, MemberGroup, Member, User, UserCredential
        from altair.app.ticketing.core.models import SalesSegmentGroup, SalesSegment, Event, OrganizationSetting, EventSetting
        from altair.app.ticketing.operators.models import Operator
        self.cart_settings = [
            CartSetting(
                organization=self.organization,
                name=u'default'
                ),
            CartSetting(
                organization=self.organization,
                name=u'event'
                ),
            CartSetting(
                organization=self.organization,
                name=u'another_event'
                ),
            CartSetting(
                organization=self.organization,
                name=u'duplicate'
                ),
            CartSetting(
                organization=self.organization,
                name=u'duplicate'
                ),
            ]
        for cart_setting in self.cart_settings:
            self.session.add(cart_setting)
        self.session.flush()
        self.organization.settings = [
            OrganizationSetting(cart_setting=self.cart_settings[0]),
            ]
        self.another_event = Event(
            organization=self.organization,
            title=u'他のイベント',
            setting=EventSetting(cart_setting=self.cart_settings[2])
            )
        self.session.add(self.another_event)
        self.stock_types = self._create_stock_types(4)
        self.stocks = self._create_stocks(self.stock_types, 10)
        self.seats = self._create_seats(self.stocks)
        self.sales_segment_group = SalesSegmentGroup(name=u'存在する販売区分グループ', event=self.event)
        self.session.add(self.sales_segment_group)
        self.another_sales_segment_group = SalesSegmentGroup(name=u'存在する販売区分グループ', event=self.another_event)
        self.session.add(self.another_sales_segment_group)
        self.payment_delivery_method_pairs = self._create_payment_delivery_method_pairs(
            self.sales_segment_group,
            transaction_fee=30,
            delivery_fee_per_order=20,
            delivery_fee_per_principal_ticket=0,
            delivery_fee_per_subticket=0,
            system_fee=10,
            special_fee=40)
        self.sales_segment = SalesSegment(
            sales_segment_group=self.sales_segment_group,
            payment_delivery_method_pairs=self.payment_delivery_method_pairs,
            performance=self.performance
            )
        self.products = self._create_products(self.stocks, sales_segment=self.sales_segment)
        self.operator = Operator()
        self.session.add(self.operator)
        self.existing_orders = [
            self._create_order(
                [(self.products[0], 2),],
                self.sales_segment,
                self.payment_delivery_method_pairs[0],
                order_no='YY0000000000'
                ),

            self._create_order(
                [(self.products[0], 2), (self.products[1], 1)],
                self.sales_segment,
                self.payment_delivery_method_pairs[0],
                order_no='YY0000000001'
                ),
            ]
        self.membership = Membership(organization=self.organization, name=u'会員種別名')
        self.session.add(self.membership)
        self.membergroup = MemberGroup(membership=self.membership, name=u'会員グループ名')
        self.session.add(self.membergroup)
        self.members = [
            Member(
                user=User(user_credential=[UserCredential(auth_identifier=u'aho', membership=self.membership)]),
                membergroup=self.membergroup
                ),
            Member(
                user=User(user_credential=[UserCredential(auth_identifier=u'alfred', membership=self.membership)]),
                membergroup=self.membergroup
                ),
            ]
        self.session.flush()
        self.config = testing.setUp(settings={
            'altair.cart.completion_page.temporary_store.cookie_name': 'xxx',
            'altair.cart.completion_page.temporary_store.secret': 'xxx',
            })
        self.config.include('altair.app.ticketing.cart.setup_components')
        self._lookup_plugin_patch = mock.patch('altair.app.ticketing.orders.importer.lookup_plugin')
        self._lookup_plugin = self._lookup_plugin_patch.start()

    def tearDown(self):
        self._lookup_plugin_patch.stop()
        testing.tearDown()
        _teardown_db()
    
    def test_it(self):
        from altair.app.ticketing.orders.models import ImportTypeEnum, AllocationModeEnum
        importer = self._makeOne(self.request, ImportTypeEnum.Create.v, AllocationModeEnum.NoAutoAllocation.v, False, self.session)
        reader = [
            {
                u'order.order_no': u'XX0000000000',
                u'order.status': u'ステータス',
                u'order.payment_status': u'決済ステータス',
                u'order.created_at': u'',
                u'order.paid_at': u'',
                u'order.delivered_at': u'配送日時',
                u'order.canceled_at': u'キャンセル日時',
                u'order.total_amount': u'110',
                u'order.transaction_fee': u'30',
                u'order.delivery_fee': u'20',
                u'order.system_fee': u'10',
                u'order.special_fee': u'40',
                u'order.margin': u'内手数料金額',
                u'order.note': u'メモ',
                u'order.special_fee_name': u'特別手数料名',
                u'sej_order.billing_number': u'SEJ払込票番号',
                u'sej_order.exchange_number': u'SEJ引換票番号',
                u'user_profile.last_name': u'姓',
                u'user_profile.first_name': u'名',
                u'user_profile.last_name_kana': u'姓(カナ)',
                u'user_profile.first_name_kana': u'名(カナ)',
                u'user_profile.nick_name': u'ニックネーム',
                u'user_profile.sex': u'性別',
                u'membership.name': u'会員種別名',
                u'membergroup.name': u'会員グループ名',
                u'user_credential.auth_identifier': u'aho',
                u'shipping_address.last_name': u'配送先姓',
                u'shipping_address.first_name': u'配送先名',
                u'shipping_address.last_name_kana': u'配送先姓(カナ)',
                u'shipping_address.first_name_kana': u'配送先名(カナ)',
                u'shipping_address.zip': u'郵便番号',
                u'shipping_address.country': u'国',
                u'shipping_address.prefecture': u'都道府県',
                u'shipping_address.city': u'市区町村',
                u'shipping_address.address_1': u'住所1',
                u'shipping_address.address_2': u'住所2',
                u'shipping_address.tel_1': u'電話番号1',
                u'shipping_address.tel_2': u'電話番号2',
                u'shipping_address.fax': u'FAX',
                u'shipping_address.email_1': u'メールアドレス1',
                u'shipping_address.email_2': u'メールアドレス2',
                u'payment_method.name': u'RESERVE_NUMBER',
                u'delivery_method.name': u'RESERVE_NUMBER',
                u'event.title': u'イベント',
                u'performance.name': u'パフォーマンス',
                u'performance.code': u'ABCDEFGH',
                u'performance.start_on': u'公演日',
                u'venue.name': u'会場',
                u'ordered_product.price': u'10',
                u'ordered_product.quantity': u'1',
                u'ordered_product.product.name': u'A',
                u'ordered_product.product.sales_segment.sales_segment_group.name': u'存在する販売区分グループ',
                u'ordered_product.product.sales_segment.margin_ratio': u'販売手数料率',
                u'ordered_product_item.product_item.name': u'product_item_of_A',
                u'ordered_product_item.price': u'10',
                u'ordered_product_item.quantity': u'1',
                u'ordered_product_item.print_histories': u'発券作業者',
                u'mail_magazine.mail_permission': u'メールマガジン受信可否',
                u'seat.name': u'Seat A-5',
                },
            ]
        task, errors = importer(reader, self.operator, self.organization, self.performance)
        self.assertEquals(len(task.proto_orders), 1)
        self.assertEquals(len(errors), 0)

    def test_create_fail(self):
        from altair.app.ticketing.orders.models import ImportTypeEnum, AllocationModeEnum
        from altair.app.ticketing.orders.exceptions import MassOrderCreationError
        importer = self._makeOne(self.request, ImportTypeEnum.Create.v, AllocationModeEnum.NoAutoAllocation.v, False, self.session)
        reader = [
            {
                u'order.order_no': u'YY0000000000',
                u'order.status': u'ステータス',
                u'order.payment_status': u'決済ステータス',
                u'order.created_at': u'',
                u'order.paid_at': u'',
                u'order.delivered_at': u'配送日時',
                u'order.canceled_at': u'キャンセル日時',
                u'order.total_amount': u'110',
                u'order.transaction_fee': u'30',
                u'order.delivery_fee': u'20',
                u'order.system_fee': u'10',
                u'order.special_fee': u'40',
                u'order.margin': u'内手数料金額',
                u'order.note': u'メモ',
                u'order.special_fee_name': u'特別手数料名',
                u'sej_order.billing_number': u'SEJ払込票番号',
                u'sej_order.exchange_number': u'SEJ引換票番号',
                u'user_profile.last_name': u'姓',
                u'user_profile.first_name': u'名',
                u'user_profile.last_name_kana': u'姓(カナ)',
                u'user_profile.first_name_kana': u'名(カナ)',
                u'user_profile.nick_name': u'ニックネーム',
                u'user_profile.sex': u'性別',
                u'membership.name': u'会員種別名',
                u'membergroup.name': u'会員グループ名',
                u'user_credential.auth_identifier': u'aho',
                u'shipping_address.last_name': u'配送先姓',
                u'shipping_address.first_name': u'配送先名',
                u'shipping_address.last_name_kana': u'配送先姓(カナ)',
                u'shipping_address.first_name_kana': u'配送先名(カナ)',
                u'shipping_address.zip': u'郵便番号',
                u'shipping_address.country': u'国',
                u'shipping_address.prefecture': u'都道府県',
                u'shipping_address.city': u'市区町村',
                u'shipping_address.address_1': u'住所1',
                u'shipping_address.address_2': u'住所2',
                u'shipping_address.tel_1': u'電話番号1',
                u'shipping_address.tel_2': u'電話番号2',
                u'shipping_address.fax': u'FAX',
                u'shipping_address.email_1': u'メールアドレス1',
                u'shipping_address.email_2': u'メールアドレス2',
                u'payment_method.name': u'RESERVE_NUMBER',
                u'delivery_method.name': u'RESERVE_NUMBER',
                u'event.title': u'イベント',
                u'performance.name': u'パフォーマンス',
                u'performance.code': u'ABCDEFGH',
                u'performance.start_on': u'公演日',
                u'venue.name': u'会場',
                u'ordered_product.price': u'10',
                u'ordered_product.quantity': u'1',
                u'ordered_product.product.name': u'A',
                u'ordered_product.product.sales_segment.sales_segment_group.name': u'存在する販売区分グループ',
                u'ordered_product.product.sales_segment.margin_ratio': u'販売手数料率',
                u'ordered_product_item.product_item.name': u'product_item_of_A',
                u'ordered_product_item.price': u'10',
                u'ordered_product_item.quantity': u'1',
                u'ordered_product_item.print_histories': u'発券作業者',
                u'mail_magazine.mail_permission': u'メールマガジン受信可否',
                u'seat.name': u'Seat B-5',
                },
            {
                u'order.order_no': u'XX0000000000',
                u'order.status': u'ステータス',
                u'order.payment_status': u'決済ステータス',
                u'order.created_at': u'',
                u'order.paid_at': u'',
                u'order.delivered_at': u'配送日時',
                u'order.canceled_at': u'キャンセル日時',
                u'order.total_amount': u'110',
                u'order.transaction_fee': u'30',
                u'order.delivery_fee': u'20',
                u'order.system_fee': u'10',
                u'order.special_fee': u'40',
                u'order.margin': u'内手数料金額',
                u'order.note': u'メモ',
                u'order.special_fee_name': u'特別手数料名',
                u'sej_order.billing_number': u'SEJ払込票番号',
                u'sej_order.exchange_number': u'SEJ引換票番号',
                u'user_profile.last_name': u'姓',
                u'user_profile.first_name': u'名',
                u'user_profile.last_name_kana': u'姓(カナ)',
                u'user_profile.first_name_kana': u'名(カナ)',
                u'user_profile.nick_name': u'ニックネーム',
                u'user_profile.sex': u'性別',
                u'membership.name': u'会員種別名',
                u'membergroup.name': u'会員グループ名',
                u'user_credential.auth_identifier': u'aho',
                u'shipping_address.last_name': u'配送先姓',
                u'shipping_address.first_name': u'配送先名',
                u'shipping_address.last_name_kana': u'配送先姓(カナ)',
                u'shipping_address.first_name_kana': u'配送先名(カナ)',
                u'shipping_address.zip': u'郵便番号',
                u'shipping_address.country': u'国',
                u'shipping_address.prefecture': u'都道府県',
                u'shipping_address.city': u'市区町村',
                u'shipping_address.address_1': u'住所1',
                u'shipping_address.address_2': u'住所2',
                u'shipping_address.tel_1': u'電話番号1',
                u'shipping_address.tel_2': u'電話番号2',
                u'shipping_address.fax': u'FAX',
                u'shipping_address.email_1': u'メールアドレス1',
                u'shipping_address.email_2': u'メールアドレス2',
                u'payment_method.name': u'RESERVE_NUMBER',
                u'delivery_method.name': u'RESERVE_NUMBER',
                u'event.title': u'イベント',
                u'performance.name': u'パフォーマンス',
                u'performance.code': u'ABCDEFGH',
                u'performance.start_on': u'公演日',
                u'venue.name': u'会場',
                u'ordered_product.price': u'10',
                u'ordered_product.quantity': u'1',
                u'ordered_product.product.name': u'A',
                u'ordered_product.product.sales_segment.sales_segment_group.name': u'存在する販売区分グループ',
                u'ordered_product.product.sales_segment.margin_ratio': u'販売手数料率',
                u'ordered_product_item.product_item.name': u'product_item_of_A',
                u'ordered_product_item.price': u'10',
                u'ordered_product_item.quantity': u'1',
                u'ordered_product_item.print_histories': u'発券作業者',
                u'mail_magazine.mail_permission': u'メールマガジン受信可否',
                u'seat.name': u'Seat A-2',
                },
            {
                u'order.order_no': u'XX0000000001',
                u'order.status': u'ステータス',
                u'order.payment_status': u'決済ステータス',
                u'order.created_at': u'',
                u'order.paid_at': u'',
                u'order.delivered_at': u'配送日時',
                u'order.canceled_at': u'キャンセル日時',
                u'order.total_amount': u'110',
                u'order.transaction_fee': u'30',
                u'order.delivery_fee': u'20',
                u'order.system_fee': u'10',
                u'order.special_fee': u'40',
                u'order.margin': u'内手数料金額',
                u'order.note': u'メモ',
                u'order.special_fee_name': u'特別手数料名',
                u'sej_order.billing_number': u'SEJ払込票番号',
                u'sej_order.exchange_number': u'SEJ引換票番号',
                u'user_profile.last_name': u'姓',
                u'user_profile.first_name': u'名',
                u'user_profile.last_name_kana': u'姓(カナ)',
                u'user_profile.first_name_kana': u'名(カナ)',
                u'user_profile.nick_name': u'ニックネーム',
                u'user_profile.sex': u'性別',
                u'membership.name': u'会員種別名',
                u'membergroup.name': u'会員グループ名',
                u'user_credential.auth_identifier': u'aho',
                u'shipping_address.last_name': u'配送先姓',
                u'shipping_address.first_name': u'配送先名',
                u'shipping_address.last_name_kana': u'配送先姓(カナ)',
                u'shipping_address.first_name_kana': u'配送先名(カナ)',
                u'shipping_address.zip': u'郵便番号',
                u'shipping_address.country': u'国',
                u'shipping_address.prefecture': u'都道府県',
                u'shipping_address.city': u'市区町村',
                u'shipping_address.address_1': u'住所1',
                u'shipping_address.address_2': u'住所2',
                u'shipping_address.tel_1': u'電話番号1',
                u'shipping_address.tel_2': u'電話番号2',
                u'shipping_address.fax': u'FAX',
                u'shipping_address.email_1': u'メールアドレス1',
                u'shipping_address.email_2': u'メールアドレス2',
                u'payment_method.name': u'RESERVE_NUMBER',
                u'delivery_method.name': u'RESERVE_NUMBER',
                u'event.title': u'イベント',
                u'performance.name': u'パフォーマンス',
                u'performance.code': u'ABCDEFGH',
                u'performance.start_on': u'公演日',
                u'venue.name': u'会場',
                u'ordered_product.price': u'10',
                u'ordered_product.quantity': u'1',
                u'ordered_product.product.name': u'A',
                u'ordered_product.product.sales_segment.sales_segment_group.name': u'存在する販売区分グループ',
                u'ordered_product.product.sales_segment.margin_ratio': u'販売手数料率',
                u'ordered_product_item.product_item.name': u'product_item_of_A',
                u'ordered_product_item.price': u'10',
                u'ordered_product_item.quantity': u'1',
                u'ordered_product_item.print_histories': u'発券作業者',
                u'mail_magazine.mail_permission': u'メールマガジン受信可否',
                u'seat.name': u'Seat D-4',
                },
            ]
        task, errors = importer(reader, self.operator, self.organization, self.performance)
        self.assertIn('YY0000000000', errors)
        self.assertEquals(len(errors['YY0000000000']), 1)
        self.assertEquals(errors['YY0000000000'][0].message, u'すでに同じ予約番号の予約またはカートが存在します')
        self.assertIn('XX0000000000', errors)
        self.assertEquals(len(errors['XX0000000000']), 1)
        self.assertEquals(errors['XX0000000000'][0].message, u'座席「Seat A-2」(id=3, l0_id=seat-A-2) は予約 YY0000000001 に配席済みです')
        self.assertIn('XX0000000001', errors)
        self.assertEquals(len(errors['XX0000000001']), 1)
        self.assertEquals(errors['XX0000000001'][0].message, u'座席「Seat D-4」の席種「D」は商品明細に紐づいている席種「A」であるべきです')

    def test_create_or_update_fail_creation(self):
        from altair.app.ticketing.orders.models import ImportTypeEnum, AllocationModeEnum
        from altair.app.ticketing.orders.exceptions import MassOrderCreationError
        importer = self._makeOne(self.request, ImportTypeEnum.CreateOrUpdate.v, AllocationModeEnum.NoAutoAllocation.v, False, self.session)
        reader = [
            {
                u'order.order_no': u'YY0000000000',
                u'order.status': u'ステータス',
                u'order.payment_status': u'決済ステータス',
                u'order.created_at': u'',
                u'order.paid_at': u'',
                u'order.delivered_at': u'配送日時',
                u'order.canceled_at': u'キャンセル日時',
                u'order.total_amount': u'110',
                u'order.transaction_fee': u'30',
                u'order.delivery_fee': u'20',
                u'order.system_fee': u'10',
                u'order.special_fee': u'40',
                u'order.margin': u'内手数料金額',
                u'order.note': u'メモ',
                u'order.special_fee_name': u'特別手数料名',
                u'sej_order.billing_number': u'SEJ払込票番号',
                u'sej_order.exchange_number': u'SEJ引換票番号',
                u'user_profile.last_name': u'姓',
                u'user_profile.first_name': u'名',
                u'user_profile.last_name_kana': u'姓(カナ)',
                u'user_profile.first_name_kana': u'名(カナ)',
                u'user_profile.nick_name': u'ニックネーム',
                u'user_profile.sex': u'性別',
                u'membership.name': u'会員種別名',
                u'membergroup.name': u'会員グループ名',
                u'user_credential.auth_identifier': u'aho',
                u'shipping_address.last_name': u'配送先姓',
                u'shipping_address.first_name': u'配送先名',
                u'shipping_address.last_name_kana': u'配送先姓(カナ)',
                u'shipping_address.first_name_kana': u'配送先名(カナ)',
                u'shipping_address.zip': u'郵便番号',
                u'shipping_address.country': u'国',
                u'shipping_address.prefecture': u'都道府県',
                u'shipping_address.city': u'市区町村',
                u'shipping_address.address_1': u'住所1',
                u'shipping_address.address_2': u'住所2',
                u'shipping_address.tel_1': u'電話番号1',
                u'shipping_address.tel_2': u'電話番号2',
                u'shipping_address.fax': u'FAX',
                u'shipping_address.email_1': u'メールアドレス1',
                u'shipping_address.email_2': u'メールアドレス2',
                u'payment_method.name': self.payment_delivery_method_pairs[0].payment_method.name,
                u'delivery_method.name': self.payment_delivery_method_pairs[0].delivery_method.name,
                u'event.title': u'イベント',
                u'performance.name': u'パフォーマンス',
                u'performance.code': u'ABCDEFGH',
                u'performance.start_on': u'公演日',
                u'venue.name': u'会場',
                u'ordered_product.price': u'10',
                u'ordered_product.quantity': u'1',
                u'ordered_product.product.name': u'A',
                u'ordered_product.product.sales_segment.sales_segment_group.name': u'存在する販売区分グループ',
                u'ordered_product.product.sales_segment.margin_ratio': u'販売手数料率',
                u'ordered_product_item.product_item.name': u'product_item_of_A',
                u'ordered_product_item.price': u'10',
                u'ordered_product_item.quantity': u'1',
                u'ordered_product_item.print_histories': u'発券作業者',
                u'mail_magazine.mail_permission': u'メールマガジン受信可否',
                u'seat.name': u'Seat A-5',
                },
            {
                u'order.order_no': u'XX0000000000',
                u'order.status': u'ステータス',
                u'order.payment_status': u'決済ステータス',
                u'order.created_at': u'',
                u'order.paid_at': u'',
                u'order.delivered_at': u'配送日時',
                u'order.canceled_at': u'キャンセル日時',
                u'order.total_amount': u'110',
                u'order.transaction_fee': u'30',
                u'order.delivery_fee': u'20',
                u'order.system_fee': u'10',
                u'order.special_fee': u'40',
                u'order.margin': u'内手数料金額',
                u'order.note': u'メモ',
                u'order.special_fee_name': u'特別手数料名',
                u'sej_order.billing_number': u'SEJ払込票番号',
                u'sej_order.exchange_number': u'SEJ引換票番号',
                u'user_profile.last_name': u'姓',
                u'user_profile.first_name': u'名',
                u'user_profile.last_name_kana': u'姓(カナ)',
                u'user_profile.first_name_kana': u'名(カナ)',
                u'user_profile.nick_name': u'ニックネーム',
                u'user_profile.sex': u'性別',
                u'membership.name': u'会員種別名',
                u'membergroup.name': u'会員グループ名',
                u'user_credential.auth_identifier': u'aho',
                u'shipping_address.last_name': u'配送先姓',
                u'shipping_address.first_name': u'配送先名',
                u'shipping_address.last_name_kana': u'配送先姓(カナ)',
                u'shipping_address.first_name_kana': u'配送先名(カナ)',
                u'shipping_address.zip': u'郵便番号',
                u'shipping_address.country': u'国',
                u'shipping_address.prefecture': u'都道府県',
                u'shipping_address.city': u'市区町村',
                u'shipping_address.address_1': u'住所1',
                u'shipping_address.address_2': u'住所2',
                u'shipping_address.tel_1': u'電話番号1',
                u'shipping_address.tel_2': u'電話番号2',
                u'shipping_address.fax': u'FAX',
                u'shipping_address.email_1': u'メールアドレス1',
                u'shipping_address.email_2': u'メールアドレス2',
                u'payment_method.name': u'RESERVE_NUMBER',
                u'delivery_method.name': u'RESERVE_NUMBER',
                u'event.title': u'イベント',
                u'performance.name': u'パフォーマンス',
                u'performance.code': u'ABCDEFGH',
                u'performance.start_on': u'公演日',
                u'venue.name': u'会場',
                u'ordered_product.price': u'10',
                u'ordered_product.quantity': u'1',
                u'ordered_product.product.name': u'A',
                u'ordered_product.product.sales_segment.sales_segment_group.name': u'存在する販売区分グループ',
                u'ordered_product.product.sales_segment.margin_ratio': u'販売手数料率',
                u'ordered_product_item.product_item.name': u'product_item_of_A',
                u'ordered_product_item.price': u'10',
                u'ordered_product_item.quantity': u'1',
                u'ordered_product_item.print_histories': u'発券作業者',
                u'mail_magazine.mail_permission': u'メールマガジン受信可否',
                u'seat.name': u'Seat A-2',
                },
            ]
        task, errors = importer(reader, self.operator, self.organization, self.performance)
        self.assertNotIn('YY0000000000', errors)
        self.assertIn('XX0000000000', errors)
        self.assertEquals(len(errors['XX0000000000']), 1)
        self.assertEquals(errors['XX0000000000'][0].message, u'座席「Seat A-2」(id=3, l0_id=seat-A-2) は予約 YY0000000001 に配席済みです')

    def test_create_or_update_fail_updating_canceled(self):
        from altair.app.ticketing.orders.models import ImportTypeEnum, AllocationModeEnum
        from altair.app.ticketing.orders.exceptions import MassOrderCreationError
        importer = self._makeOne(self.request, ImportTypeEnum.CreateOrUpdate.v, AllocationModeEnum.NoAutoAllocation.v, False, self.session)
        self.existing_orders[0].release()
        self.existing_orders[0].mark_canceled()
        reader = [
            {
                u'order.order_no': u'YY0000000000',
                u'order.status': u'ステータス',
                u'order.payment_status': u'決済ステータス',
                u'order.created_at': u'',
                u'order.paid_at': u'',
                u'order.delivered_at': u'配送日時',
                u'order.canceled_at': u'キャンセル日時',
                u'order.total_amount': u'110',
                u'order.transaction_fee': u'30',
                u'order.delivery_fee': u'20',
                u'order.system_fee': u'10',
                u'order.special_fee': u'40',
                u'order.margin': u'内手数料金額',
                u'order.note': u'メモ',
                u'order.special_fee_name': u'特別手数料名',
                u'sej_order.billing_number': u'SEJ払込票番号',
                u'sej_order.exchange_number': u'SEJ引換票番号',
                u'user_profile.last_name': u'姓',
                u'user_profile.first_name': u'名',
                u'user_profile.last_name_kana': u'姓(カナ)',
                u'user_profile.first_name_kana': u'名(カナ)',
                u'user_profile.nick_name': u'ニックネーム',
                u'user_profile.sex': u'性別',
                u'membership.name': u'会員種別名',
                u'membergroup.name': u'会員グループ名',
                u'user_credential.auth_identifier': u'aho',
                u'shipping_address.last_name': u'配送先姓',
                u'shipping_address.first_name': u'配送先名',
                u'shipping_address.last_name_kana': u'配送先姓(カナ)',
                u'shipping_address.first_name_kana': u'配送先名(カナ)',
                u'shipping_address.zip': u'郵便番号',
                u'shipping_address.country': u'国',
                u'shipping_address.prefecture': u'都道府県',
                u'shipping_address.city': u'市区町村',
                u'shipping_address.address_1': u'住所1',
                u'shipping_address.address_2': u'住所2',
                u'shipping_address.tel_1': u'電話番号1',
                u'shipping_address.tel_2': u'電話番号2',
                u'shipping_address.fax': u'FAX',
                u'shipping_address.email_1': u'メールアドレス1',
                u'shipping_address.email_2': u'メールアドレス2',
                u'payment_method.name': self.payment_delivery_method_pairs[0].payment_method.name,
                u'delivery_method.name': self.payment_delivery_method_pairs[0].delivery_method.name,
                u'event.title': u'イベント',
                u'performance.name': u'パフォーマンス',
                u'performance.code': u'ABCDEFGH',
                u'performance.start_on': u'公演日',
                u'venue.name': u'会場',
                u'ordered_product.price': u'10',
                u'ordered_product.quantity': u'1',
                u'ordered_product.product.name': u'A',
                u'ordered_product.product.sales_segment.sales_segment_group.name': u'存在する販売区分グループ',
                u'ordered_product.product.sales_segment.margin_ratio': u'販売手数料率',
                u'ordered_product_item.product_item.name': u'product_item_of_A',
                u'ordered_product_item.price': u'10',
                u'ordered_product_item.quantity': u'1',
                u'ordered_product_item.print_histories': u'発券作業者',
                u'mail_magazine.mail_permission': u'メールマガジン受信可否',
                u'seat.name': u'Seat A-5',
                },
            {
                u'order.order_no': u'XX0000000000',
                u'order.status': u'ステータス',
                u'order.payment_status': u'決済ステータス',
                u'order.created_at': u'',
                u'order.paid_at': u'',
                u'order.delivered_at': u'配送日時',
                u'order.canceled_at': u'キャンセル日時',
                u'order.total_amount': u'110',
                u'order.transaction_fee': u'30',
                u'order.delivery_fee': u'20',
                u'order.system_fee': u'10',
                u'order.special_fee': u'40',
                u'order.margin': u'内手数料金額',
                u'order.note': u'メモ',
                u'order.special_fee_name': u'特別手数料名',
                u'sej_order.billing_number': u'SEJ払込票番号',
                u'sej_order.exchange_number': u'SEJ引換票番号',
                u'user_profile.last_name': u'姓',
                u'user_profile.first_name': u'名',
                u'user_profile.last_name_kana': u'姓(カナ)',
                u'user_profile.first_name_kana': u'名(カナ)',
                u'user_profile.nick_name': u'ニックネーム',
                u'user_profile.sex': u'性別',
                u'membership.name': u'会員種別名',
                u'membergroup.name': u'会員グループ名',
                u'user_credential.auth_identifier': u'aho',
                u'shipping_address.last_name': u'配送先姓',
                u'shipping_address.first_name': u'配送先名',
                u'shipping_address.last_name_kana': u'配送先姓(カナ)',
                u'shipping_address.first_name_kana': u'配送先名(カナ)',
                u'shipping_address.zip': u'郵便番号',
                u'shipping_address.country': u'国',
                u'shipping_address.prefecture': u'都道府県',
                u'shipping_address.city': u'市区町村',
                u'shipping_address.address_1': u'住所1',
                u'shipping_address.address_2': u'住所2',
                u'shipping_address.tel_1': u'電話番号1',
                u'shipping_address.tel_2': u'電話番号2',
                u'shipping_address.fax': u'FAX',
                u'shipping_address.email_1': u'メールアドレス1',
                u'shipping_address.email_2': u'メールアドレス2',
                u'payment_method.name': u'RESERVE_NUMBER',
                u'delivery_method.name': u'RESERVE_NUMBER',
                u'event.title': u'イベント',
                u'performance.name': u'パフォーマンス',
                u'performance.code': u'ABCDEFGH',
                u'performance.start_on': u'公演日',
                u'venue.name': u'会場',
                u'ordered_product.price': u'10',
                u'ordered_product.quantity': u'1',
                u'ordered_product.product.name': u'A',
                u'ordered_product.product.sales_segment.sales_segment_group.name': u'存在する販売区分グループ',
                u'ordered_product.product.sales_segment.margin_ratio': u'販売手数料率',
                u'ordered_product_item.product_item.name': u'product_item_of_A',
                u'ordered_product_item.price': u'10',
                u'ordered_product_item.quantity': u'1',
                u'ordered_product_item.print_histories': u'発券作業者',
                u'mail_magazine.mail_permission': u'メールマガジン受信可否',
                u'seat.name': u'Seat A-4',
                },
            ]
        task, errors = importer(reader, self.operator, self.organization, self.performance)
        self.assertIn('YY0000000000', errors)
        self.assertEquals(len(errors['YY0000000000']), 1)
        self.assertEquals(errors['YY0000000000'][0].message, u'元の注文 YY0000000000 はキャンセル済みです')
        self.assertNotIn('XX0000000000', errors)

    def test_cart_setting_ok(self):
        from altair.app.ticketing.orders.models import ImportTypeEnum, AllocationModeEnum
        importer = self._makeOne(self.request, ImportTypeEnum.Create.v, AllocationModeEnum.NoAutoAllocation.v, False, self.session)
        reader = [
            {
                u'order.order_no': u'XX0000000000',
                u'order.status': u'ステータス',
                u'order.payment_status': u'決済ステータス',
                u'order.created_at': u'',
                u'order.paid_at': u'',
                u'order.delivered_at': u'配送日時',
                u'order.canceled_at': u'キャンセル日時',
                u'order.total_amount': u'110',
                u'order.transaction_fee': u'30',
                u'order.delivery_fee': u'20',
                u'order.system_fee': u'10',
                u'order.special_fee': u'40',
                u'order.margin': u'内手数料金額',
                u'order.note': u'メモ',
                u'order.special_fee_name': u'特別手数料名',
                u'sej_order.billing_number': u'SEJ払込票番号',
                u'sej_order.exchange_number': u'SEJ引換票番号',
                u'user_profile.last_name': u'姓',
                u'user_profile.first_name': u'名',
                u'user_profile.last_name_kana': u'姓(カナ)',
                u'user_profile.first_name_kana': u'名(カナ)',
                u'user_profile.nick_name': u'ニックネーム',
                u'user_profile.sex': u'性別',
                u'membership.name': u'会員種別名',
                u'membergroup.name': u'会員グループ名',
                u'user_credential.auth_identifier': u'aho',
                u'shipping_address.last_name': u'配送先姓',
                u'shipping_address.first_name': u'配送先名',
                u'shipping_address.last_name_kana': u'配送先姓(カナ)',
                u'shipping_address.first_name_kana': u'配送先名(カナ)',
                u'shipping_address.zip': u'郵便番号',
                u'shipping_address.country': u'国',
                u'shipping_address.prefecture': u'都道府県',
                u'shipping_address.city': u'市区町村',
                u'shipping_address.address_1': u'住所1',
                u'shipping_address.address_2': u'住所2',
                u'shipping_address.tel_1': u'電話番号1',
                u'shipping_address.tel_2': u'電話番号2',
                u'shipping_address.fax': u'FAX',
                u'shipping_address.email_1': u'メールアドレス1',
                u'shipping_address.email_2': u'メールアドレス2',
                u'payment_method.name': u'RESERVE_NUMBER',
                u'delivery_method.name': u'RESERVE_NUMBER',
                u'event.title': u'イベント',
                u'performance.name': u'パフォーマンス',
                u'performance.code': u'ABCDEFGH',
                u'performance.start_on': u'公演日',
                u'venue.name': u'会場',
                u'ordered_product.price': u'10',
                u'ordered_product.quantity': u'1',
                u'ordered_product.product.name': u'A',
                u'ordered_product.product.sales_segment.sales_segment_group.name': u'存在する販売区分グループ',
                u'ordered_product.product.sales_segment.margin_ratio': u'販売手数料率',
                u'ordered_product_item.product_item.name': u'product_item_of_A',
                u'ordered_product_item.price': u'10',
                u'ordered_product_item.quantity': u'1',
                u'ordered_product_item.print_histories': u'発券作業者',
                u'mail_magazine.mail_permission': u'メールマガジン受信可否',
                u'seat.name': u'Seat A-5',
                u'order.cart_setting_id': u'default'
                },
            {
                u'order.order_no': u'XX0000000001',
                u'order.status': u'ステータス',
                u'order.payment_status': u'決済ステータス',
                u'order.created_at': u'',
                u'order.paid_at': u'',
                u'order.delivered_at': u'配送日時',
                u'order.canceled_at': u'キャンセル日時',
                u'order.total_amount': u'110',
                u'order.transaction_fee': u'30',
                u'order.delivery_fee': u'20',
                u'order.system_fee': u'10',
                u'order.special_fee': u'40',
                u'order.margin': u'内手数料金額',
                u'order.note': u'メモ',
                u'order.special_fee_name': u'特別手数料名',
                u'sej_order.billing_number': u'SEJ払込票番号',
                u'sej_order.exchange_number': u'SEJ引換票番号',
                u'user_profile.last_name': u'姓',
                u'user_profile.first_name': u'名',
                u'user_profile.last_name_kana': u'姓(カナ)',
                u'user_profile.first_name_kana': u'名(カナ)',
                u'user_profile.nick_name': u'ニックネーム',
                u'user_profile.sex': u'性別',
                u'membership.name': u'会員種別名',
                u'membergroup.name': u'会員グループ名',
                u'user_credential.auth_identifier': u'aho',
                u'shipping_address.last_name': u'配送先姓',
                u'shipping_address.first_name': u'配送先名',
                u'shipping_address.last_name_kana': u'配送先姓(カナ)',
                u'shipping_address.first_name_kana': u'配送先名(カナ)',
                u'shipping_address.zip': u'郵便番号',
                u'shipping_address.country': u'国',
                u'shipping_address.prefecture': u'都道府県',
                u'shipping_address.city': u'市区町村',
                u'shipping_address.address_1': u'住所1',
                u'shipping_address.address_2': u'住所2',
                u'shipping_address.tel_1': u'電話番号1',
                u'shipping_address.tel_2': u'電話番号2',
                u'shipping_address.fax': u'FAX',
                u'shipping_address.email_1': u'メールアドレス1',
                u'shipping_address.email_2': u'メールアドレス2',
                u'payment_method.name': u'RESERVE_NUMBER',
                u'delivery_method.name': u'RESERVE_NUMBER',
                u'event.title': u'イベント',
                u'performance.name': u'パフォーマンス',
                u'performance.code': u'ABCDEFGH',
                u'performance.start_on': u'公演日',
                u'venue.name': u'会場',
                u'ordered_product.price': u'10',
                u'ordered_product.quantity': u'1',
                u'ordered_product.product.name': u'A',
                u'ordered_product.product.sales_segment.sales_segment_group.name': u'存在する販売区分グループ',
                u'ordered_product.product.sales_segment.margin_ratio': u'販売手数料率',
                u'ordered_product_item.product_item.name': u'product_item_of_A',
                u'ordered_product_item.price': u'10',
                u'ordered_product_item.quantity': u'1',
                u'ordered_product_item.print_histories': u'発券作業者',
                u'mail_magazine.mail_permission': u'メールマガジン受信可否',
                u'seat.name': u'Seat A-4',
                u'order.cart_setting_id': u'event'
                },
            ]
        task, errors = importer(reader, self.operator, self.organization, self.performance)
        self.assertEquals(len(task.proto_orders), 2)
        self.assertEquals(len(errors), 0)

    def test_cart_setting_defaults_to_organization_setting(self):
        from altair.app.ticketing.orders.models import ImportTypeEnum, AllocationModeEnum
        importer = self._makeOne(self.request, ImportTypeEnum.Create.v, AllocationModeEnum.NoAutoAllocation.v, False, self.session)
        reader = [
            {
                u'order.order_no': u'XX0000000000',
                u'order.status': u'ステータス',
                u'order.payment_status': u'決済ステータス',
                u'order.created_at': u'',
                u'order.paid_at': u'',
                u'order.delivered_at': u'配送日時',
                u'order.canceled_at': u'キャンセル日時',
                u'order.total_amount': u'110',
                u'order.transaction_fee': u'30',
                u'order.delivery_fee': u'20',
                u'order.system_fee': u'10',
                u'order.special_fee': u'40',
                u'order.margin': u'内手数料金額',
                u'order.note': u'メモ',
                u'order.special_fee_name': u'特別手数料名',
                u'sej_order.billing_number': u'SEJ払込票番号',
                u'sej_order.exchange_number': u'SEJ引換票番号',
                u'user_profile.last_name': u'姓',
                u'user_profile.first_name': u'名',
                u'user_profile.last_name_kana': u'姓(カナ)',
                u'user_profile.first_name_kana': u'名(カナ)',
                u'user_profile.nick_name': u'ニックネーム',
                u'user_profile.sex': u'性別',
                u'membership.name': u'会員種別名',
                u'membergroup.name': u'会員グループ名',
                u'user_credential.auth_identifier': u'aho',
                u'shipping_address.last_name': u'配送先姓',
                u'shipping_address.first_name': u'配送先名',
                u'shipping_address.last_name_kana': u'配送先姓(カナ)',
                u'shipping_address.first_name_kana': u'配送先名(カナ)',
                u'shipping_address.zip': u'郵便番号',
                u'shipping_address.country': u'国',
                u'shipping_address.prefecture': u'都道府県',
                u'shipping_address.city': u'市区町村',
                u'shipping_address.address_1': u'住所1',
                u'shipping_address.address_2': u'住所2',
                u'shipping_address.tel_1': u'電話番号1',
                u'shipping_address.tel_2': u'電話番号2',
                u'shipping_address.fax': u'FAX',
                u'shipping_address.email_1': u'メールアドレス1',
                u'shipping_address.email_2': u'メールアドレス2',
                u'payment_method.name': u'RESERVE_NUMBER',
                u'delivery_method.name': u'RESERVE_NUMBER',
                u'event.title': u'イベント',
                u'performance.name': u'パフォーマンス',
                u'performance.code': u'ABCDEFGH',
                u'performance.start_on': u'公演日',
                u'venue.name': u'会場',
                u'ordered_product.price': u'10',
                u'ordered_product.quantity': u'1',
                u'ordered_product.product.name': u'A',
                u'ordered_product.product.sales_segment.sales_segment_group.name': u'存在する販売区分グループ',
                u'ordered_product.product.sales_segment.margin_ratio': u'販売手数料率',
                u'ordered_product_item.product_item.name': u'product_item_of_A',
                u'ordered_product_item.price': u'10',
                u'ordered_product_item.quantity': u'1',
                u'ordered_product_item.print_histories': u'発券作業者',
                u'mail_magazine.mail_permission': u'メールマガジン受信可否',
                u'seat.name': u'Seat A-5',
                },
            ]
        task, errors = importer(reader, self.operator, self.organization, self.performance)
        self.assertEquals(len(task.proto_orders), 1)
        self.assertEquals(task.proto_orders[0].cart_setting_id, self.organization.setting.cart_setting_id)
        self.assertEquals(len(errors), 0)

    def test_cart_setting_defaults_to_event_setting(self):
        from altair.app.ticketing.orders.models import ImportTypeEnum, AllocationModeEnum
        from altair.app.ticketing.core.models import EventSetting
        self.event.setting = EventSetting(cart_setting=self.cart_settings[1])
        importer = self._makeOne(self.request, ImportTypeEnum.Create.v, AllocationModeEnum.NoAutoAllocation.v, False, self.session)
        reader = [
            {
                u'order.order_no': u'XX0000000000',
                u'order.status': u'ステータス',
                u'order.payment_status': u'決済ステータス',
                u'order.created_at': u'',
                u'order.paid_at': u'',
                u'order.delivered_at': u'配送日時',
                u'order.canceled_at': u'キャンセル日時',
                u'order.total_amount': u'110',
                u'order.transaction_fee': u'30',
                u'order.delivery_fee': u'20',
                u'order.system_fee': u'10',
                u'order.special_fee': u'40',
                u'order.margin': u'内手数料金額',
                u'order.note': u'メモ',
                u'order.special_fee_name': u'特別手数料名',
                u'sej_order.billing_number': u'SEJ払込票番号',
                u'sej_order.exchange_number': u'SEJ引換票番号',
                u'user_profile.last_name': u'姓',
                u'user_profile.first_name': u'名',
                u'user_profile.last_name_kana': u'姓(カナ)',
                u'user_profile.first_name_kana': u'名(カナ)',
                u'user_profile.nick_name': u'ニックネーム',
                u'user_profile.sex': u'性別',
                u'membership.name': u'会員種別名',
                u'membergroup.name': u'会員グループ名',
                u'user_credential.auth_identifier': u'aho',
                u'shipping_address.last_name': u'配送先姓',
                u'shipping_address.first_name': u'配送先名',
                u'shipping_address.last_name_kana': u'配送先姓(カナ)',
                u'shipping_address.first_name_kana': u'配送先名(カナ)',
                u'shipping_address.zip': u'郵便番号',
                u'shipping_address.country': u'国',
                u'shipping_address.prefecture': u'都道府県',
                u'shipping_address.city': u'市区町村',
                u'shipping_address.address_1': u'住所1',
                u'shipping_address.address_2': u'住所2',
                u'shipping_address.tel_1': u'電話番号1',
                u'shipping_address.tel_2': u'電話番号2',
                u'shipping_address.fax': u'FAX',
                u'shipping_address.email_1': u'メールアドレス1',
                u'shipping_address.email_2': u'メールアドレス2',
                u'payment_method.name': u'RESERVE_NUMBER',
                u'delivery_method.name': u'RESERVE_NUMBER',
                u'event.title': u'イベント',
                u'performance.name': u'パフォーマンス',
                u'performance.code': u'ABCDEFGH',
                u'performance.start_on': u'公演日',
                u'venue.name': u'会場',
                u'ordered_product.price': u'10',
                u'ordered_product.quantity': u'1',
                u'ordered_product.product.name': u'A',
                u'ordered_product.product.sales_segment.sales_segment_group.name': u'存在する販売区分グループ',
                u'ordered_product.product.sales_segment.margin_ratio': u'販売手数料率',
                u'ordered_product_item.product_item.name': u'product_item_of_A',
                u'ordered_product_item.price': u'10',
                u'ordered_product_item.quantity': u'1',
                u'ordered_product_item.print_histories': u'発券作業者',
                u'mail_magazine.mail_permission': u'メールマガジン受信可否',
                u'seat.name': u'Seat A-5',
                },
            ]
        task, errors = importer(reader, self.operator, self.organization, self.performance)
        self.assertEquals(len(task.proto_orders), 1)
        self.assertEquals(task.proto_orders[0].cart_setting_id, self.event.setting.cart_setting_id)
        self.assertEquals(len(errors), 0)

    def test_cart_setting_nonexistent_fail(self):
        from altair.app.ticketing.orders.models import ImportTypeEnum, AllocationModeEnum
        importer = self._makeOne(self.request, ImportTypeEnum.Create.v, AllocationModeEnum.NoAutoAllocation.v, False, self.session)
        reader = [
            {
                u'order.order_no': u'XX0000000000',
                u'order.status': u'ステータス',
                u'order.payment_status': u'決済ステータス',
                u'order.created_at': u'',
                u'order.paid_at': u'',
                u'order.delivered_at': u'配送日時',
                u'order.canceled_at': u'キャンセル日時',
                u'order.total_amount': u'110',
                u'order.transaction_fee': u'30',
                u'order.delivery_fee': u'20',
                u'order.system_fee': u'10',
                u'order.special_fee': u'40',
                u'order.margin': u'内手数料金額',
                u'order.note': u'メモ',
                u'order.special_fee_name': u'特別手数料名',
                u'sej_order.billing_number': u'SEJ払込票番号',
                u'sej_order.exchange_number': u'SEJ引換票番号',
                u'user_profile.last_name': u'姓',
                u'user_profile.first_name': u'名',
                u'user_profile.last_name_kana': u'姓(カナ)',
                u'user_profile.first_name_kana': u'名(カナ)',
                u'user_profile.nick_name': u'ニックネーム',
                u'user_profile.sex': u'性別',
                u'membership.name': u'会員種別名',
                u'membergroup.name': u'会員グループ名',
                u'user_credential.auth_identifier': u'aho',
                u'shipping_address.last_name': u'配送先姓',
                u'shipping_address.first_name': u'配送先名',
                u'shipping_address.last_name_kana': u'配送先姓(カナ)',
                u'shipping_address.first_name_kana': u'配送先名(カナ)',
                u'shipping_address.zip': u'郵便番号',
                u'shipping_address.country': u'国',
                u'shipping_address.prefecture': u'都道府県',
                u'shipping_address.city': u'市区町村',
                u'shipping_address.address_1': u'住所1',
                u'shipping_address.address_2': u'住所2',
                u'shipping_address.tel_1': u'電話番号1',
                u'shipping_address.tel_2': u'電話番号2',
                u'shipping_address.fax': u'FAX',
                u'shipping_address.email_1': u'メールアドレス1',
                u'shipping_address.email_2': u'メールアドレス2',
                u'payment_method.name': u'RESERVE_NUMBER',
                u'delivery_method.name': u'RESERVE_NUMBER',
                u'event.title': u'イベント',
                u'performance.name': u'パフォーマンス',
                u'performance.code': u'ABCDEFGH',
                u'performance.start_on': u'公演日',
                u'venue.name': u'会場',
                u'ordered_product.price': u'10',
                u'ordered_product.quantity': u'1',
                u'ordered_product.product.name': u'A',
                u'ordered_product.product.sales_segment.sales_segment_group.name': u'存在する販売区分グループ',
                u'ordered_product.product.sales_segment.margin_ratio': u'販売手数料率',
                u'ordered_product_item.product_item.name': u'product_item_of_A',
                u'ordered_product_item.price': u'10',
                u'ordered_product_item.quantity': u'1',
                u'ordered_product_item.print_histories': u'発券作業者',
                u'mail_magazine.mail_permission': u'メールマガジン受信可否',
                u'seat.name': u'Seat A-5',
                u'order.cart_setting_id': u'NONEXISTENT'
                },
            ]
        task, errors = importer(reader, self.operator, self.organization, self.performance)
        self.assertEquals(len(task.proto_orders), 0)
        self.assertEquals(len(errors), 1)

    def test_cart_setting_duplicate_fail(self):
        from altair.app.ticketing.orders.models import ImportTypeEnum, AllocationModeEnum
        importer = self._makeOne(self.request, ImportTypeEnum.Create.v, AllocationModeEnum.NoAutoAllocation.v, False, self.session)
        reader = [
            {
                u'order.order_no': u'XX0000000000',
                u'order.status': u'ステータス',
                u'order.payment_status': u'決済ステータス',
                u'order.created_at': u'',
                u'order.paid_at': u'',
                u'order.delivered_at': u'配送日時',
                u'order.canceled_at': u'キャンセル日時',
                u'order.total_amount': u'110',
                u'order.transaction_fee': u'30',
                u'order.delivery_fee': u'20',
                u'order.system_fee': u'10',
                u'order.special_fee': u'40',
                u'order.margin': u'内手数料金額',
                u'order.note': u'メモ',
                u'order.special_fee_name': u'特別手数料名',
                u'sej_order.billing_number': u'SEJ払込票番号',
                u'sej_order.exchange_number': u'SEJ引換票番号',
                u'user_profile.last_name': u'姓',
                u'user_profile.first_name': u'名',
                u'user_profile.last_name_kana': u'姓(カナ)',
                u'user_profile.first_name_kana': u'名(カナ)',
                u'user_profile.nick_name': u'ニックネーム',
                u'user_profile.sex': u'性別',
                u'membership.name': u'会員種別名',
                u'membergroup.name': u'会員グループ名',
                u'user_credential.auth_identifier': u'aho',
                u'shipping_address.last_name': u'配送先姓',
                u'shipping_address.first_name': u'配送先名',
                u'shipping_address.last_name_kana': u'配送先姓(カナ)',
                u'shipping_address.first_name_kana': u'配送先名(カナ)',
                u'shipping_address.zip': u'郵便番号',
                u'shipping_address.country': u'国',
                u'shipping_address.prefecture': u'都道府県',
                u'shipping_address.city': u'市区町村',
                u'shipping_address.address_1': u'住所1',
                u'shipping_address.address_2': u'住所2',
                u'shipping_address.tel_1': u'電話番号1',
                u'shipping_address.tel_2': u'電話番号2',
                u'shipping_address.fax': u'FAX',
                u'shipping_address.email_1': u'メールアドレス1',
                u'shipping_address.email_2': u'メールアドレス2',
                u'payment_method.name': u'RESERVE_NUMBER',
                u'delivery_method.name': u'RESERVE_NUMBER',
                u'event.title': u'イベント',
                u'performance.name': u'パフォーマンス',
                u'performance.code': u'ABCDEFGH',
                u'performance.start_on': u'公演日',
                u'venue.name': u'会場',
                u'ordered_product.price': u'10',
                u'ordered_product.quantity': u'1',
                u'ordered_product.product.name': u'A',
                u'ordered_product.product.sales_segment.sales_segment_group.name': u'存在する販売区分グループ',
                u'ordered_product.product.sales_segment.margin_ratio': u'販売手数料率',
                u'ordered_product_item.product_item.name': u'product_item_of_A',
                u'ordered_product_item.price': u'10',
                u'ordered_product_item.quantity': u'1',
                u'ordered_product_item.print_histories': u'発券作業者',
                u'mail_magazine.mail_permission': u'メールマガジン受信可否',
                u'seat.name': u'Seat A-5',
                u'order.cart_setting_id': u'duplicate'
                },
            ]
        task, errors = importer(reader, self.operator, self.organization, self.performance)
        self.assertEquals(len(task.proto_orders), 0)
        self.assertEquals(len(errors), 1)



