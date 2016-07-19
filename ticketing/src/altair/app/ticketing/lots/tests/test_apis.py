# -*- coding:utf-8 -*-
from unittest import TestCase
import mock
from pyramid import testing
from altair.app.ticketing.testing import _setup_db, _teardown_db, DummyRequest
from ..testing import _create_products, login

dependency_modules = [
    'altair.app.ticketing.orders.models',
    'altair.app.ticketing.users.models',
    'altair.app.ticketing.lots.models',
    'altair.app.ticketing.core.models',
]

# class get_productsTests(TestCase):
#     def _callFUT(self, *args, **kwargs):
#         from ..api import get_products
#         return get_products(*args, **kwargs)

#     def test_it(self):
#         request = DummyRequest()
#         sales_segment = mock.Mock()
#         performances = [
#             testing.DummyModel()
#         ]
#         results = self._callFUT(request, sales_segment, performances)
#         sales_segment.get_products.assert_called_with(performances)

# class create_cartTests(TestCase):
#     @classmethod
#     def setUpClass(cls):
#         cls.session = _setup_db(modules=dependency_modules)


#     @classmethod
#     def tearDownClass(self):
#         _teardown_db()

#     def setUp(self):
#         self.config = testing.setUp()
#         self.session.remove()

#     def tearDown(self):
#         import transaction
#         transaction.abort()
#         testing.tearDown()

#     def _callFUT(self, *args, **kwargs):
#         from .. import api
#         return api.create_cart(*args, **kwargs)


#     def test_it(self):
#         from altair.app.ticketing.core.models import (
#             Performance, Product, PaymentDeliveryMethodPair, ShippingAddress, SalesSegment,
#             PaymentMethod, DeliveryMethod, Event, Organization
#         )
#         from altair.app.ticketing.lots.models import Lot, LotEntry, LotEntryWish, LotElectedEntry, LotEntryProduct
#         from pyramid.interfaces import IRequest
#         from altair.app.ticketing.cart.interfaces import IStocker
#         from ..testing import DummyStockerFactory

#         stocks = []
#         self.config.registry.adapters.register([IRequest], IStocker, "", DummyStockerFactory(stocks))

#         performance = Performance(id=999999,
#             event=Event(organization=Organization(code="TT", short_name=u"testing")),
#         )
#         self.session.add(performance)
#         self.session.flush()
#         product = Product(price=10)
#         payment_delivery_method_pair = PaymentDeliveryMethodPair(system_fee=9999,
#             transaction_fee=0,
#             delivery_fee=0,
#             discount=0,
#             payment_method=PaymentMethod(fee=0),
#             delivery_method=DeliveryMethod(fee=0))
#         shipping_address = ShippingAddress()
#         sales_segment = SalesSegment()

#         request = DummyRequest()
#         lot_entry = LotEntry(
#             payment_delivery_method_pair=payment_delivery_method_pair,
#             shipping_address=shipping_address,
#             lot=Lot(
#                 sales_segment=sales_segment,
#             ),
#             lot_elected_entries=[
#                 LotElectedEntry(
#                     lot_entry_wish=LotEntryWish(
#                         performance=performance,
#                         performance_id=performance.id,
#                         products=[
#                             LotEntryProduct(quantity=10, product=product),
#                         ],
#                     ),
#                 ),
#             ],
#         )

#         result = self._callFUT(request, lot_entry)

#         self.assertEqual(result.performance, performance)
#         self.assertEqual(result.payment_delivery_pair, payment_delivery_method_pair)
#         self.assertEqual(result.shipping_address, shipping_address)
#         self.assertEqual(result.system_fee, 9999)
#         self.assertEqual(result.sales_segment, sales_segment)
#         self.assertEqual(len(result.products), 1)
#         self.assertEqual(result.products[0].product, product)


# class get_lotTests(TestCase):
#     @classmethod
#     def setUpClass(cls):
#         cls.session = _setup_db(modules=dependency_modules)
#
#
#     @classmethod
#     def tearDownClass(self):
#         _teardown_db()
#
#     def setUp(self):
#         self.session.remove()
#
#     def tearDown(self):
#         import transaction
#         transaction.abort()
#
#     def _callFUT(self, *args, **kwargs):
#         from .. import api
#         return api.get_lot(*args, **kwargs)
#
#
#     def test_it(self):
#         from ..testing import _add_lot
#         request = DummyRequest()
#         event = testing.DummyModel(id=1111)
#         sales_segment = testing.DummyModel(id=12345)
#         l = _add_lot(self.session, event.id, sales_segment.id, 5, 3)
#         lot_id = l.id
#         result = self._callFUT(request, event, sales_segment, lot_id)
#
#         self.assertEqual(result[0], l)
#         self.assertEqual(len(result[1]), 5)
#         self.assertEqual(result[1][0].name, u"パフォーマンス 0")
#         self.assertEqual(result[1][4].name, u"パフォーマンス 4")
#         self.assertEqual(len(result[2]), 3)
#         self.assertEqual(result[2][0].name, u"席 0")
#         self.assertEqual(result[2][2].name, u"席 2")
#

class entry_lotTests(TestCase):
    def setUp(self):
        from altair.sqlahelper import register_sessionmaker_with_engine
        self.config = testing.setUp()
        self.config.include('altair.app.ticketing.cart.request')
        self.session = _setup_db(modules=dependency_modules)
        register_sessionmaker_with_engine(
            self.config.registry,
            'slave',
            self.session.bind
            )
        from altair.app.ticketing.core.models import Host, Organization
        organization = Organization(name='test', short_name='test')
        host = Host(organization=organization, host_name='example.com:80')
        self.session.add(organization)
        self.session.add(host)
        self.session.flush()
        self.organization = organization

    def tearDown(self):
        import transaction
        transaction.abort()
        _teardown_db()
        testing.tearDown()

    def _callFUT(self, *args, **kwargs):
        from .. import api
        return api.entry_lot(*args, **kwargs)


    def test_it(self):
        from datetime import datetime
        from altair.app.ticketing.core.models import ShippingAddress
        from altair.app.ticketing.core.models import PaymentMethod
        from altair.app.ticketing.users.models import Membership, MemberGroup
        from ..testing import _add_lot

        request = DummyRequest(host='example.com:80', organization=self.organization)
        login(self.config, {"auth_type": "fc_auth", "username": "test", "membership": "test", "membergroup": "test"})

        event = testing.DummyModel(id=1111)
        sales_segment = testing.DummyModel(id=12345)
        lot = _add_lot(self.session, event.id, sales_segment.id, 5, 3)
        lot.event.organization = self.organization
        lot_id = lot.id
        payment_delivery_method_pairs = lot.sales_segment.payment_delivery_method_pairs
        membership = Membership(organization=self.organization, name="test")
        performances = lot.performances
        shipping_address = ShippingAddress()
        self.session.add(shipping_address)
        self.session.add(membership)
        self.session.add(MemberGroup(name='test', membership=membership))
        products = _create_products(self.session, [
            {'name': u'商品 A', 'price': 100},
            {'name': u'商品 B', 'price': 100},
            {'name': u'商品 C', 'price': 100},
        ])
        self.session.flush()
        wishes = [
                    # 第一希望
                    {"performance_id": performances[0].id,
                     "wished_products": [{"wish_order": 1, "product_id": products[0].id, "quantity": 10}]},
                    # 第二希望
                    {"performance_id": performances[1].id,
                     "wished_products": [{"wish_order": 2, "product_id": products[1].id, "quantity": 11},
                                         {"wish_order": 2, "product_id": products[2].id, "quantity": 12}]},
                 ]
        entry_no = "testing-entry-no"

        result = self._callFUT(request, entry_no,
                               lot, shipping_address, wishes,
                               payment_delivery_method_pairs[0], None,
                               1, datetime(2013, 4, 24), u"memo")

        self.assertEqual(result.entry_no, "testing-entry-no")
        self.assertEqual(result.shipping_address, shipping_address)
        self.assertEqual(result.payment_delivery_method_pair, payment_delivery_method_pairs[0])
        self.assertEqual(len(result.wishes), 2)
        # 第一希望
        self.assertEqual(result.wishes[0].wish_order, 0)
        self.assertEqual(result.wishes[0].performance, performances[0])
        self.assertEqual(len(result.wishes[0].products), 1)
        self.assertEqual(result.wishes[0].products[0].quantity, 10)
        self.assertEqual(result.wishes[0].products[0].product_id, products[0].id)
        # 第二希望
        self.assertEqual(result.wishes[1].wish_order, 1)
        self.assertEqual(result.wishes[1].performance, performances[1])
        self.assertEqual(len(result.wishes[1].products), 2)
        self.assertEqual(result.wishes[1].products[0].quantity, 11)
        self.assertEqual(result.wishes[1].products[0].product_id, products[1].id)
        self.assertEqual(result.wishes[1].products[1].quantity, 12)
        self.assertEqual(result.wishes[1].products[1].product_id, products[2].id)

        #self.assertTrue(result.entry_no.startswith("LOTtest"))
        self.assertEqual(result.membergroup.name, "test")
        self.assertEqual(result.membership.name, "test")


class get_entryTests(TestCase):
    @classmethod
    def setUpClass(cls):
        from altair.sqlahelper import register_sessionmaker_with_engine
        cls.session = _setup_db(modules=dependency_modules)
        cls.config = testing.setUp()
        cls.config.include('altair.app.ticketing.cart.request')
        register_sessionmaker_with_engine(
            cls.config.registry,
            'slave',
            cls.session.bind
            )

    @classmethod
    def tearDownClass(self):
        _teardown_db()
        testing.tearDown()

    def setUp(self):
        self.session.remove()

    def tearDown(self):
        import transaction
        transaction.abort()

    def _callFUT(self, *args, **kwargs):
        from .. import api
        return api.get_entry(*args, **kwargs)

    def test_it(self):
        from altair.app.ticketing.core.models import ShippingAddress, DBSession
        from altair.app.ticketing.lots.models import LotEntry
        request = DummyRequest()
        entry_no = u'LOTtest000001'
        tel_no = '0123456789'
        shipping_address = ShippingAddress(tel_1=tel_no)
        entry = LotEntry(entry_no=entry_no, shipping_address=shipping_address)
        DBSession.add(entry)
        DBSession.flush()


        result = self._callFUT(request, entry_no, tel_no)
        self.assertEqual(result.id, entry.id)

class entry_infoTests(TestCase):
    @classmethod
    def setUpClass(cls):
        from altair.sqlahelper import register_sessionmaker_with_engine
        cls.session = _setup_db(modules=dependency_modules)
        cls.config = testing.setUp()
        register_sessionmaker_with_engine(
            cls.config.registry,
            'slave',
            cls.session.bind
            )

    @classmethod
    def tearDownClass(self):
        _teardown_db()
        testing.tearDown()

    def _callFUT(self, *args, **kwargs):
        from .. import api
        return api._entry_info(*args, **kwargs)

    def test_it(self):
        from datetime import datetime
        from altair.app.ticketing.core.models import ShippingAddress

        wish = testing.DummyModel(
            lot_entry=testing.DummyModel(
                lot=testing.DummyModel(
                    event=testing.DummyModel(title=u"テストイベント"),
                ),
                entry_no="testENTRYNO",
                membergroup=testing.DummyModel(),
                user=testing.DummyModel(
                    user_profile=testing.DummyModel(
                        zip="1234567",
                        prefecture=u"東京都",
                        sex=1,
                        nick_name=u"nick",
                        last_name=u"らすと",
                        first_name=u"ふぁーすと",
                        last_name_kana=u"ふぁーすと",
                        first_name_kana=u"ふぁーすと",
                    )
                    ),
                shipping_address=ShippingAddress(
                    zip="1234567",
                    prefecture=u"東京都",
                    sex=1,
                    last_name=u"らすと",
                    first_name=u"ふぁーすと",
                    last_name_kana=u"ふぁーすと",
                    first_name_kana=u"ふぁーすと",
                    ),
                payment_delivery_method_pair=testing.DummyModel(
                    payment_method=testing.DummyModel(name=u"testing payment"),
                    delivery_method=testing.DummyModel(name=u"testing delivery"),
                ),
            ),
            performance=testing.DummyModel(
                code=u"TESTING",
                name=u"テスト公演",
                venue=testing.DummyModel(name=u"testing-venue"),
                start_on=datetime(2013, 1, 1),
            ),
            wish_order=10,
            created_at=datetime(2013, 1, 1),
            products=[
                ],
            total_quantity=0,
            status=u"",
        )
        result = self._callFUT(wish)


# class elect_entryTests(TestCase):
#     def setUp(self):
#         from datetime import datetime
#         self.datetime = datetime

#     def _callFUT(self, *args, **kwargs):
#         from .. import api
#         return api.elect_entry(*args, **kwargs)

#     def test_it(self):

#         from .. import models as m
#         lot = testing.DummyModel()
#         wish = m.LotEntryWish(
#             lot_entry=m.LotEntry()
#         )

#         result = self._callFUT(lot, wish)
#         self.assertTrue(wish.elected_at)
#         self.assertTrue(wish.lot_entry.elected_at)

#         self.assertEqual(result.lot_entry, wish.lot_entry)
#         self.assertEqual(result.lot_entry_wish, wish)

class notify_entry_lotTests(TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.include('altair.app.ticketing.cart.request')

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *args, **kwargs):
        from .. import api
        return api.notify_entry_lot(*args, **kwargs)

    def test_it(self):
        from ..events import LotEntriedEvent

        called = []
        def handler(event):
            called.append(event)

        self.config.add_subscriber(handler, LotEntriedEvent)

        entry = testing.DummyModel()
        request = DummyRequest()
        self._callFUT(request, entry)

        self.assertEqual(called[0].lot_entry, entry)

#class elect_lot_entriesTests(TestCase):
#    def _callFUT(self, *args, **kwargs):
#        from ..api import elect_lot_entries
#        return elect_lot_entries(*args, **kwargs)
#
#    def test_it(self):
#
#        # 当選データ
#        # 落選データ
#
#        result = self._callFUT()


class LotEntryBuildingTest(TestCase):
    """altair.app.ticketing.lots.api.build_lot_entryのテスト
    >>> import altair.app.ticketing.lots.api.build_lot_ent
    """
    def _callFUT(self, *args, **kwds):
        from ..api import build_lot_entry
        return build_lot_entry(*args, **kwds)


# 新抽選
class CreatingLotsFromFormTest(TestCase):
    """画面(form)から抽選が作成されることを確認"""
    def _callFUT(self, *args, **kwds):
        from ..api import create_lot
        return create_lot(*args, **kwds)

    def setUp(self):
        self.session = _setup_db(modules=dependency_modules)

    def tearDown(self):
        testing.tearDown()
        _teardown_db()

    @mock.patch('altair.app.ticketing.events.sales_segments.resources.SalesSegmentAccessor.update_sales_segment')
    def test_create_lot_from_form(self, mock_update_sales_segment):
        """新規で抽選用のSalesSegmentGroupを作成するとき, Lot(+SalesSegment)も作成される
        """
        from datetime import datetime
        from altair.app.ticketing.core.models import Event, SalesSegmentGroup, SalesSegment
        from altair.app.ticketing.lots.models import Lot
        from altair.app.ticketing.events.sales_segment_groups.forms import SalesSegmentGroupAndLotForm
        mock_update_sales_segment.return_value = None
        event1 = Event(
            title=u'テストイベント'
        )
        self.session.add(event1)
        self.session.flush()
        ssg1 = SalesSegmentGroup(
            event=event1,
            kind='early_lottery'
        )
        form = testing.DummyModel(
            data=dict(
                name=u'テスト抽選',
                limit_wishes=3,
                entry_limit=1,
                description='',
                lotting_announce_datetime=datetime(2016,7,1,0,0),
                lotting_announce_timezone='night',
                custom_timezone_label='',
                auth_type='',
                lot_entry_user_withdraw=True
            )
        )

        self._callFUT(event1, form, ssg1)

        lot = self.session.query(Lot).filter(Lot.name == u'テスト抽選').first()
        ss = self.session.query(SalesSegment).filter(SalesSegment.event_id == event1.id).first()
        self.assertTrue(lot)
        self.assertIs(ss, lot.sales_segment)

    # TODO:SalesSegmentGroupを渡さない場合
    # def test_create_without_ssg(self):


class CreatingLotsProductTest(TestCase):
    def _callFUT(self, *args, **kwds):
        from ..api import create_lot_products
        return create_lot_products(*args, **kwds)

    def setUp(self):
        self.session = _setup_db(modules=dependency_modules)

    def tearDown(self):
        testing.tearDown()
        _teardown_db()

    def _setup_test_data(self):
        from datetime import datetime
        from altair.app.ticketing.core.models import Event, SalesSegmentGroup, SalesSegment, Performance, Product
        from altair.app.ticketing.lots.models import Lot
        event = Event(
            title=u'テストイベント'
        )
        self.session.add(event)
        self.ssg = SalesSegmentGroup(
            event=event,
            name=u'先行抽選',
            kind='early_lottery'
        )
        self.session.add(self.ssg)
        self.lot = Lot(name=u'抽選１')
        lot_ss = SalesSegment(
            sales_segment_group=self.ssg
        )
        self.session.add(lot_ss)
        lot_ss.lots.append(self.lot)
        ss1 = SalesSegment(
            sales_segment_group=self.ssg,
            performance=Performance(
                name=u'公演１',
                start_on=datetime(2016, 7, 1)
            )
        )
        self.session.add(ss1)
        ss1.products.append(Product(name=u'商品１', price=100))
        ss2 = SalesSegment(
            sales_segment_group=self.ssg,
            performance=Performance(
                name=u'公演２',
                start_on=datetime(2016, 7, 2)
            )
        )
        self.session.add(ss2)
        ss2.products.append(Product(name=u'商品２', price=200))
        ss3 = SalesSegment(
            sales_segment_group=self.ssg,
            performance=Performance(
                name=u'公演３',
                start_on=datetime(2016, 7, 3)
            )
        )
        self.session.add(ss3)
        ss3.products.append(Product(name=u'商品３', price=300))
        self.session.flush()

    def test_create_lot_products(self):
        """販売区分グループ配下にある商品を、抽選の商品としてコピーする"""
        self._setup_test_data()

        self._callFUT(self.ssg, self.lot)

        for p in self.lot.sales_segment.products:
            self.assertIn(p.name, [u'商品１', u'商品２', u'商品３'])

    def test_excluding_performance(self):
        """指定した公演を含む商品は追加されない"""
        from altair.app.ticketing.core.models import Performance
        self._setup_test_data()
        exclude_performances = []
        performance2 = self.session.query(Performance).filter(Performance.name == u'公演２').first()
        exclude_performances.append(performance2.id)

        self._callFUT(self.ssg, self.lot, exclude_performances)

        copied_product_names = [p.name for p in self.lot.sales_segment.products]
        self.assertIn(u'商品１', copied_product_names)
        self.assertNotIn(u'商品２', copied_product_names)
        self.assertIn(u'商品３', copied_product_names)


class CopyingLotsWhenSSGCopyTest(TestCase):
    """コンテキスト：販売区分グループコピー時の抽選コピー"""
    def _callFUT(self, *args, **kwds):
        from ..api import copy_lots_between_sales_segmnent_group
        return copy_lots_between_sales_segmnent_group(*args, **kwds)

    def setUp(self):
        self.session = _setup_db(modules=dependency_modules)

    def tearDown(self):
        testing.tearDown()
        _teardown_db()

    def _setup_test_data(self):
        from altair.app.ticketing.core.models import Event, SalesSegmentGroup, SalesSegment, Product, Performance
        from altair.app.ticketing.lots.models import Lot
        event = Event(title=u'テストイベント')
        self.session.add(event)
        self.ssg1 = SalesSegmentGroup(
            name=u'先行抽選',
            kind='early_lottery',
            event=event,
            sales_segments=[
                SalesSegment(
                    lots=[Lot(name=u'抽選１')],
                    products=[
                        Product(name=u'抽選商品１', price=100, original_product_id=3),
                        Product(name=u'抽選商品２', price=200, original_product_id=4)
                    ]
                ),
                SalesSegment(
                    performance=Performance(name=u'公演１'),
                    products=[
                        Product(name=u'商品１', price=100, original_product_id=None),
                        Product(name=u'商品２', price=200, original_product_id=None)
                    ]
                )
            ]
        )
        self.ssg2 = SalesSegmentGroup(
            name=u'コピー先行抽選',
            kind='early_lottery',
            event=event,
            sales_segments=[
                SalesSegment(
                    performance=Performance(name=u'コピー公演１'),
                    products=[
                        Product(name=u'コピー商品１', price=100, original_product_id=None),
                        Product(name=u'コピー商品２', price=200, original_product_id=None)
                    ]
                )
            ]
        )
        self.session.add(self.ssg1)
        self.session.add(self.ssg2)
        self.session.flush()

    @mock.patch('altair.app.ticketing.events.sales_segments.resources.SalesSegmentAccessor.update_sales_segment')
    def test_copy_lots_between_sales_segmnent_group(self, mock_update_sales_segment):
        """販売区分グループ配下の抽選(+販売区分)を別の販売区分グループにコピーする
        (公演に紐づく販売区分と商品は、このメソッド実行前に作成されている前提)
        """
        mock_update_sales_segment.return_value = None
        self._setup_test_data()

        self._callFUT(self.ssg1, self.ssg2)

        ssg2_lots = self.ssg2.get_lots()
        self.assertTrue(ssg2_lots)
        self.assertTrue(ssg2_lots[0].sales_segment)
        self.assertTrue(ssg2_lots[0].sales_segment.products)
        self.assertEqual(ssg2_lots[0].sales_segment.products[0].name, u'コピー商品１')


class CopyingLotProductsTests(TestCase):
    """抽選商品を公演商品から作成する"""
    def _callFUT(self, *args, **kwds):
        from ..api import copy_lot_products_from_performance
        return copy_lot_products_from_performance(*args, **kwds)

    def setUp(self):
        self.session = _setup_db(modules=dependency_modules)

    def tearDown(self):
        testing.tearDown()
        _teardown_db()

    def _setup_test_data(self):
        from altair.app.ticketing.core.models import Performance, SalesSegmentGroup, SalesSegment, Product
        from altair.app.ticketing.lots.models import Lot
        lottery_ssg = SalesSegmentGroup(
            name=u'先行抽選',
            kind='early_lottery'
        )
        normal_ssg = SalesSegmentGroup(
            name=u'一般発売',
            kind='normal'
        )
        self.lot1 = Lot(
            name=u'抽選１',
            sales_segment=SalesSegment(
                sales_segment_group=lottery_ssg,
                products=[]
            )
        )
        self.lot2 = Lot(
            name=u'抽選２',
            sales_segment=SalesSegment(
                sales_segment_group=lottery_ssg,
                products=[]
            )
        )
        self.performance1 = Performance(
            name=u'公演１',
            sales_segments=[
                SalesSegment(
                    sales_segment_group=lottery_ssg,
                    products=[
                        Product(name=u'抽選商品１', price=100, original_product_id=None),
                        Product(name=u'抽選商品２', price=200, original_product_id=None)
                    ]
                ),
                SalesSegment(
                    sales_segment_group=normal_ssg,
                    products=[
                        Product(name=u'一般商品１', price=1000, original_product_id=None),
                        Product(name=u'一般商品２', price=2000, original_product_id=None),
                        Product(name=u'一般商品３', price=3000, original_product_id=None)
                    ]
                )
            ]
        )
        self.session.add(self.lot1)
        self.session.add(self.performance1)
        self.session.flush()

    def test_copy_lots_between_performance(self):
        """抽選商品を公演商品から作成する
        一般商品はコピーされないことも確認する"""
        self._setup_test_data()

        self._callFUT(self.performance1, self.lot1)

        self.assertEqual(len(self.lot1.sales_segment.products), 2)

    def test_not_copy_to_other_lots(self):
        """コピー対象としていない抽選には商品がコピーされない"""
        self._setup_test_data()

        self._callFUT(self.performance1, self.lot1)

        self.assertEqual(len(self.lot2.sales_segment.products), 0)
