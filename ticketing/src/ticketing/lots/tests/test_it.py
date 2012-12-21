# -*- coding:utf-8 -*-

import unittest
from pyramid import testing
from ticketing.testing import _setup_db, _teardown_db

dependency_modules = [
    'ticketing.core.models',
    'ticketing.users.models',
    'ticketing.cart.models',
    'ticketing.lots.models',
]


class EntryLotViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = testing.setUp()
        cls.config.registry.settings['mako.directories'] = ['ticketing.lots:templates']
        cls.config.include('pyramid_layout')
        cls.config.include('ticketing.lots')
        cls.session = _setup_db(modules=dependency_modules, echo=False)


    @classmethod
    def tearDownClass(cls):
        testing.tearDown()
        _teardown_db()

    def setUp(self):
        self.session.remove()

    def tearDown(self):
        import transaction
        transaction.abort()

    def _getTarget(self):
        from .. import views
        return views.EntryLotView

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)


    def test_get(self):
        from ...users.models import MemberGroup
        from ..testing import _add_lot, login
        
        membergroup = MemberGroup(name='test-group')
        self.session.add(membergroup)
        login(self.config, {'membergroup': 'test-group'})
        
        event = testing.DummyModel(id=1111)
        sales_segment = testing.DummyModel(id=12345)
        lot = _add_lot(self.session, event.id, sales_segment.id, 5, 3, membergroups=[membergroup])

        request = testing.DummyRequest(
            matchdict=dict(event_id=1111, lot_id=lot.id),
        )
        target = self._makeOne(request)        
        result = target.get()

        self.assertEqual(result['lot'].id, lot.id)

    def _add_datas(self, product_data):
        from ...users.models import MemberGroup
        from ..testing import _add_lots, login

        membergroup = MemberGroup(name='test-group')
        self.session.add(membergroup)
        login(self.config, {'membergroup': 'test-group'})
        
        lot, products = _add_lots(self.session, product_data, [membergroup])
        return lot, products

    def test_post(self):
        self.config.add_route('lots.entry.confirm', '/lots/events/{event_id}/entry/{lot_id}/confirm')
        lot, products = self._add_datas([
            {'name': u'商品 A', 'price': 100},
            {'name': u'商品 B', 'price': 100},
            {'name': u'商品 C', 'price': 100},
        ])

        sales_segment = lot.sales_segment
        payment_delivery_method_pair = sales_segment.payment_delivery_method_pairs[0]
        performances = lot.performances

        wishes = {
            "performance-1": str(performances[0].id),
            "performance-2": str(performances[1].id),
            "product-id-1-1" : str(products[0].id),
            "product-quantity-1-1" : "10",
            "product-id-1-2" : str(products[1].id),
            "product-quantity-1-2" : "5",
            "product-id-2-1" : str(products[2].id),
            "product-quantity-2-1" : "5",
        }

        data = self._params(
            first_name=u'あ',
            first_name_kana=u'イ',
            last_name=u'う',
            last_name_kana=u'エ',
            tel=u"01234567899",
            fax=u"01234567899",
            zip=u'1234567',
            prefecture=u'東京都',
            city=u'渋谷区',
            address_1=u"代々木１丁目",
            address_2=u"森京ビル",
            mail_address=u"test@example.com",
            mail_address2=u"test@example.com",
            sex='1',
            payment_delivery_method_pair_id=str(payment_delivery_method_pair.id),
            **wishes
        )
        request = testing.DummyRequest(
            matchdict=dict(event_id=lot.event_id, lot_id=lot.id),
            params=data,
        )
        target = self._makeOne(request)        
        result = target.post()
        if isinstance(result, dict):
            print result['form'].errors

        self.assertEqual(result.location, "http://example.com/lots/events/1111/entry/1/confirm")
        self.assertIsNotNone(request.session['lots.entry']['token'])
        self.assertEqual(len(request.session['lots.entry']['token']), 32)
        self.assertEqual(request.session['lots.entry']['wishes'],  
            [{"performance_id": str(performances[0].id), 
              "wished_products": [
                  {"wish_order": 1, "product_id": '1', "quantity": 10}, 
                  {"wish_order": 1, "product_id": '2', "quantity": 5}]}, 
             {"performance_id": str(performances[1].id), 
              "wished_products": [
                  {"wish_order": 2, "product_id": '3', "quantity": 5}]}] )
        self.assertEqual(request.session['lots.entry']['shipping_address'],  
            {'address_1': u'代々木１丁目',
             'address_2': u'森京ビル',
             'city': u'渋谷区',
             'country': u'日本国',
             'email': u'test@example.com',
             'fax': u'01234567899',
             'first_name': u'あ',
             'first_name_kana': u'イ',
             'last_name': u'う',
             'last_name_kana': u'エ',
             'prefecture': u'東京都',
             'tel_1': u'01234567899',
             'tel_2': u'',
             'sex': u'1',
             'zip': u'1234567'})

    def _params(self, **kwargs):
        from webob.multidict import MultiDict
        return MultiDict(kwargs)

class ConfirmLotEntryViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = testing.setUp()
        cls.config.registry.settings['mako.directories'] = ['ticketing.lots:templates']
        cls.config.include('pyramid_layout')
        cls.config.include('ticketing.lots')
        cls.session = _setup_db(modules=dependency_modules, echo=False)

    def _add_datas(self, product_data):
        from ...users.models import MemberGroup
        from ..testing import _add_lots, login

        membergroup = MemberGroup(name='test-group')
        self.session.add(membergroup)
        login(self.config, {'membergroup': 'test-group'})
        
        lot, products = _add_lots(self.session, product_data, [membergroup])
        return lot, products

    @classmethod
    def tearDownClass(cls):
        testing.tearDown()
        _teardown_db()

    def setUp(self):
        self.session.remove()

    def tearDown(self):
        import transaction
        transaction.abort()

    def _getTarget(self):
        from .. import views
        return views.ConfirmLotEntryView

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_get(self):
        lot, products = self._add_datas([
            {'name': u'商品 A', 'price': 100},
            {'name': u'商品 B', 'price': 100},
            {'name': u'商品 C', 'price': 100},
        ])
        sales_segment = lot.sales_segment
        payment_delivery_method_pair = sales_segment.payment_delivery_method_pairs[0]
        product1 = products[0]
        product2 = products[1]
        product3 = products[2]
        performances = lot.performances
        performance1 = performances[0]
        performance2 = performances[1]
        performance_id1 = str(performance1.id)
        performance_id2 = str(performance2.id)

        request = testing.DummyRequest(
            session={'lots.entry': 
                {
                    'shipping_address': 
                        {'address_1': u'代々木１丁目',
                         'address_2': u'森京ビル',
                         'city': u'渋谷区',
                         'country': u'日本国',
                         'email': u'test@example.com',
                         'fax': u'01234567899',
                         'first_name': u'あ',
                         'first_name_kana': u'イ',
                         'last_name': u'う',
                         'last_name_kana': u'エ',
                         'prefecture': u'東京都',
                         'tel_1': u'01234567899',
                         'tel_2': None,
                         'zip': u'1234567'}, #shipping_address
                    #'wishes': [[(1, '1', 10, performance_id1), (1, '2', 5, performance_id1)], [(2, '3', 5, performance_id2)]], # wishes
                    'wishes': [{"performance_id": str(performances[0].id), 
                                "wished_products": [
                                    {"wish_order": 1, "product_id": '1', "quantity": 10}, 
                                    {"wish_order": 1, "product_id": '2', "quantity": 5}]}, 
                               {"performance_id": str(performances[1].id), 
                                "wished_products": [
                                    {"wish_order": 2, "product_id": '3', "quantity": 5}]}],
                    'payment_delivery_method_pair_id': str(payment_delivery_method_pair.id),
                    'token': 'this-is-session-token',
                }, #lots.entry
            }, #session
        )
        context = testing.DummyResource()

        target = self._makeOne(context, request)

        result = target.get()

        self.assertEqual(result['wishes'],
            [[{'wish_order': 1, 'product': product1, "quantity": 10, "performance": performance1}, 
              {'wish_order': 1, 'product': product2, "quantity": 5, "performance": performance1}], 
             [{'wish_order': 2, 'product': product3, "quantity": 5, "performance": performance2}]] )
        self.assertEqual(result['shipping_address'],
                        {'address_1': u'代々木１丁目',
                         'address_2': u'森京ビル',
                         'city': u'渋谷区',
                         'country': u'日本国',
                         'email': u'test@example.com',
                         'fax': u'01234567899',
                         'first_name': u'あ',
                         'first_name_kana': u'イ',
                         'last_name': u'う',
                         'last_name_kana': u'エ',
                         'prefecture': u'東京都',
                         'tel_1': u'01234567899',
                         'tel_2': None,
                         'zip': u'1234567'}, #shipping_address
        ) 
        self.assertEqual(result['token'], 'this-is-session-token')

    def test_post_back(self):
        self.config.add_route('lots.entry.index', '/back/to/form')
        request = testing.DummyRequest(
            session={'lots.entry': {'token': 'test-token'}},
            params={'back': 'Back', 
                    'token': 'test-token'},
        )
        context = testing.DummyResource()

        target = self._makeOne(context, request)

        result = target.post()
        self.assertEqual(result.location, 'http://example.com/back/to/form')

    def test_post_without_token(self):
        self.config.add_route('lots.entry.index', '/back/to/form')
        request = testing.DummyRequest(
        )
        request.session['lots.entry'] = {}
        context = testing.DummyResource()

        target = self._makeOne(context, request)

        result = target.post()
        self.assertEqual(result.location, 'http://example.com/back/to/form')

    def test_post(self):
        lot, products = self._add_datas([
            {'name': u'商品 A', 'price': 100},
            {'name': u'商品 B', 'price': 100},
            {'name': u'商品 C', 'price': 100},
        ])
        self.config.add_route('lots.entry.index', '/back/to/form')
        self.config.add_renderer('.txt' , 'pyramid.mako_templating.renderer_factory')
        sales_segment = lot.sales_segment
        payment_delivery_method_pair = sales_segment.payment_delivery_method_pairs[0]
        event_id = lot.event_id
        request = testing.DummyRequest(
            session={'lots.entry': 
                {
                    'shipping_address': 
                        {'address_1': u'代々木１丁目',
                         'address_2': u'森京ビル',
                         'city': u'渋谷区',
                         'country': u'日本国',
                         'email': u'test@example.com',
                         'fax': u'01234567899',
                         'first_name': u'あ',
                         'first_name_kana': u'イ',
                         'last_name': u'う',
                         'last_name_kana': u'エ',
                         'prefecture': u'東京都',
                         'tel_1': u'01234567899',
                         'tel_2': None,
                         'zip': u'1234567'}, #shipping_address
                    'wishes': [{"performance_id": "123", 
                                "wished_products": [
                                    {"wish_order": 1, "product_id": '1', "quantity": 10}, 
                                    {"wish_order": 1, "product_id": '2', "quantity": 5}]}, 
                               {"performance_id": "124", 
                                "wished_products": [
                                    {"wish_order": 2, "product_id": '3', "quantity": 5}]}],
                    'token': 'test-token', # token
                    'payment_delivery_method_pair_id': payment_delivery_method_pair.id,
                }, #lots.entry
            }, # session
            params={'token': 'test-token'},
            matchdict=dict(
                event_id=event_id,
                lot_id=lot.id,
            )
        )
        request.registry.settings['lots.accepted_mail_subject'] = '抽選テスト'
        request.registry.settings['lots.accepted_mail_sender'] = 'testing@sender.example.com'
        request.registry.settings['lots.accepted_mail_template'] = 'ticketing.lots:mail_templates/accept_entry.txt'
        context = testing.DummyResource()

        target = self._makeOne(context, request)

        result = target.post()

        self._assertLotEntry(lot, request.session['lots.entry']['shipping_address'])

    def _assertLotEntry(self, lot, shipping_address):
        self.assertEqual(len(lot.entries), 1)
        lot_entry = lot.entries[0]
        self._assert_shipping_address(lot_entry.shipping_address, shipping_address)

    def _assert_shipping_address(self, actual, expected):
        from .. import helpers
        names = [n for n in helpers.SHIPPING_ATTRS if n not in ['nick_name', 'sex']]
        for name in names:
            self.assertEqual(getattr(actual, name), expected[name])
        
class LotReviewViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = testing.setUp()
        cls.config.registry.settings['mako.directories'] = ['ticketing.lots:templates']
        cls.config.include('pyramid_layout')
        cls.config.include('ticketing.lots')
        cls.session = _setup_db(modules=dependency_modules, echo=False)


    @classmethod
    def tearDownClass(cls):
        testing.tearDown()
        _teardown_db()

    def setUp(self):
        self.session.remove()

    def tearDown(self):
        import transaction
        transaction.abort()

    def _getTarget(self):
        from .. import views
        return views.LotReviewView

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_get(self):
        from .. import schemas
        request = testing.DummyRequest()
        context = testing.DummyResource()
        target = self._makeOne(context, request)
        result = target.get()

        self.assertTrue(isinstance(result['form'], schemas.ShowLotEntryForm))

    def _params(self, **kw):
        from webob.multidict import MultiDict
        return MultiDict(kw)

    def test_post_invalid(self):
        from .. import schemas

        request = testing.DummyRequest(
            params=self._params(),
        )
        context = testing.DummyResource()

        target = self._makeOne(context, request)

        result = target.post()

        self.assertTrue(isinstance(result['form'], schemas.ShowLotEntryForm))

    def test_post_with_elected(self):
        from datetime import datetime
        self.config.add_route('lots.payment.index', '/lots/events/{event_id}/payment/{lot_id}')
        from ticketing.core.models import ShippingAddress, DBSession, Event
        from ticketing.lots.models import LotEntry, Lot
        request = testing.DummyRequest()
        entry_no = u'LOTtest000001'
        tel_no = '0123456789'
        shipping_address = ShippingAddress(tel_1=tel_no)
        event = Event()
        lot = Lot(event=event)
        entry = LotEntry(entry_no=entry_no, lot=lot, shipping_address=shipping_address, elected_at=datetime.now())
        DBSession.add(entry)
        DBSession.flush()

        request = testing.DummyRequest(
            params=self._params(
                entry_no=entry_no,
                tel_no=tel_no,
            ),
        )
        context = testing.DummyResource()

        target = self._makeOne(context, request)

        result = target.post()
        self.assertIn('entry', result)
        self.assertEqual(result['payment_url'], 'http://example.com/lots/events/1/payment/1')
        self.assertIn('lots.entry_id', request.session)

    def test_post_without_elected(self):
        from datetime import datetime
        self.config.add_route('lots.payment', '/lots/payment')
        from ticketing.core.models import ShippingAddress, DBSession, Event
        from ticketing.lots.models import LotEntry, Lot
        request = testing.DummyRequest()
        entry_no = u'LOTtest000001'
        tel_no = '0123456789'
        shipping_address = ShippingAddress(tel_1=tel_no)
        event = Event()
        lot = Lot(event=event)
        entry = LotEntry(entry_no=entry_no, lot=lot, shipping_address=shipping_address)
        DBSession.add(entry)
        DBSession.flush()

        request = testing.DummyRequest(
            params=self._params(
                entry_no=entry_no,
                tel_no=tel_no,
            ),
        )
        context = testing.DummyResource()

        target = self._makeOne(context, request)

        result = target.post()
        self.assertIn('entry', result)
        self.assertEqual(result['entry'], entry)
        self.assertIsNone(result['payment_url'])
        self.assertIn('lots.entry_id', request.session)


class PaymentViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = testing.setUp()
        cls.config.registry.settings['mako.directories'] = ['ticketing.lots:templates']
        cls.config.include('pyramid_layout')
        cls.config.include('ticketing.lots')
        cls.session = _setup_db(modules=dependency_modules, echo=False)
    
    @classmethod
    def tearDownClass(cls):
        testing.tearDown()
        _teardown_db()

    def setUp(self):
        self.session.remove()

    def tearDown(self):
        import transaction
        transaction.abort()

    def _getTarget(self):
        from .. import views
        return views.PaymentView

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_no_entry(self):
        from pyramid.httpexceptions import HTTPNotFound
        request = testing.DummyRequest(
            matchdict={"event_id": None},
        )
        target = self._makeOne(request)

        self.assertRaises(HTTPNotFound, target.submit)

    def _add_entry(self, entry_id):
        from ..models import LotEntry
        entry = LotEntry(id=entry_id)
        self.session.add(entry)
        self.session.flush()
        return entry

    def _add_entry_elected(self, entry_id):
        from datetime import datetime
        from ticketing.core.models import (
            PaymentDeliveryMethodPair,
            PaymentMethod,
            DeliveryMethod,
            Performance,
            Event,
            Organization,
        )
        from ..models import LotEntry, LotElectedEntry, LotEntryWish, Lot
        lot = Lot()
        performance = Performance(event=Event(organization=Organization(short_name="testing", code="TEST")))
        entry = LotEntry(id=entry_id, elected_at=datetime.now(), lot=lot,
            payment_delivery_method_pair=PaymentDeliveryMethodPair(system_fee=999, 
                transaction_fee=100, delivery_fee=234, discount=0,
                payment_method=PaymentMethod(fee=11),
                delivery_method=DeliveryMethod(fee=22)))
        elected = LotElectedEntry(lot_entry=entry,
            lot_entry_wish=LotEntryWish(performance=performance))

        self.session.add(entry)
        self.session.flush()

        return entry


    def test_not_elected(self):
        from ..exceptions import NotElectedException
        request = testing.DummyRequest(
            matchdict={"event_id": None},
        )
        entry_id = 999999
        entry = self._add_entry(entry_id)
        request.session['lots.entry_id'] = entry_id
        target = self._makeOne(request)

        self.assertRaises(NotElectedException, target.submit)

    def test_elected(self):
        from ..exceptions import NotElectedException
        from ticketing.payments.interfaces import IPaymentDeliveryPlugin
        from ticketing.cart.models import Cart

        reg = self.config.registry
        dummy_preparer = DummyPreperer()
        reg.utilities.register([], IPaymentDeliveryPlugin,
            "payment-None:delivery-None", 
            dummy_preparer,
            )
        request = testing.DummyRequest(
            matchdict={"event_id": None},
        )
        entry_id = 999999
        entry = self._add_entry_elected(entry_id)
        request.session['lots.entry_id'] = entry_id
        target = self._makeOne(request)

        result = target.submit()

        self.assertIn('ticketing.cart_id', request.session)
        cart_id = request.session['ticketing.cart_id']
        cart = Cart.query.filter(Cart.id==cart_id).one()
        self.assertIsNotNone(cart.tickets_amount)
        self.assertIsNotNone(cart.transaction_fee)
        self.assertEqual(dummy_preparer.called,
            [('prepare', request, cart)])

class DummyPreperer(object):
    def __init__(self):
        self.called = []

    def prepare(self, request, cart):
        self.called.append(("prepare", request, cart))
