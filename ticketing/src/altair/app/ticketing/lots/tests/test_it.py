# -*- coding:utf-8 -*-

import unittest
import mock
from pyramid import testing
from altair.app.ticketing.testing import _setup_db, _teardown_db, DummyRequest
from ..testing import DummyAuthenticatedResource

dependency_modules = [
    'altair.app.ticketing.orders.models',
    'altair.app.ticketing.core.models',
    'altair.app.ticketing.users.models',
    'altair.app.ticketing.mailmags.models',
    'altair.app.ticketing.cart.models',
    'altair.app.ticketing.lots.models',
]

testing_settings = {
    'makotxt.default_filters': 'unicode',
    'mako.directories': ['altair.app.ticketing.lots:templates'],
    'altair.sej.template_file': '',
    'altair.nogizaka46_auth.key': '',
}


class keep_authTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.session = _setup_db(modules=dependency_modules, echo=False)
        cls.config = testing.setUp(settings=testing_settings)
        from pyramid.authorization import ACLAuthorizationPolicy
        cls.config.set_authorization_policy(ACLAuthorizationPolicy())
        cls.config.include('altair.auth')
        cls.config.include('pyramid_layout')

    @classmethod
    def tearDownClass(cls):
        testing.tearDown()
        _teardown_db()

    @mock.patch('altair.multicheckout.api.Multicheckout3DAPI.save_api_response')
    @mock.patch('altair.multicheckout.api.get_multicheckout_impl')
    def test_it(self, mock_service_factory, mock_save_api_response):
        from altair.multicheckout.testing import DummyCheckout3D
        from altair.multicheckout.api import get_multicheckout_3d_api
        mock_service_factory.return_value = DummyCheckout3D()

        request = DummyRequest()
        multicheckout_api = get_multicheckout_3d_api(request)
        order_no = 'test_order_no'

        result = multicheckout_api.checkout_sales(order_no)

        self.assertEqual(result.OrderNo, order_no)
        mock_save_api_response.assert_called_with(result, None)


class EntryLotViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from altair.sqlahelper import register_sessionmaker_with_engine
        cls.session = _setup_db(modules=dependency_modules, echo=False)
        cls.config = testing.setUp(settings=testing_settings)
        register_sessionmaker_with_engine(
            cls.config.registry,
            'slave',
            cls.session.bind
            )
        from pyramid.authorization import ACLAuthorizationPolicy
        cls.config.set_authorization_policy(ACLAuthorizationPolicy())
        cls._get_organization_patch = mock.patch('altair.app.ticketing.cart.request.get_organization')
        cls._get_organization = cls._get_organization_patch.start()
        cls._get_organization.return_value = testing.DummyResource(id=1)
        cls.config.include('altair.auth')
        cls.config.include('pyramid_layout')
        cls.config.include('altair.pyramid_tz')
        cls.config.include('altair.app.ticketing.cart.request')


    @classmethod
    def tearDownClass(cls):
        cls._get_organization_patch.stop()
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
        from altair.app.ticketing.core.models import Organization
        from altair.app.ticketing.users.models import Membership, MemberGroup
        from ..testing import _add_lots, login

        organization = Organization(code='XX', short_name='example')
        membergroup = MemberGroup(
            membership=Membership(organization=organization, name='test-membership'),
            name='test-group'
            )
        self.session.add(membergroup)
        login(self.config, {"auth_type": "fc_auth", "username": "test", "membership": "test-membership", "membergroup": "test-group"})
        #event = testing.DummyModel(id=1111)
        #sales_segment = testing.DummyModel(id=12345)
        #lot = _add_lot(self.session, event.id, sales_segment.id, 5, 3, membergroups=[membergroup])
        lot, products = _add_lots(self.session, organization, [], membergroups=[membergroup])
        event = lot.event

        request = DummyRequest(
            matchdict=dict(event_id=1111, lot_id=lot.id),
        )

        context = DummyAuthenticatedResource(
            request=request,
            event=event, lot=lot,
            user={'auth_identifier': 'test', 'is_guest': True, 'organization_id': 1, 'membership': "test-membership", 'membergroup': "test-group"},
            membershipinfo=membergroup.membership,
            cart_setting=testing.DummyModel(
                extra_form_fields=[],
                flavors=None,
                ),
            )
        target = self._makeOne(context, request)
        result = target.get()

        self.assertEqual(result['lot'].id, lot.id)

    def _add_datas(self, product_data):
        from altair.app.ticketing.core.models import Organization
        from altair.app.ticketing.users.models import Membership, MemberGroup
        from ..testing import _add_lots, login

        organization = Organization(code='XX', short_name='example')
        membergroup = MemberGroup(
            membership=Membership(organization=organization, name='test-membership'),
            name='test-group'
            )
        self.session.add(membergroup)
        login(self.config, {"username": "test", "membership": "test-membership", "membergroup": "test-group"})

        lot, products = _add_lots(self.session, organization, product_data, [membergroup])
        return lot, products

    def test_post(self):
        from altair.app.ticketing.payments.interfaces import IPaymentDeliveryPlugin
        self.config.add_route('lots.entry.confirm', '/lots/events/{event_id}/entry/{lot_id}/confirm')
        lot, products = self._add_datas([
            {'name': u'商品 A', 'price': 100},
            {'name': u'商品 B', 'price': 100},
            {'name': u'商品 C', 'price': 100},
        ])
        lot.sales_segment.max_quantity = 100

        sales_segment = lot.sales_segment
        payment_delivery_method_pair = pdmp = sales_segment.payment_delivery_method_pairs[0]
        preparer_name = "payment-%s:delivery-%s" % (pdmp.payment_method.payment_plugin_id,
                                                    pdmp.delivery_method.delivery_plugin_id,)
        class DummyPaymentDeliveryPlugin(object):
            def __init__(self):
                self.called = []

            def prepare(self, *args, **kwargs):
                self.called.append(('prepare', args, kwargs))

        self.config.registry.registerUtility(DummyPaymentDeliveryPlugin(),
                                             IPaymentDeliveryPlugin,
                                             name=preparer_name)
        performances = lot.performances

        data = self._params(**{
            "first_name": u'あ',
            "first_name_kana": u'イ',
            "last_name": u'う',
            "last_name_kana": u'エ',
            "tel_1": u"01234567899",
            "fax": u"01234567899",
            "zip": u'1234567',
            "prefecture": u'東京都',
            "city": u'渋谷区',
            "address_1": u"代々木１丁目",
            "address_2": u"森京ビル",
            "email_1": u"test@example.com",
            "email_1_confirm": u"test@example.com",
            "email_2": u"test2@example.com",
            "email_2_confirm": u"test2@example.com",
            "sex": '1',
            "birthday.year": '1980',
            "birthday.month": '05',
            "birthday.day": '03',
            "payment_delivery_method_pair_id": str(payment_delivery_method_pair.id),

            "performanceDate-1": str(products[0].performance_id),
            "performanceDate-2": str(products[1].performance_id),
            "product-id-1-1" : str(products[0].id),
            "product-quantity-1-1" : "10",
            "product-id-1-2" : str(products[1].id),
            "product-quantity-1-2" : "5",
            "product-id-2-1" : str(products[2].id),
            "product-quantity-2-1" : "5",
            })

        request = DummyRequest(
            matchdict=dict(event_id=lot.event_id, lot_id=lot.id),
            params=data,
        )
        context = testing.DummyResource(
            request=request,
            event=lot.event, lot=lot,
            organization=lot.event.organization,
            check_entry_limit=lambda wishes, user, email: True,
            authenticated_user=lambda:{'auth_identifier':None, 'is_guest':True, 'organization_id': 1, 'membership': "test-membership"},
            cart_setting=testing.DummyModel(
                extra_form_fields=[],
                flavors=None,
                ),
            )
        request.context = context
        target = self._makeOne(context, request)

        result = target.post()
        for s in request.session.pop_flash():
            print s

        self.assertEqual(result.location, "http://example.com/lots/events/1111/entry/1/confirm")
        self.assertIsNotNone(request.session['lots.entry']['token'])
        self.assertEqual(len(request.session['lots.entry']['token']), 32)
        self.assertEqual(request.session['lots.entry']['shipping_address'],
            {'address_1': u'代々木１丁目',
             'address_2': u'森京ビル',
             'city': u'渋谷区',
             'country': u'日本国',
             'email_1': u'test@example.com',
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
    def _add_datas(self, product_data):
        from ...core.models import Organization, Host
        from ...users.models import Membership, MemberGroup
        from ..testing import _add_lots, login

        organization = Organization(name='test', short_name='test')
        host = Host(organization=organization, host_name='example.com:80')
        membership = Membership(organization=organization, name='test-membership')
        membergroup = MemberGroup(name='test-group', membership=membership)
        self.session.add(organization)
        self.session.add(host)
        self.session.add(membership)
        self.session.add(membergroup)
        login(self.config, {"username": "test", "membership": "test-membership", "membergroup": "test-group"})

        lot, products = _add_lots(self.session, organization, product_data, [membergroup])
        return lot, products

    def setUp(self):
        from altair.sqlahelper import register_sessionmaker_with_engine
        self.session = _setup_db(modules=dependency_modules, echo=False)
        self.config = testing.setUp(settings=testing_settings)
        register_sessionmaker_with_engine(
            self.config.registry,
            'slave',
            self.session.bind
            )
        from pyramid.authorization import ACLAuthorizationPolicy
        self.config.set_authorization_policy(ACLAuthorizationPolicy())
        self._get_organization_patch = mock.patch('altair.app.ticketing.cart.request.get_organization')
        self._get_organization = self._get_organization_patch.start()
        self._get_organization.return_value = testing.DummyResource()
        self._get_altair_auth_info_patch = mock.patch('altair.app.ticketing.cart.request.get_altair_auth_info')
        self._get_altair_auth_info = self._get_altair_auth_info_patch.start()
        self._get_altair_auth_info.return_value = dict(
            organization_id=1
            )
        self.config.include('altair.auth')
        self.config.include('pyramid_layout')
        self.config.include('altair.app.ticketing.lots.setup_routes')
        self.config.include('altair.app.ticketing.cart.request')

    def tearDown(self):
        self._get_organization_patch.stop()
        self._get_altair_auth_info.stop()
        import transaction
        self.session.remove()
        transaction.abort()
        testing.tearDown()
        _teardown_db()

    def _getTarget(self):
        from .. import views
        return views.ConfirmLotEntryView

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_get(self):
        from datetime import datetime
        lot, products = self._add_datas([
            {'name': u'商品 A', 'price': 100},
            {'name': u'商品 B', 'price': 100},
            {'name': u'商品 C', 'price': 100},
        ])
        organization = lot.event.organization
        sales_segment = lot.sales_segment
        payment_delivery_method_pair = sales_segment.payment_delivery_method_pairs[0]
        performances = lot.performances

        request = DummyRequest(
            host='example.com:80',
            session={'lots.entry':
                {
                    'shipping_address':
                        {'address_1': u'代々木１丁目',
                         'address_2': u'森京ビル',
                         'city': u'渋谷区',
                         'country': u'日本国',
                         'email_1': u'test@example.com',
                         'fax': u'01234567899',
                         'first_name': u'あ',
                         'first_name_kana': u'イ',
                         'last_name': u'う',
                         'last_name_kana': u'エ',
                         'prefecture': u'東京都',
                         'tel_1': u'01234567899',
                         'tel_2': None,
                         'zip': u'1234567'}, #shipping_address

                    'wishes': [{"performance_id": str(performances[0].id),
                                "wished_products": [
                                    {"wish_order": 1, "product_id": '1', "quantity": 10},
                                    {"wish_order": 1, "product_id": '2', "quantity": 5}]},
                               {"performance_id": str(performances[1].id),
                                "wished_products": [
                                    {"wish_order": 2, "product_id": '3', "quantity": 5}]}],
                    'payment_delivery_method_pair_id': str(payment_delivery_method_pair.id),
                    'token': 'this-is-session-token',
                    'gender': u"1",
                    'birthday': datetime.now(),
                    'memo': u"",
                }, #lots.entry
            }, #session
        )
        context = testing.DummyResource(event=testing.DummyModel(),
                                        lot=lot,
                                        organization=organization,
                                        extra_form_fields=[],
                                        cart_setting=testing.DummyModel(
                                            extra_form_fields=[],
                                            flavors=None,
                                            ),
                                        )

        target = self._makeOne(context, request)

        result = target.get()

        self.assertEqual(result['shipping_address'],
                        {'address_1': u'代々木１丁目',
                         'address_2': u'森京ビル',
                         'city': u'渋谷区',
                         'country': u'日本国',
                         'email_1': u'test@example.com',
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
        request = DummyRequest(
            host='example.com:80',
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
        request = DummyRequest(
            host='example.com:80',
            )
        request.session['lots.entry'] = {}
        context = testing.DummyResource()

        target = self._makeOne(context, request)

        result = target.post()
        self.assertEqual(result.location, 'http://example.com/back/to/form')

    def test_post(self):
        #from altair.app.ticketing import txt_renderer_factory
        from datetime import datetime
        from altair.app.ticketing.payments.testing import DummyPreparer
        from altair.app.ticketing.payments.directives import add_payment_plugin

        lot, products = self._add_datas([
            {'name': u'商品 A', 'price': 100},
            {'name': u'商品 B', 'price': 100},
            {'name': u'商品 C', 'price': 100},
        ])
        self.session.flush()
        self.config.add_route('lots.entry.index', '/back/to/form')
        #self.config.add_renderer('.txt' , txt_renderer_factory)
        sales_segment = lot.sales_segment
        payment_delivery_method_pair = sales_segment.payment_delivery_method_pairs[0]
        plugin_id = payment_delivery_method_pair.payment_method.payment_plugin_id = 100
        add_payment_plugin(self.config, DummyPreparer(None), plugin_id)

        event_id = lot.event_id
        shipping_address_dict = {
            'address_1': u'代々木１丁目',
            'address_2': u'森京ビル',
            'city': u'渋谷区',
            'country': u'日本国',
            'email_1': u'test@example.com',
            'email_1_confirm': u'test@example.com',
            'email_2': u'test@example.com',
            'email_2_confirm': u'test@example.com',
            'fax': u'01234567899',
            'first_name': u'あ',
            'first_name_kana': u'イ',
            'last_name': u'う',
            'last_name_kana': u'エ',
            'prefecture': u'東京都',
            'tel_1': u'01234567899',
            'tel_2': None,
            'zip': u'1234567'
            }
        request = DummyRequest(
            host='example.com:80',
            session={
                'lots.entry.time': datetime.now(),
                'lots.entry':
                {
                    'entry_no': 'testing-entry-no',
                    'shipping_address': shipping_address_dict,
                    'wishes': [{"performance_id": "123",
                                "wished_products": [
                                    {"wish_order": 1, "product_id": products[0].id, "quantity": 10},
                                    {"wish_order": 1, "product_id": products[1].id, "quantity": 5}]},
                               {"performance_id": "124",
                                "wished_products": [
                                    {"wish_order": 2, "product_id": products[2].id, "quantity": 5}]}],
                    'token': 'test-token', # token
                    'payment_delivery_method_pair_id': payment_delivery_method_pair.id,
                    'gender': u"1",
                    'birthday': datetime.now(),
                    'memo': u"",
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
        request.registry.settings['lots.accepted_mail_template'] = 'altair.app.ticketing:templates/lots_accept_entry.txt'
        context = DummyAuthenticatedResource(
            user={ 'auth_identifier': None, 'is_guest': True, 'organization_id': 1, 'membership': 'test' },
            membershipinfo=testing.DummyResource(enable_point_input=False)
            )
        context.lot = lot
        context.event = lot.event
        request.context = context

        target = self._makeOne(context, request)

        result = target.post()

        entry_no = request.session['lots.entry_no']
        self._assertLotEntry(lot, entry_no, shipping_address_dict)

    def _assertLotEntry(self, lot, entry_no, shipping_address_dict):
        self.assertEqual(len(lot.entries), 1)
        lot_entry = lot.entries[0]
        self.assertEqual(lot_entry.entry_no, entry_no)
        self._assert_shipping_address(lot_entry.shipping_address, shipping_address_dict)

    def _assert_shipping_address(self, actual, expected):
        from .. import helpers
        names = [n for n in helpers.SHIPPING_ATTRS if n not in ['nick_name', 'sex']]
        for name in names:
            self.assertEqual(getattr(actual, name), expected[name])

class LotReviewViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from altair.sqlahelper import register_sessionmaker_with_engine
        cls.session = _setup_db(modules=dependency_modules, echo=False)
        cls.config = testing.setUp(settings=testing_settings)
        register_sessionmaker_with_engine(
            cls.config.registry,
            'slave',
            cls.session.bind
            )
        from pyramid.authorization import ACLAuthorizationPolicy
        cls.config.set_authorization_policy(ACLAuthorizationPolicy())
        cls._get_organization_patch = mock.patch('altair.app.ticketing.cart.request.get_organization')
        cls._get_organization = cls._get_organization_patch.start()
        cls._get_organization.return_value = testing.DummyResource(id=1)
        cls.config.include('altair.auth')
        cls.config.include('pyramid_layout')
        cls.config.include('altair.app.ticketing.cart.request')


    @classmethod
    def tearDownClass(cls):
        cls._get_organization_patch.stop()
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
        request = DummyRequest()
        context = testing.DummyResource()
        target = self._makeOne(context, request)
        result = target.get()

        self.assertTrue(isinstance(result['form'], schemas.ShowLotEntryForm))

    def _params(self, **kw):
        from webob.multidict import MultiDict
        return MultiDict(kw)

    def test_post_invalid(self):
        from .. import schemas

        request = DummyRequest(
            params=self._params(),
        )
        context = testing.DummyResource()

        target = self._makeOne(context, request)

        result = target.post()

        self.assertTrue(isinstance(result['form'], schemas.ShowLotEntryForm))

    def test_post_with_elected(self):
        from datetime import datetime
        self.config.add_route('lots.payment.index', '/lots/events/{event_id}/payment/{lot_id}')
        from altair.app.ticketing.core.models import ShippingAddress, DBSession, Event
        from altair.app.ticketing.lots.models import LotEntry, Lot

        entry_no = u'LOTtest000001'
        tel_no = '0123456789'
        shipping_address = ShippingAddress(tel_1=tel_no)
        event = Event()
        lot = Lot(event=event)
        entry = LotEntry(entry_no=entry_no, lot=lot, shipping_address=shipping_address, elected_at=datetime.now())
        DBSession.add(entry)
        DBSession.flush()

        request = DummyRequest(
            params=self._params(
                entry_no=entry_no,
                tel_no=tel_no,
            ),
        )
        context = testing.DummyResource()

        target = self._makeOne(context, request)

        result = target.post()

        ## fuckin' my_render_view_to_response!
        #self.assertIsNotNone(result)
        #self.assertIn('entry', result)
        #self.assertEqual(result['payment_url'], 'http://example.com/lots/events/1/payment/1')
        #self.assertIn('lots.entry_id', request.session)

    def test_post_without_elected(self):
        from datetime import datetime
        self.config.add_route('lots.payment', '/lots/payment')
        from altair.app.ticketing.core.models import ShippingAddress, DBSession, Event
        from altair.app.ticketing.lots.models import LotEntry, Lot
        entry_no = u'LOTtest000001'
        tel_no = '0123456789'
        shipping_address = ShippingAddress(tel_1=tel_no)
        event = Event()
        lot = Lot(event=event)
        entry = LotEntry(entry_no=entry_no, lot=lot, shipping_address=shipping_address)
        DBSession.add(entry)
        DBSession.flush()

        request = DummyRequest(
            params=self._params(
                entry_no=entry_no,
                tel_no=tel_no,
            ),
        )
        context = testing.DummyResource()

        target = self._makeOne(context, request)

        result = target.post()
        ## get out my_render_view_to_response!
        # self.assertIsNotNone(result)
        # self.assertIn('entry', result)
        # self.assertEqual(result['entry'], entry)
        # self.assertIsNone(result['payment_url'])
        # self.assertIn('lots.entry_id', request.session)


# class PaymentViewTests(unittest.TestCase):
#     @classmethod
#     def setUpClass(cls):
#         cls.config = testing.setUp(settings=testing_settings)
#         cls.config.include('pyramid_layout')
#         cls.config.include('altair.app.ticketing.lots')
#         cls.session = _setup_db(modules=dependency_modules, echo=False)

#     @classmethod
#     def tearDownClass(cls):
#         testing.tearDown()
#         _teardown_db()

#     def setUp(self):
#         self.session.remove()

#     def tearDown(self):
#         import transaction
#         transaction.abort()

#     def _getTarget(self):
#         from .. import views
#         return views.PaymentView

#     def _makeOne(self, *args, **kwargs):
#         return self._getTarget()(*args, **kwargs)

#     def test_no_entry(self):
#         from pyramid.httpexceptions import HTTPNotFound
#         request = testing.DummyRequest(
#             matchdict={"event_id": None},
#         )
#         context = testing.DummyResource()
#         context.lot = None
#         target = self._makeOne(context, request)

#         self.assertRaises(HTTPNotFound, target.submit)

#     def _add_entry(self, entry_id):
#         from ..models import LotEntry
#         entry = LotEntry(id=entry_id)
#         self.session.add(entry)
#         self.session.flush()
#         return entry

#     def test_not_elected(self):
#         from ..exceptions import NotElectedException
#         request = testing.DummyRequest(
#             matchdict={"event_id": None},
#         )
#         context = testing.DummyResource()
#         entry_id = 999999
#         entry = self._add_entry(entry_id)
#         context.lot = entry.lot
#         request.session['lots.entry_id'] = entry_id
#         target = self._makeOne(context, request)

#         self.assertRaises(NotElectedException, target.submit)
